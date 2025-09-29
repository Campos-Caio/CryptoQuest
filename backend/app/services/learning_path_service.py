import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.models.learning_path import LearningPath, UserPathProgress, LearningPathResponse
from app.models.mission import QuizSubmision
from app.repositories.learning_path_repository import LearningPathRepository
from app.core.firebase import get_firestore_db_async

logger = logging.getLogger(__name__)

class LearningPathService:
    """Service para lógica de negócio das trilhas de aprendizado"""
    
    def __init__(self):
        self.repository = LearningPathRepository()
    
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
    
    async def complete_mission(self, user_id: str, path_id: str, mission_id: str, score: int) -> Dict[str, Any]:
        """Conclui uma missão e atualiza o progresso"""
        try:
            logger.info(f"Concluindo missão {mission_id} para usuário {user_id} na trilha {path_id}")
            
            # Busca a trilha para validar a missão
            path = self.repository.get_learning_path_by_id(path_id)
            if not path:
                raise ValueError(f"Trilha {path_id} não encontrada")
            
            # Valida se a missão existe na trilha
            mission_exists = False
            mission_module = None
            for module in path.modules:
                for mission in module.missions:
                    if mission.id == mission_id:
                        mission_exists = True
                        mission_module = module
                        break
                if mission_exists:
                    break
            
            if not mission_exists:
                raise ValueError(f"Missão {mission_id} não encontrada na trilha {path_id}")
            
            # Verifica se a pontuação é suficiente
            required_score = mission_module.missions[0].required_score if mission_module.missions else 70
            if score < required_score:
                raise ValueError(f"Pontuação {score} insuficiente. Mínimo necessário: {required_score}")
            
            # Atualiza o progresso
            progress = await self.repository.complete_mission(user_id, path_id, mission_id, score)
            
            # Verifica se o módulo foi concluído
            module_completed = await self._check_module_completion(progress, mission_module)
            
            # Verifica se a trilha foi concluída
            path_completed = await self._check_path_completion(progress, path)
            
            result = {
                "progress": progress,
                "module_completed": module_completed,
                "path_completed": path_completed,
                "next_module": await self._get_next_module(path, progress) if not path_completed else None
            }
            
            logger.info(f"Missão {mission_id} concluída com sucesso para usuário {user_id}")
            return result
            
        except Exception as e:
            logger.error(f"Erro no service ao concluir missão: {e}")
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
    
    async def _check_module_completion(self, progress: UserPathProgress, module) -> bool:
        """Verifica se um módulo foi concluído"""
        try:
            module_missions = [mission.id for mission in module.missions]
            completed_module_missions = [mid for mid in progress.completed_missions if mid in module_missions]
            
            if len(completed_module_missions) == len(module_missions):
                # Módulo concluído
                if module.id not in progress.completed_modules:
                    await self.repository.complete_module(progress.user_id, progress.path_id, module.id)
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
                progress.completed_at = datetime.utcnow()
                progress.progress_percentage = 100.0
                self.repository.update_progress(progress)
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
            if success:
                points_earned = int(score / 10) * 10  # 10 pontos por 10% de acerto
            
            logger.info(f"Missão completada: score={score:.1f}%, success={success}, points={points_earned}")
            
            return {
                "score": int(score),
                "success": success,
                "points": points_earned,
                "correct_answers": correct_answers,
                "total_questions": total_questions,
                "required_score": mission.required_score
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
                    started_at=datetime.utcnow(),
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
                if len(progress.completed_missions) >= total_missions:
                    progress.completed_at = datetime.utcnow()
            
            # Salvar progresso
            self.repository.update_progress(progress)
            
        except Exception as e:
            logger.error(f"Erro ao atualizar progresso do usuário: {e}")
            raise
