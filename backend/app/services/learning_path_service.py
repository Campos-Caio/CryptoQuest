import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, UTC
from app.models.learning_path import LearningPath, UserPathProgress, LearningPathResponse
from app.models.mission import QuizSubmision, EnhancedQuizSubmission
from app.repositories.learning_path_repository import LearningPathRepository
from app.core.firebase import get_firestore_db_async
from app.services.reward_service import RewardService
from app.services.event_bus import get_event_bus
from app.models.events import LearningPathCompletedEvent, QuizCompletedEvent
from app.core.logging_config import get_cryptoquest_logger

# 🆕 Imports para IA - ATIVADOS
from app.ai.services.ml_engine import get_ml_engine
from app.ai.services.recommendation_engine import get_recommendation_engine
from app.ai.data.behavioral_data_collector import get_behavioral_collector

logger = logging.getLogger(__name__)
cryptoquest_logger = get_cryptoquest_logger()

class LearningPathService:
    """Service para lógica de negócio das trilhas de aprendizado"""
    
    def __init__(self, reward_service: RewardService = None):
        self.repository = LearningPathRepository()
        self.reward_service = reward_service
        self.event_bus = get_event_bus()
        
        # 🆕 Inicializar serviços de IA - ATIVADOS
        self.ml_engine = get_ml_engine()
        self.recommendation_engine = get_recommendation_engine()
        self.behavioral_collector = get_behavioral_collector()
    
    # ==================== OPERAÇÕES DE TRILHAS ====================
    
    async def get_all_learning_paths(self) -> List[LearningPath]:
        """Busca todas as trilhas ativas"""
        try:
            logger.info("Buscando todas as trilhas ativas")
            paths = self.repository.get_all_learning_paths()
            
            # Ordena por data de criação (mais recentes primeiro)
            paths.sort(key=lambda x: x.created_at, reverse=True)
            
            logger.info(f"Retornando {len(paths)} trilhas ativas")
            return paths
            
        except Exception as e:
            logger.error(f"Erro no service ao buscar trilhas: {e}")
            raise
    
    async def get_learning_path_by_id(self, path_id: str) -> Optional[LearningPath]:
        """Busca uma trilha específica por ID"""
        try:
            logger.info(f"Buscando trilha: {path_id}")
            path = self.repository.get_learning_path_by_id(path_id)
            
            if not path:
                logger.warning(f"Trilha {path_id} não encontrada")
                return None
            
            logger.info(f"Trilha {path_id} encontrada: {path.name}")
            return path
            
        except Exception as e:
            logger.error(f"Erro no service ao buscar trilha {path_id}: {e}")
            raise
    
    # ==================== OPERAÇÕES DE PROGRESSO ====================
    
    async def get_user_path_details(self, user_id: str, path_id: str) -> Optional[LearningPathResponse]:
        """Busca detalhes completos de uma trilha com progresso do usuário"""
        try:
            logger.info(f"Buscando detalhes da trilha {path_id} para usuário {user_id}")
            
            # Busca a trilha
            path = self.repository.get_learning_path_by_id(path_id)
            if not path:
                logger.warning(f"Trilha {path_id} não encontrada")
                return None
            
            logger.info(f"Trilha encontrada: {path.name}")
            logger.info(f"Módulos: {len(path.modules)}")
            
            # Busca o progresso do usuário
            progress = self.repository.get_user_progress(user_id, path_id)
            logger.info(f"Progresso encontrado: {progress is not None}")
            if progress:
                logger.info(f"Progresso encontrado para usuário {user_id}")
            
            # Calcula estatísticas
            stats = await self._calculate_path_stats(path, progress)
            logger.info(f"Estatísticas calculadas: {stats}")
            
            response = LearningPathResponse(
                path=path,
                progress=progress,
                stats=stats
            )
            
            logger.info(f"Detalhes da trilha {path_id} preparados para usuário {user_id}")
            return response
            
        except Exception as e:
            logger.error(f"Erro no service ao buscar detalhes da trilha: {e}")
            logger.error(f"Tipo do erro: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
    
    async def start_learning_path(self, user_id: str, path_id: str) -> UserPathProgress:
        """Inicia uma trilha para o usuário"""
        try:
            logger.info(f"Iniciando trilha {path_id} para usuário {user_id}")
            
            # Verifica se a trilha existe
            path = self.repository.get_learning_path_by_id(path_id)
            if not path:
                raise ValueError(f"Trilha {path_id} não encontrada")
            
            if not path.is_active:
                raise ValueError(f"Trilha {path_id} não está ativa")
            
            # Inicia a trilha
            progress = self.repository.start_learning_path(user_id, path_id)
            
            # Define o primeiro módulo como atual
            if path.modules:
                first_module = min(path.modules, key=lambda x: x.order)
                progress.current_module_id = first_module.id
                self.repository.update_progress(progress)
            
            logger.info(f"Trilha {path_id} iniciada com sucesso para usuário {user_id}")
            return progress
            
        except Exception as e:
            logger.error(f"Erro no service ao iniciar trilha: {e}")
            raise
    
    
    # ==================== MÉTODOS AUXILIARES ====================
    
    async def _calculate_path_stats(self, path: LearningPath, progress: Optional[UserPathProgress]) -> Dict[str, Any]:
        """Calcula estatísticas da trilha"""
        try:
            total_modules = len(path.modules)
            total_missions = sum(len(module.missions) for module in path.modules)
            
            if progress:
                completed_modules = len(progress.completed_modules)
                completed_missions = len(progress.completed_missions)
                progress_percentage = (completed_missions / total_missions * 100) if total_missions > 0 else 0
                
                # Atualiza o progresso se necessário
                if progress.progress_percentage != progress_percentage:
                    progress.progress_percentage = progress_percentage
                    self.repository.update_progress(progress)
            else:
                completed_modules = 0
                completed_missions = 0
                progress_percentage = 0
            
            return {
                "total_modules": total_modules,
                "total_missions": total_missions,
                "completed_modules": completed_modules,
                "completed_missions": completed_missions,
                "progress_percentage": round(progress_percentage, 2),
                "is_started": progress is not None,
                "is_completed": progress.completed_at is not None if progress else False
            }
            
        except Exception as e:
            logger.error(f"Erro ao calcular estatísticas: {e}")
            return {}
    
    async def _check_and_persist_module_completion(self, progress: UserPathProgress, learning_path) -> None:
        """Verifica e persiste conclusão de módulos de forma robusta"""
        try:
            modules_completed = []
            
            for module in learning_path.modules:
                # Obter missões do módulo
                module_missions = [mission.id for mission in module.missions]
                
                # Verificar quais missões do módulo foram concluídas
                completed_module_missions = [mid for mid in progress.completed_missions if mid in module_missions]
                
                # Verificar se módulo foi concluído
                is_module_completed = len(completed_module_missions) == len(module_missions)
                
                if is_module_completed and module.id not in progress.completed_modules:
                    progress.completed_modules.append(module.id)
                    modules_completed.append(module.id)
                    
                    # Persistir imediatamente no banco
                    self.repository.complete_module(progress.user_id, progress.path_id, module.id)
            
            if modules_completed:
                logger.info(f"Módulos concluídos: {modules_completed}")
                
                # Emitir eventos de módulo completado
                for module_id in modules_completed:
                    try:
                        # Encontrar o módulo para obter o nome
                        module = next((m for m in learning_path.modules if m.id == module_id), None)
                        if module:
                            from app.models.events import ModuleCompletedEvent
                            module_event = ModuleCompletedEvent(
                                user_id=progress.user_id,
                                learning_path_id=progress.path_id,
                                module_id=module_id,
                                module_name=module.name
                            )
                            await self.event_bus.emit(module_event)
                            logger.info(f"Evento de módulo completado emitido: {module_id}")
                    except Exception as e:
                        logger.error(f"Erro ao emitir evento de módulo {module_id}: {e}")
                
        except Exception as e:
            logger.error(f"Erro ao verificar conclusão de módulos: {e}")
            raise

    async def _verify_progress_integrity(self, progress: UserPathProgress, learning_path) -> None:
        """Verifica a integridade dos dados de progresso"""
        try:
            # Recarregar progresso do banco para verificar se foi salvo
            saved_progress = self.repository.get_user_progress(progress.user_id, progress.path_id)
            
            if saved_progress:
                # Verificar se os dados estão consistentes
                if len(saved_progress.completed_modules) != len(progress.completed_modules):
                    logger.warning(f"Inconsistência detectada no progresso do usuário {progress.user_id}")
                    # Forçar atualização
                    self.repository.update_progress(progress)
            else:
                logger.error(f"Progresso não encontrado no banco para usuário {progress.user_id}")
                
        except Exception as e:
            logger.error(f"Erro ao verificar integridade: {e}")

    async def _check_module_completion(self, progress: UserPathProgress, module) -> bool:
        """Verifica se um módulo foi concluído"""
        try:
            module_missions = [mission.id for mission in module.missions]
            completed_module_missions = [mid for mid in progress.completed_missions if mid in module_missions]
            
            if len(completed_module_missions) == len(module_missions):
                # Módulo concluído
                if module.id not in progress.completed_modules:
                    self.repository.complete_module(progress.user_id, progress.path_id, module.id)
                    progress.completed_modules.append(module.id)
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Erro ao verificar conclusão do módulo: {e}")
            return False
    
    async def _check_path_completion(self, progress: UserPathProgress, path: LearningPath) -> bool:
        """Verifica se a trilha foi concluída"""
        try:
            if progress.completed_at:
                return True
            
            total_missions = sum(len(module.missions) for module in path.modules)
            if len(progress.completed_missions) >= total_missions:
                # Trilha concluída
                progress.completed_at = datetime.now(UTC)
                progress.progress_percentage = 100.0
                self.repository.update_progress(progress)
                
                # Log de evento de negócio - trilha completada
                cryptoquest_logger.log_business_event(
                    "learning_path_completed",
                    {
                        "user_id": progress.user_id,
                        "path_id": progress.path_id,
                        "total_missions": total_missions,
                        "completed_missions": len(progress.completed_missions),
                        "completion_time": progress.completed_at.isoformat()
                    }
                )
                
                # Log de ação do usuário
                cryptoquest_logger.log_user_action(
                    progress.user_id,
                    "learning_path_completed",
                    {
                        "path_id": progress.path_id,
                        "total_missions": total_missions,
                        "completion_percentage": 100.0
                    }
                )
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Erro ao verificar conclusão da trilha: {e}")
            return False
    
    async def _get_next_module(self, path: LearningPath, progress: UserPathProgress) -> Optional[Dict[str, Any]]:
        """Retorna o próximo módulo a ser executado"""
        try:
            if not progress.current_module_id:
                # Se não há módulo atual, retorna o primeiro
                if path.modules:
                    first_module = min(path.modules, key=lambda x: x.order)
                    return {
                        "id": first_module.id,
                        "name": first_module.name,
                        "order": first_module.order
                    }
                return None
            
            # Busca o próximo módulo não concluído
            current_module_order = None
            for module in path.modules:
                if module.id == progress.current_module_id:
                    current_module_order = module.order
                    break
            
            if current_module_order is None:
                return None
            
            # Busca o próximo módulo
            next_module = None
            for module in path.modules:
                if module.order > current_module_order and module.id not in progress.completed_modules:
                    if next_module is None or module.order < next_module.order:
                        next_module = module
            
            if next_module:
                return {
                    "id": next_module.id,
                    "name": next_module.name,
                    "order": next_module.order
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar próximo módulo: {e}")
            return None
    
   
    async def complete_mission_with_ai(
        self, 
        user_id: str, 
        path_id: str, 
        mission_id: str, 
        submission: EnhancedQuizSubmission
    ) -> Dict[str, Any]:
        """
        Completa uma missão com dados comportamentais enriquecidos para análise de IA.
        
        Args:
            user_id: ID do usuário
            path_id: ID da trilha
            mission_id: ID da missão
            submission: Respostas enriquecidas do quiz
            
        Returns:
            Dict com resultado da missão e insights de IA
        """
        try:
            logger.info(f"Completando missão {mission_id} com IA para usuário {user_id}")
            
            # 1. 🆕 Coletar dados comportamentais - ATIVADO
            behavioral_data = await self.behavioral_collector.collect_quiz_data(
                user_id=user_id,
                quiz_id=mission_id,
                submission=submission
            )
            
            # 2. Executar lógica original de completar missão
            result = await self.complete_mission(
                user_id=user_id,
                path_id=path_id,
                mission_id=mission_id,
                submission=QuizSubmision(answers=submission.answers)
            )
            
            # 3. 🆕 Análise de IA
            ai_insights = await self._generate_ai_insights(
                user_id=user_id,
                mission_id=mission_id,
                behavioral_data=behavioral_data,
                result=result
            )
            
            # 4. 🆕 Adicionar insights de IA ao resultado
            result.update({
                "ai_insights": ai_insights,
                "behavioral_data_collected": True,
                "session_id": behavioral_data.session_id
            })
            
            cryptoquest_logger.log_business_event(
                "mission_completed_with_ai",
                context={
                    "user_id": user_id,
                    "mission_id": mission_id,
                    "ai_insights_generated": len(ai_insights),
                    "behavioral_data_session": behavioral_data.session_id
                }
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao completar missão com IA: {e}")
            # Fallback para método original
            return await self.complete_mission(
                user_id=user_id,
                path_id=path_id,
                mission_id=mission_id,
                submission=QuizSubmision(answers=submission.answers)
            )
    
    async def _generate_ai_insights(
        self, 
        user_id: str, 
        mission_id: str, 
        behavioral_data, 
        result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Gera insights de IA baseados nos dados comportamentais"""
        try:
            insights = {
                "learning_pattern": None,
                "recommendations": [],
                "difficulty_suggestion": None,
                "performance_summary": {}
            }
            
            # 1. Análise de padrões de aprendizado - ATIVADO
            quiz_history = await self.behavioral_collector.get_user_behavioral_history(user_id, limit=10)
            if quiz_history:
                pattern = await self.ml_engine.analyze_user_patterns(user_id, quiz_history)
                insights["learning_pattern"] = {
                    "type": pattern.pattern_type,
                    "strength": pattern.strength,
                    "context": pattern.context
                }
            
            # 2. Gerar recomendações - ATIVADO
            recommendations = await self.recommendation_engine.get_recommendations(user_id, limit=3)
            insights["recommendations"] = [
                {
                    "content_id": rec.content_id,
                    "type": rec.content_type,
                    "relevance_score": rec.relevance_score,
                    "reasoning": rec.reasoning
                }
                for rec in recommendations
            ]
            
            # 3. Sugestão de dificuldade - ATIVADO
            performance_metrics = behavioral_data.performance_metrics
            difficulty_prediction = self.ml_engine.difficulty_predictor.predict_optimal_difficulty({
                "user_level": 2,  # Seria buscado do perfil do usuário
                "domain_proficiency": performance_metrics.get("avg_confidence", 0.5),
                "avg_response_time": performance_metrics.get("avg_response_time", 30),
                "confidence_level": performance_metrics.get("avg_confidence", 0.5)
            })
            
            insights["difficulty_suggestion"] = {
                "optimal_difficulty": difficulty_prediction.value,
                "confidence": difficulty_prediction.confidence,
                "reasoning": difficulty_prediction.reasoning
            }
            
            # 4. Resumo de performance - ATIVADO
            insights["performance_summary"] = {
                "engagement_score": performance_metrics.get("engagement_score", 0.0),
                "response_consistency": performance_metrics.get("response_time_consistency", 0.0),
                "learning_efficiency": performance_metrics.get("avg_confidence", 0.0) * 
                                     (1.0 - performance_metrics.get("retry_rate", 0.0))
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"Erro ao gerar insights de IA: {e}")
            return {"error": str(e)}
    
    # ==================== COMPLETAR MISSÃO ====================
    
    async def complete_mission(
        self, 
        user_id: str, 
        path_id: str, 
        mission_id: str, 
        submission: QuizSubmision
    ) -> Dict[str, Any]:
        """
        Completa uma missão de uma trilha de aprendizado.
        
        Args:
            user_id: ID do usuário
            path_id: ID da trilha
            mission_id: ID da missão
            submission: Respostas do quiz
            
        Returns:
            Dict com resultado da missão
        """
        try:
            logger.info(f"Completando missão {mission_id} da trilha {path_id} para usuário {user_id}")
            
            # Buscar a trilha
            learning_path = self.repository.get_learning_path_by_id(path_id)
            if not learning_path:
                raise ValueError(f"Trilha {path_id} não encontrada")
            
            # Encontrar a missão na trilha
            mission = None
            for module in learning_path.modules:
                for m in module.missions:
                    if m.id == mission_id:
                        mission = m
                        break
                if mission:
                    break
            
            if not mission:
                raise ValueError(f"Missão {mission_id} não encontrada na trilha {path_id}")
            
            # Buscar o quiz
            db = await get_firestore_db_async()
            quiz_doc = await db.collection("quizzes").document(mission.mission_id).get()
            
            if not quiz_doc.exists:
                raise ValueError(f"Quiz {mission.mission_id} não encontrado")
            
            quiz_data = quiz_doc.to_dict()
            
            # Calcular pontuação
            correct_answers = 0
            total_questions = len(quiz_data.get("questions", []))
            
            for i, question in enumerate(quiz_data.get("questions", [])):
                if i < len(submission.answers):
                    if submission.answers[i] == question.get("correct_answer_index", -1):
                        correct_answers += 1
            
            score = (correct_answers / total_questions * 100) if total_questions > 0 else 0
            success = score >= mission.required_score
            
            # Atualizar progresso do usuário
            await self._update_user_progress(
                user_id=user_id,
                path_id=path_id,
                mission_id=mission_id,
                score=score,
                success=success
            )
            
            # Calcular pontos baseados na pontuação
            points_earned = 0
            xp_earned = 0
            if success:
                points_earned = int(score / 10) * 10  # 10 pontos por 10% de acerto
                xp_earned = int(score / 5) * 5  # 5 XP por 5% de acerto
            
            logger.info(f"Missão completada: score={score:.1f}%, success={success}, points={points_earned}, xp={xp_earned}")
            
            # Log de evento de negócio
            cryptoquest_logger.log_business_event(
                "learning_path_mission_completed",
                {
                    "user_id": user_id,
                    "path_id": path_id,
                    "mission_id": mission_id,
                    "score": score,
                    "success": success,
                    "correct_answers": correct_answers,
                    "total_questions": total_questions,
                    "required_score": mission.required_score
                }
            )
            
            # Log de ação do usuário
            cryptoquest_logger.log_user_action(
                user_id,
                "learning_path_mission_attempted",
                {
                    "path_id": path_id,
                    "mission_id": mission_id,
                    "score": score,
                    "success": success,
                    "time_taken": submission.time_taken if hasattr(submission, 'time_taken') else None
                }
            )
            
            # Integrar com sistema de recompensas se disponível
            reward_result = {}
            if self.reward_service and success:
                try:
                    reward_result = await self.reward_service.award_mission_completion(
                        user_id=user_id,
                        mission_id=mission_id,
                        score=score,
                        mission_type='learning_path'
                    )
                    logger.info(f"Recompensas concedidas: {reward_result}")
                except Exception as e:
                    logger.error(f"Erro ao conceder recompensas: {e}")
            
            # Emitir evento de quiz completado
            if success:
                try:
                    quiz_event = QuizCompletedEvent(
                        user_id=user_id,
                        quiz_id=mission.mission_id,
                        score=score,
                        learning_path_id=path_id,
                        mission_id=mission_id
                    )
                    await self.event_bus.emit(quiz_event)
                    logger.info(f"Evento de quiz completado emitido: {mission_id}")
                except Exception as e:
                    logger.error(f"Erro ao emitir evento de quiz: {e}")
            
            # Buscar progresso atualizado após as mudanças
            updated_progress = self.repository.get_user_progress(user_id, path_id)
            
            return {
                "score": int(score),
                "success": success,
                "points": points_earned,
                "xp": xp_earned,
                "correct_answers": correct_answers,
                "total_questions": total_questions,
                "required_score": mission.required_score,
                "progress": updated_progress.model_dump() if updated_progress else None,
                "next_module_unlocked": await self._get_next_unlocked_module(path_id, user_id),
                "rewards": reward_result
            }
            
        except Exception as e:
            logger.error(f"Erro ao completar missão: {e}")
            raise
    
    async def _update_user_progress(
        self, 
        user_id: str, 
        path_id: str, 
        mission_id: str, 
        score: float, 
        success: bool
    ):
        """Atualiza o progresso do usuário na trilha"""
        try:
            # Buscar progresso atual
            progress = self.repository.get_user_progress(user_id, path_id)
            
            if not progress:
                # Criar novo progresso
                progress = UserPathProgress(
                    user_id=user_id,
                    path_id=path_id,
                    started_at=datetime.now(UTC),
                    completed_at=None,
                    current_module_id=None,
                    completed_missions=[],
                    total_score=0
                )
            
            # Atualizar missões completadas
            if success and mission_id not in progress.completed_missions:
                progress.completed_missions.append(mission_id)
            
            # Atualizar pontuação total
            if success:
                progress.total_score += int(score)
            
            # Atualizar módulo atual
            learning_path = self.repository.get_learning_path_by_id(path_id)
            if learning_path:
                # Encontrar o módulo da missão
                for module in learning_path.modules:
                    for mission in module.missions:
                        if mission.id == mission_id:
                            progress.current_module_id = module.id
                            break
                    if progress.current_module_id:
                        break
                
                # Verificar se a trilha foi completada
                total_missions = sum(len(module.missions) for module in learning_path.modules)
                if len(progress.completed_missions) >= total_missions and not progress.completed_at:
                    progress.completed_at = datetime.now(UTC)
                    progress.progress_percentage = 100.0
                    
                    # Emitir evento de trilha completada
                    try:
                        learning_path_event = LearningPathCompletedEvent(
                            user_id=progress.user_id,
                            learning_path_id=progress.path_id,
                            learning_path_name=learning_path.name,
                            total_missions=total_missions,
                            completed_missions=len(progress.completed_missions)
                        )
                        await self.event_bus.emit(learning_path_event)
                        logger.info(f"Evento de trilha completada emitido: {progress.path_id}")
                    except Exception as e:
                        logger.error(f"Erro ao emitir evento de trilha completada: {e}")
            
            # Verificar e persistir conclusão de módulos
            if learning_path:
                await self._check_and_persist_module_completion(progress, learning_path)
            
            # Salvar progresso
            self.repository.update_progress(progress)
            
            # Verificar integridade dos dados
            await self._verify_progress_integrity(progress, learning_path)

            # Verificar se deve avançar para o próximo módulo
            await self._advance_to_next_module(progress, learning_path)
            
        except Exception as e:
            logger.error(f"Erro ao atualizar progresso do usuário: {e}")
            raise
    
    async def _advance_to_next_module(self, progress: UserPathProgress, learning_path: LearningPath):
        """Avança para o próximo módulo disponível"""
        try:
            # Se não há módulo atual, define o primeiro
            if not progress.current_module_id:
                if learning_path.modules:
                    first_module = min(learning_path.modules, key=lambda x: x.order)
                    progress.current_module_id = first_module.id
                    self.repository.update_progress(progress)
                return
            
            # Encontra o módulo atual
            current_module = None
            for module in learning_path.modules:
                if module.id == progress.current_module_id:
                    current_module = module
                    break
            
            if not current_module:
                return
            
            # Verifica se o módulo atual foi concluído
            module_missions = [mission.id for mission in current_module.missions]
            completed_module_missions = [mid for mid in progress.completed_missions if mid in module_missions]
            
            if len(completed_module_missions) == len(module_missions):
                # Módulo concluído, avança para o próximo
                next_module = None
                for module in learning_path.modules:
                    if module.order > current_module.order and module.id not in progress.completed_modules:
                        next_module = module
                        break
                
                if next_module:
                    progress.current_module_id = next_module.id
                    self.repository.update_progress(progress)
                    logger.info(f"Usuário {progress.user_id} avançou para módulo {next_module.id}")
        
        except Exception as e:
            logger.error(f"Erro ao avançar para próximo módulo: {e}")
    
    async def _get_next_unlocked_module(self, path_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Retorna informações sobre o próximo módulo desbloqueado"""
        try:
            progress = self.repository.get_user_progress(user_id, path_id)
            learning_path = self.repository.get_learning_path_by_id(path_id)
            
            if not progress or not learning_path:
                return None
            
            # Encontra o próximo módulo não concluído
            for module in sorted(learning_path.modules, key=lambda x: x.order):
                if module.id not in progress.completed_modules:
                    return {
                        "id": module.id,
                        "name": module.name,
                        "order": module.order,
                        "is_unlocked": True
                    }
            
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar próximo módulo: {e}")
            return None