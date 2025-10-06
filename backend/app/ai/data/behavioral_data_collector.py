"""
Coletor de dados comportamentais para análise de IA.
"""
import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, UTC
import json

from app.ai.models.ai_models import (
    UserBehavioralData, EnhancedQuizSubmission, LearningSession,
    UserKnowledgeProfile, KnowledgeDomainProfile
)
from app.ai.config import ai_config
from app.core.logging_config import get_cryptoquest_logger, LogCategory
from app.core.firebase import get_firestore_db_async

logger = logging.getLogger(__name__)
cryptoquest_logger = get_cryptoquest_logger()


class BehavioralDataCollector:
    """Coletor de dados comportamentais dos usuários"""
    
    def __init__(self):
        self.data_storage = {}  # Cache local para performance
        self.session_tracking = {}
        self.db = None  # Será inicializado quando necessário
        
        cryptoquest_logger.log_system_event("behavioral_data_collector_initialized")
    
    async def _get_db(self):
        """Inicializa conexão com Firestore se necessário"""
        if self.db is None:
            self.db = await get_firestore_db_async()
        return self.db
    
    async def collect_quiz_data(self, user_id: str, quiz_id: str, 
                               submission: EnhancedQuizSubmission) -> UserBehavioralData:
        """Coleta dados comportamentais de uma submissão de quiz"""
        try:
            # Gerar ID único para a sessão
            session_id = f"{user_id}_{quiz_id}_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}"
            
            # Calcular métricas de performance
            performance_metrics = self._calculate_performance_metrics(submission)
            
            # Criar registro de dados comportamentais
            behavioral_data = UserBehavioralData(
                user_id=user_id,
                session_id=session_id,
                quiz_id=quiz_id,
                submission_data=submission.model_dump(),  # Converter para dict
                performance_metrics=performance_metrics,
                collected_at=datetime.now(UTC)
            )
            
            # Armazenar dados
            await self._store_behavioral_data(behavioral_data)
            
            # Atualizar perfil de conhecimento
            await self._update_knowledge_profile(user_id, behavioral_data)
            
            # Log do evento
            cryptoquest_logger.log_business_event(
                "behavioral_data_collected",
                {
                    "user_id": user_id,
                    "quiz_id": quiz_id,
                    "session_id": session_id,
                    "metrics": performance_metrics
                }
            )
            
            return behavioral_data
            
        except Exception as e:
            logger.error(f"Erro ao coletar dados comportamentais: {e}")
            raise
    
    def _calculate_performance_metrics(self, submission: EnhancedQuizSubmission) -> Dict[str, Any]:
        """Calcula métricas de performance baseadas na submissão"""
        try:
            answers = submission.answers
            time_per_question = submission.time_per_question or []
            confidence_levels = submission.confidence_levels or []
            hints_used = submission.hints_used or []
            attempts_per_question = submission.attempts_per_question or []
            
            # Métricas básicas
            total_questions = len(answers)
            avg_response_time = sum(time_per_question) / len(time_per_question) if time_per_question else 0
            avg_confidence = sum(confidence_levels) / len(confidence_levels) if confidence_levels else 0.5
            total_hints_used = sum(hints_used)
            total_attempts = sum(attempts_per_question) if attempts_per_question else total_questions
            
            # Métricas derivadas
            response_time_consistency = self._calculate_consistency(time_per_question)
            confidence_variance = self._calculate_variance(confidence_levels)
            hints_usage_rate = total_hints_used / total_questions if total_questions > 0 else 0
            retry_rate = (total_attempts - total_questions) / total_questions if total_questions > 0 else 0
            
            # Score de engajamento (0-1)
            engagement_score = self._calculate_engagement_score(
                avg_confidence, hints_usage_rate, retry_rate
            )
            
            return {
                "total_questions": total_questions,
                "avg_response_time": avg_response_time,
                "avg_confidence": avg_confidence,
                "response_time_consistency": response_time_consistency,
                "confidence_variance": confidence_variance,
                "hints_usage_rate": hints_usage_rate,
                "retry_rate": retry_rate,
                "engagement_score": engagement_score,
                "total_hints_used": total_hints_used,
                "total_attempts": total_attempts
            }
            
        except Exception as e:
            logger.error(f"Erro ao calcular métricas de performance: {e}")
            return {}
    
    def _calculate_consistency(self, values: List[float]) -> float:
        """Calcula consistência de uma lista de valores"""
        if len(values) < 2:
            return 1.0
        
        mean_value = sum(values) / len(values)
        variance = sum((x - mean_value) ** 2 for x in values) / len(values)
        std_dev = variance ** 0.5
        
        # Normalizar para 0-1 (maior consistência = menor desvio padrão)
        consistency = 1.0 - min(1.0, std_dev / mean_value) if mean_value > 0 else 1.0
        return max(0.0, consistency)
    
    def _calculate_variance(self, values: List[float]) -> float:
        """Calcula variância de uma lista de valores"""
        if len(values) < 2:
            return 0.0
        
        mean_value = sum(values) / len(values)
        variance = sum((x - mean_value) ** 2 for x in values) / len(values)
        return variance
    
    def _calculate_engagement_score(self, avg_confidence: float, 
                                   hints_usage_rate: float, retry_rate: float) -> float:
        """Calcula score de engajamento (0-1)"""
        # Confiança alta = mais engajamento
        confidence_score = avg_confidence
        
        # Uso moderado de dicas = mais engajamento (não muito, não muito pouco)
        hints_score = 1.0 - abs(hints_usage_rate - 0.3) * 2  # Ideal em 0.3
        hints_score = max(0.0, hints_score)
        
        # Poucos retries = mais engajamento
        retry_score = max(0.0, 1.0 - retry_rate)
        
        # Peso das métricas
        engagement = (confidence_score * 0.5 + hints_score * 0.3 + retry_score * 0.2)
        return min(1.0, engagement)
    
    async def _store_behavioral_data(self, data: UserBehavioralData):
        """Armazena dados comportamentais no Firestore"""
        try:
            db = await self._get_db()
            
            # Estrutura organizada no Firestore
            behavioral_doc = {
                "user_id": data.user_id,
                "session_id": data.session_id,
                "quiz_id": data.quiz_id,
                "submission_data": {
                    "answers": data.submission_data.answers,
                    "time_per_question": data.submission_data.time_per_question,
                    "confidence_levels": data.submission_data.confidence_levels,
                    "hints_used": data.submission_data.hints_used,
                    "attempts_per_question": data.submission_data.attempts_per_question,
                    "session_metadata": data.submission_data.session_metadata,
                    "device_info": data.submission_data.device_info
                },
                "performance_metrics": data.performance_metrics,
                "collected_at": data.collected_at,
                "created_at": datetime.now(UTC),
                "data_version": "1.0"
            }
            
            # Salvar na coleção 'ai_behavioral_data'
            doc_ref = db.collection("ai_behavioral_data").document(data.session_id)
            await doc_ref.set(behavioral_doc)
            
            # Atualizar cache local para performance
            if data.user_id not in self.data_storage:
                self.data_storage[data.user_id] = []
            
            self.data_storage[data.user_id].append({
                "session_id": data.session_id,
                "quiz_id": data.quiz_id,
                "performance_metrics": data.performance_metrics,
                "collected_at": data.collected_at.isoformat()
            })
            
            # Limitar cache local para evitar crescimento excessivo
            if len(self.data_storage[data.user_id]) > 100:
                self.data_storage[data.user_id] = self.data_storage[data.user_id][-50:]
            
            logger.info(f"Dados comportamentais salvos no Firestore: {data.session_id}")
                
        except Exception as e:
            logger.error(f"Erro ao armazenar dados comportamentais no Firestore: {e}")
            # Fallback para cache local em caso de erro
            if data.user_id not in self.data_storage:
                self.data_storage[data.user_id] = []
            self.data_storage[data.user_id].append({
                "session_id": data.session_id,
                "quiz_id": data.quiz_id,
                "performance_metrics": data.performance_metrics,
                "collected_at": data.collected_at.isoformat()
            })
    
    async def _update_knowledge_profile(self, user_id: str, behavioral_data: UserBehavioralData):
        """Atualiza perfil de conhecimento do usuário no Firestore"""
        try:
            db = await self._get_db()
            
            metrics = behavioral_data.performance_metrics
            quiz_id = behavioral_data.quiz_id
            
            # Determinar domínio baseado no quiz_id
            domain = self._determine_domain_from_quiz(quiz_id)
            
            # Calcular proficiência baseada na performance
            proficiency = self._calculate_domain_proficiency(metrics)
            
            # Buscar perfil existente ou criar novo
            profile_ref = db.collection("ai_knowledge_profiles").document(user_id)
            profile_doc = await profile_ref.get()
            
            if profile_doc.exists:
                # Atualizar perfil existente
                profile_data = profile_doc.to_dict()
                domains = profile_data.get("domains", {})
                
                # Atualizar domínio específico
                if domain in domains:
                    # Calcular média ponderada com dados existentes
                    existing_proficiency = domains[domain].get("proficiency_level", 0.5)
                    existing_questions = domains[domain].get("total_questions", 0)
                    new_questions = metrics.get("total_questions", 1)
                    
                    # Média ponderada: (existing * existing_questions + new * new_questions) / total
                    total_questions = existing_questions + new_questions
                    new_proficiency = (existing_proficiency * existing_questions + proficiency * new_questions) / total_questions
                    
                    domains[domain].update({
                        "proficiency_level": new_proficiency,
                        "total_questions": total_questions,
                        "correct_answers": domains[domain].get("correct_answers", 0) + metrics.get("total_questions", 0),
                        "average_response_time": (domains[domain].get("average_response_time", 0) + metrics.get("avg_response_time", 0)) / 2,
                        "last_updated": datetime.now(UTC)
                    })
                else:
                    # Novo domínio
                    domains[domain] = {
                        "domain": domain,
                        "proficiency_level": proficiency,
                        "confidence": 0.7,  # Confiança inicial
                        "last_updated": datetime.now(UTC),
                        "evidence_sources": [quiz_id],
                        "total_questions": metrics.get("total_questions", 1),
                        "correct_answers": metrics.get("total_questions", 0),
                        "average_response_time": metrics.get("avg_response_time", 0),
                        "difficulty_preference": 0.5
                    }
                
                # Atualizar perfil geral
                profile_data.update({
                    "domains": domains,
                    "updated_at": datetime.now(UTC),
                    "engagement_score": (profile_data.get("engagement_score", 0) + metrics.get("engagement_score", 0)) / 2
                })
                
                await profile_ref.update(profile_data)
            else:
                # Criar novo perfil
                new_profile = {
                    "user_id": user_id,
                    "domains": {
                        domain: {
                            "domain": domain,
                            "proficiency_level": proficiency,
                            "confidence": 0.7,
                            "last_updated": datetime.now(UTC),
                            "evidence_sources": [quiz_id],
                            "total_questions": metrics.get("total_questions", 1),
                            "correct_answers": metrics.get("total_questions", 0),
                            "average_response_time": metrics.get("avg_response_time", 0),
                            "difficulty_preference": 0.5
                        }
                    },
                    "learning_style": "mixed",
                    "pace_preference": "medium",
                    "difficulty_preference": 0.5,
                    "engagement_score": metrics.get("engagement_score", 0),
                    "retention_rate": 0.0,
                    "created_at": datetime.now(UTC),
                    "updated_at": datetime.now(UTC)
                }
                
                await profile_ref.set(new_profile)
            
            cryptoquest_logger.log_business_event(
                "knowledge_profile_updated",
                {
                    "user_id": user_id,
                    "domain": domain,
                    "proficiency": proficiency,
                    "quiz_id": quiz_id
                }
            )
            
        except Exception as e:
            logger.error(f"Erro ao atualizar perfil de conhecimento: {e}")
    
    def _determine_domain_from_quiz(self, quiz_id: str) -> str:
        """Determina domínio baseado no ID do quiz"""
        # Mapeamento simples - em produção seria mais sofisticado
        if "bitcoin" in quiz_id.lower():
            return "bitcoin_basics"
        elif "blockchain" in quiz_id.lower():
            return "blockchain_technology"
        elif "defi" in quiz_id.lower():
            return "defi"
        elif "trading" in quiz_id.lower():
            return "crypto_trading"
        elif "smart" in quiz_id.lower() or "contract" in quiz_id.lower():
            return "smart_contracts"
        else:
            return "bitcoin_basics"  # Domínio padrão
    
    def _calculate_domain_proficiency(self, metrics: Dict[str, Any]) -> float:
        """Calcula proficiência no domínio baseada nas métricas"""
        try:
            engagement_score = metrics.get('engagement_score', 0.5)
            avg_confidence = metrics.get('avg_confidence', 0.5)
            retry_rate = metrics.get('retry_rate', 0)
            
            # Fórmula simples para calcular proficiência
            proficiency = (engagement_score * 0.4 + avg_confidence * 0.4 + 
                          (1.0 - retry_rate) * 0.2)
            
            return min(1.0, max(0.0, proficiency))
            
        except Exception as e:
            logger.error(f"Erro ao calcular proficiência: {e}")
            return 0.5
    
    async def get_user_behavioral_history(self, user_id: str, 
                                        limit: int = 50) -> List[Dict[str, Any]]:
        """Retorna histórico de dados comportamentais do usuário do Firestore"""
        try:
            db = await self._get_db()
            
            # Buscar dados do Firestore
            query = (db.collection("ai_behavioral_data")
                    .where("user_id", "==", user_id)
                    .order_by("collected_at", direction="DESCENDING")
                    .limit(limit))
            
            docs = await query.get()
            
            behavioral_history = []
            for doc in docs:
                data = doc.to_dict()
                behavioral_history.append({
                    "session_id": data.get("session_id"),
                    "quiz_id": data.get("quiz_id"),
                    "performance_metrics": data.get("performance_metrics", {}),
                    "collected_at": data.get("collected_at").isoformat() if data.get("collected_at") else None
                })
            
            # Atualizar cache local para performance
            self.data_storage[user_id] = behavioral_history
            
            return behavioral_history
            
        except Exception as e:
            logger.error(f"Erro ao buscar histórico comportamental do Firestore: {e}")
            # Fallback para cache local
            user_data = self.data_storage.get(user_id, [])
            return user_data[-limit:] if user_data else []
    
    async def get_user_performance_summary(self, user_id: str) -> Dict[str, Any]:
        """Retorna resumo de performance do usuário do Firestore"""
        try:
            # Buscar dados do Firestore
            behavioral_history = await self.get_user_behavioral_history(user_id, limit=100)
            
            if not behavioral_history:
                return {"status": "no_data"}
            
            # Calcular médias
            all_metrics = [item['performance_metrics'] for item in behavioral_history if item.get('performance_metrics')]
            
            if not all_metrics:
                return {"status": "no_metrics"}
            
            avg_response_time = sum(m.get('avg_response_time', 0) for m in all_metrics) / len(all_metrics)
            avg_confidence = sum(m.get('avg_confidence', 0) for m in all_metrics) / len(all_metrics)
            avg_engagement = sum(m.get('engagement_score', 0) for m in all_metrics) / len(all_metrics)
            
            # Calcular tendência
            performance_trend = "stable"
            if len(all_metrics) > 1:
                recent_engagement = all_metrics[0].get('engagement_score', 0)
                older_engagement = all_metrics[-1].get('engagement_score', 0)
                if recent_engagement > older_engagement + 0.1:
                    performance_trend = "improving"
                elif recent_engagement < older_engagement - 0.1:
                    performance_trend = "declining"
            
            return {
                "total_sessions": len(behavioral_history),
                "avg_response_time": round(avg_response_time, 2),
                "avg_confidence": round(avg_confidence, 3),
                "avg_engagement_score": round(avg_engagement, 3),
                "last_session": behavioral_history[0]['collected_at'] if behavioral_history else None,
                "performance_trend": performance_trend,
                "data_source": "firestore"
            }
            
        except Exception as e:
            logger.error(f"Erro ao calcular resumo de performance: {e}")
            return {"status": "error", "message": str(e)}
    
    async def start_learning_session(self, user_id: str, session_type: str = "quiz") -> str:
        """Inicia uma nova sessão de aprendizado e salva no Firestore"""
        try:
            session_id = f"{user_id}_{session_type}_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}"
            
            session = LearningSession(
                session_id=session_id,
                user_id=user_id,
                start_time=datetime.now(UTC)
            )
            
            # Salvar no Firestore
            db = await self._get_db()
            session_doc = {
                "session_id": session_id,
                "user_id": user_id,
                "start_time": session.start_time,
                "end_time": None,
                "quizzes_completed": [],
                "total_time_spent": 0.0,
                "average_confidence": 0.0,
                "learning_style_detected": None,
                "difficulty_adaptations": [],
                "created_at": datetime.now(UTC)
            }
            
            await db.collection("ai_learning_sessions").document(session_id).set(session_doc)
            
            # Manter no cache local para performance
            self.session_tracking[session_id] = session
            
            logger.info(f"Sessão de aprendizado iniciada: {session_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Erro ao iniciar sessão de aprendizado: {e}")
            return ""
    
    async def end_learning_session(self, session_id: str) -> Dict[str, Any]:
        """Finaliza uma sessão de aprendizado e atualiza no Firestore"""
        try:
            session = self.session_tracking.get(session_id)
            if not session:
                return {"status": "session_not_found"}
            
            session.end_time = datetime.now(UTC)
            session.total_time_spent = (session.end_time - session.start_time).total_seconds()
            
            # Calcular métricas da sessão
            session_summary = {
                "session_id": session_id,
                "user_id": session.user_id,
                "duration_seconds": session.total_time_spent,
                "quizzes_completed": len(session.quizzes_completed),
                "average_confidence": session.average_confidence,
                "learning_style_detected": session.learning_style_detected,
                "difficulty_adaptations": len(session.difficulty_adaptations)
            }
            
            # Atualizar no Firestore
            db = await self._get_db()
            session_doc = {
                "end_time": session.end_time,
                "total_time_spent": session.total_time_spent,
                "quizzes_completed": session.quizzes_completed,
                "average_confidence": session.average_confidence,
                "learning_style_detected": session.learning_style_detected,
                "difficulty_adaptations": session.difficulty_adaptations,
                "updated_at": datetime.now(UTC)
            }
            
            await db.collection("ai_learning_sessions").document(session_id).update(session_doc)
            
            # Remover da tracking ativa
            del self.session_tracking[session_id]
            
            logger.info(f"Sessão de aprendizado finalizada: {session_id}")
            return session_summary
            
        except Exception as e:
            logger.error(f"Erro ao finalizar sessão de aprendizado: {e}")
            return {"status": "error", "message": str(e)}


# Instância global do coletor de dados
_behavioral_collector_instance: Optional[BehavioralDataCollector] = None

def get_behavioral_collector() -> BehavioralDataCollector:
    """Retorna instância global do coletor de dados comportamentais"""
    global _behavioral_collector_instance
    if _behavioral_collector_instance is None:
        _behavioral_collector_instance = BehavioralDataCollector()
    return _behavioral_collector_instance
