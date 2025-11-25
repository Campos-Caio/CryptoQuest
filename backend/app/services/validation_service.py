"""
Serviço de validação para verificar condições de badges.
Implementa lógica de negócio para determinar quando badges devem ser concedidos.
"""

from typing import List, Dict, Any, Optional
from app.models.events import BaseEvent, MissionCompletedEvent, LevelUpEvent, PointsEarnedEvent, LearningPathCompletedEvent, ModuleCompletedEvent, QuizCompletedEvent
from app.models.user import UserProfile
from app.repositories.user_repository import UserRepository
from app.repositories.badge_repository import BadgeRepository
import logging

logger = logging.getLogger(__name__)


class ValidationService:
    """
    Serviço para validar condições de badges.
    
    Responsabilidades:
    - Verificar condições de badges baseadas em eventos
    - Validar elegibilidade para badges específicos
    - Calcular progresso para badges progressivos
    """
    
    def __init__(self, user_repo: UserRepository, badge_repo: BadgeRepository):
        self.user_repo = user_repo
        self.badge_repo = badge_repo

    async def check_badge_conditions(self, user_id: str, event: BaseEvent) -> List[str]:
        """
        Verifica quais badges o usuário pode ganhar baseado no evento.
        
        Args:
            user_id: ID do usuário
            event: Evento que disparou a verificação
            
        Returns:
            Lista de IDs de badges que podem ser concedidos
        """
        try:
            eligible_badges = []
            
            # Verificar badges baseados no tipo de evento
            if isinstance(event, MissionCompletedEvent):
                eligible_badges.extend(await self._check_mission_badges(user_id, event))
            elif isinstance(event, LevelUpEvent):
                eligible_badges.extend(await self._check_level_badges(user_id, event))
            elif isinstance(event, PointsEarnedEvent):
                eligible_badges.extend(await self._check_points_badges(user_id, event))
            elif isinstance(event, LearningPathCompletedEvent):
                eligible_badges.extend(await self._check_learning_path_badges(user_id, event))
            elif isinstance(event, ModuleCompletedEvent):
                eligible_badges.extend(await self._check_module_badges(user_id, event))
            elif isinstance(event, QuizCompletedEvent):
                eligible_badges.extend(await self._check_quiz_badges(user_id, event))
            
            # Verificar badges gerais
            eligible_badges.extend(await self._check_general_badges(user_id, event))
            
            logger.info(f"Badges elegíveis para usuário {user_id}: {eligible_badges}")
            return eligible_badges
            
        except Exception as e:
            logger.error(f"Erro ao verificar condições de badges para usuário {user_id}: {e}")
            return []

    async def _check_mission_badges(self, user_id: str, event: MissionCompletedEvent) -> List[str]:
        """Verifica badges relacionados a missões"""
        eligible_badges = []
        
        try:
            # Badge de primeira missão
            if self._is_first_mission(user_id):
                eligible_badges.append("first_steps")
            
            # Badge de score perfeito
            if event.score >= 100.0:
                eligible_badges.append("perfectionist")
            
            # Badge de streak (implementar lógica de streak)
            streak = self._get_current_streak(user_id)
            if streak >= 7:
                eligible_badges.append("streak_7")
            if streak >= 30:
                eligible_badges.append("streak_30")
                
        except Exception as e:
            logger.error(f"Erro ao verificar badges de missão: {e}")
        
        return eligible_badges

    async def _check_level_badges(self, user_id: str, event: LevelUpEvent) -> List[str]:
        """Verifica badges relacionados a níveis"""
        eligible_badges = []
        
        try:
            new_level = event.new_level
            
            # Badges de marcos de nível
            if new_level >= 5:
                eligible_badges.append("level_5")
            if new_level >= 10:
                eligible_badges.append("level_10")
            if new_level >= 25:
                eligible_badges.append("level_25")
            if new_level >= 50:
                eligible_badges.append("level_50")
                
        except Exception as e:
            logger.error(f"Erro ao verificar badges de nível: {e}")
        
        return eligible_badges

    async def _check_points_badges(self, user_id: str, event: PointsEarnedEvent) -> List[str]:
        """Verifica badges relacionados a pontos"""
        eligible_badges = []
        
        try:
            total_points = event.total_points
            
            # Badges de marcos de pontos
            if total_points >= 1000:
                eligible_badges.append("point_collector")
            if total_points >= 5000:
                eligible_badges.append("point_master")
            if total_points >= 10000:
                eligible_badges.append("point_legend")
                
        except Exception as e:
            logger.error(f"Erro ao verificar badges de pontos: {e}")
        
        return eligible_badges

    async def _check_general_badges(self, user_id: str, event: BaseEvent) -> List[str]:
        """Verifica badges gerais que podem ser concedidos a qualquer momento"""
        eligible_badges = []
        
        try:
            # Badge de participação (usuário ativo)
            if self._is_active_user(user_id):
                eligible_badges.append("active_participant")
                
        except Exception as e:
            logger.error(f"Erro ao verificar badges gerais: {e}")
        
        return eligible_badges

    async def _is_first_mission(self, user_id: str) -> bool:
        """Verifica se é a primeira missão do usuário"""
        try:
            user = self.user_repo.get_user_profile(user_id)
            if not user:
                return False
            
            # Verificar se já completou alguma missão
            completed_missions = user.completed_missions or {}
            return len(completed_missions) == 0
            
        except Exception as e:
            logger.error(f"Erro ao verificar primeira missão: {e}")
            return False

    async def _get_current_streak(self, user_id: str) -> int:
        """Calcula o streak atual do usuário"""
        try:
            user = self.user_repo.get_user_profile(user_id)
            if not user:
                return 0
            
            # Implementar lógica de streak baseada em daily_missions
            # Por enquanto, retorna 0 (implementar lógica real)
            return user.current_streak or 0
            
        except Exception as e:
            logger.error(f"Erro ao calcular streak: {e}")
            return 0

    async def _is_active_user(self, user_id: str) -> bool:
        """Verifica se o usuário é ativo"""
        try:
            user = self.user_repo.get_user_profile(user_id)
            if not user:
                return False
            
            # Usuário ativo se tem pontos > 0 ou completou questionário
            return user.points > 0 or user.has_completed_questionnaire
            
        except Exception as e:
            logger.error(f"Erro ao verificar usuário ativo: {e}")
            return False

    def validate_badge_eligibility(self, user_id: str, badge_id: str) -> bool:
        """
        Valida se um usuário é elegível para um badge específico.
        
        Args:
            user_id: ID do usuário
            badge_id: ID do badge
            
        Returns:
            True se elegível, False caso contrário
        """
        try:
            # Verificar se já possui o badge
            if self.badge_repo.has_badge(user_id, badge_id):
                return False
            
            # Buscar informações do badge
            badge = self.badge_repo.get_badge_by_id(badge_id)
            if not badge:
                return False
            
            # Verificar requisitos específicos do badge
            requirements = badge.requirements or {}
            req_type = requirements.get('type')
            
            if req_type == 'first_completion':
                return self._is_first_mission(user_id)
            elif req_type == 'perfect_score':
                # Verificar se tem score perfeito recente
                return self._has_recent_perfect_score(user_id)
            elif req_type == 'level':
                user = self.user_repo.get_user_profile(user_id)
                required_level = requirements.get('value', 0)
                return user and user.level >= required_level
            elif req_type == 'points':
                user = self.user_repo.get_user_profile(user_id)
                required_points = requirements.get('value', 0)
                return user and user.points >= required_points
            elif req_type == 'streak':
                current_streak = self._get_current_streak(user_id)
                required_streak = requirements.get('value', 0)
                return current_streak >= required_streak
            
            return False
            
        except Exception as e:
            logger.error(f"Erro ao validar elegibilidade do badge {badge_id}: {e}")
            return False

    async def _has_recent_perfect_score(self, user_id: str) -> bool:
        """Verifica se o usuário tem score perfeito recente"""
        try:
            # Implementar lógica para verificar scores recentes
            # Por enquanto, retorna False
            return False
        except Exception as e:
            logger.error(f"Erro ao verificar score perfeito: {e}")
            return False

    async def get_user_progress(self, user_id: str, badge_id: str) -> Dict[str, Any]:
        """
        Retorna o progresso do usuário para um badge específico.
        
        Args:
            user_id: ID do usuário
            badge_id: ID do badge
            
        Returns:
            Dicionário com informações de progresso
        """
        try:
            badge = self.badge_repo.get_badge_by_id(badge_id)
            if not badge:
                return {'progress': 0, 'completed': False, 'requirements': {}}
            
            requirements = badge.requirements or {}
            req_type = requirements.get('type')
            
            progress = 0
            completed = False
            
            if req_type == 'level':
                user = self.user_repo.get_user_profile(user_id)
                required_level = requirements.get('value', 0)
                if user:
                    progress = min(user.level / required_level * 100, 100)
                    completed = user.level >= required_level
                    
            elif req_type == 'points':
                user = self.user_repo.get_user_profile(user_id)
                required_points = requirements.get('value', 0)
                if user:
                    progress = min(user.points / required_points * 100, 100)
                    completed = user.points >= required_points
                    
            elif req_type == 'streak':
                current_streak = self._get_current_streak(user_id)
                required_streak = requirements.get('value', 0)
                progress = min(current_streak / required_streak * 100, 100)
                completed = current_streak >= required_streak
            
            return {
                'progress': progress,
                'completed': completed,
                'requirements': requirements,
                'badge_info': {
                    'id': badge.id,
                    'name': badge.name,
                    'description': badge.description
                }
            }
            
        except Exception as e:
            logger.error(f"Erro ao calcular progresso do badge {badge_id}: {e}")
            return {'progress': 0, 'completed': False, 'requirements': {}}

    async def _check_learning_path_badges(self, user_id: str, event: LearningPathCompletedEvent) -> List[str]:
        """Verifica badges relacionados a trilhas completadas"""
        eligible_badges = []
        
        try:
            # Badge específico da trilha
            path_id = event.learning_path_id
            if path_id == "fundamentos_dinheiro_bitcoin":
                eligible_badges.append("fundamentos_bitcoin_master")
            elif path_id == "aprofundando_bitcoin_tecnologia":
                eligible_badges.append("bitcoin_tech_expert")
            elif path_id == "bitcoin_ecossistema_financeiro":
                eligible_badges.append("bitcoin_ecosystem_master")
            
            # Badge de primeira trilha
            if self._is_first_learning_path(user_id):
                eligible_badges.append("learning_path_beginner")
            
            # Badge de múltiplas trilhas
            completed_paths = self._count_completed_learning_paths(user_id)
            if completed_paths >= 2:
                eligible_badges.append("learning_path_enthusiast")
            if completed_paths >= 3:
                eligible_badges.append("learning_path_master")
            
            logger.info(f"Badges de trilha elegíveis para usuário {user_id}: {eligible_badges}")
            return eligible_badges
            
        except Exception as e:
            logger.error(f"Erro ao verificar badges de trilha para usuário {user_id}: {e}")
            return []

    async def _check_module_badges(self, user_id: str, event: ModuleCompletedEvent) -> List[str]:
        """Verifica badges relacionados a módulos completados"""
        eligible_badges = []
        
        try:
            # Badge de primeiro módulo
            if self._is_first_module(user_id):
                eligible_badges.append("first_module_completed")
            
            # Badge de múltiplos módulos
            completed_modules = self._count_completed_modules(user_id)
            if completed_modules >= 5:
                eligible_badges.append("module_explorer")
            if completed_modules >= 10:
                eligible_badges.append("module_master")
            
            logger.info(f"Badges de módulo elegíveis para usuário {user_id}: {eligible_badges}")
            return eligible_badges
            
        except Exception as e:
            logger.error(f"Erro ao verificar badges de módulo para usuário {user_id}: {e}")
            return []

    async def _check_quiz_badges(self, user_id: str, event: QuizCompletedEvent) -> List[str]:
        """Verifica badges relacionados a quizzes"""
        eligible_badges = []
        
        try:
            # Badge de score perfeito
            if event.score >= 100:
                eligible_badges.append("perfect_quiz_score")
            
            # Badge de excelência em quizzes
            excellent_quizzes = self._count_excellent_quizzes(user_id)
            if excellent_quizzes >= 5:
                eligible_badges.append("excellent_quiz_score")
            
            logger.info(f"Badges de quiz elegíveis para usuário {user_id}: {eligible_badges}")
            return eligible_badges
            
        except Exception as e:
            logger.error(f"Erro ao verificar badges de quiz para usuário {user_id}: {e}")
            return []

    async def _is_first_learning_path(self, user_id: str) -> bool:
        """Verifica se é a primeira trilha completada"""
        try:
            # Buscar progresso das trilhas
            from app.core.firebase import get_firestore_db
            db = get_firestore_db()
            
            progress_docs = db.collection("user_path_progress")\
                .where("user_id", "==", user_id)\
                .where("completed_at", "!=", None)\
                .stream()
            
            completed_count = 0
            for doc in progress_docs:
                completed_count += 1
            
            return completed_count == 1
            
        except Exception as e:
            logger.error(f"Erro ao verificar primeira trilha para usuário {user_id}: {e}")
            return False

    async def _count_completed_learning_paths(self, user_id: str) -> int:
        """Conta trilhas completadas"""
        try:
            from app.core.firebase import get_firestore_db
            db = get_firestore_db()
            
            progress_docs = db.collection("user_path_progress")\
                .where("user_id", "==", user_id)\
                .where("completed_at", "!=", None)\
                .stream()
            
            return len(list(progress_docs))
            
        except Exception as e:
            logger.error(f"Erro ao contar trilhas completadas para usuário {user_id}: {e}")
            return 0

    async def _is_first_module(self, user_id: str) -> bool:
        """Verifica se é o primeiro módulo completado"""
        try:
            from app.core.firebase import get_firestore_db
            db = get_firestore_db()
            
            # Buscar progresso das trilhas
            progress_docs = db.collection("user_path_progress")\
                .where("user_id", "==", user_id)\
                .stream()
            
            total_modules_completed = 0
            for doc in progress_docs:
                progress_data = doc.to_dict()
                completed_missions = len(progress_data.get("completed_missions", []))
                # Assumindo 2 missões por módulo
                modules_in_path = completed_missions // 2
                total_modules_completed += modules_in_path
            
            return total_modules_completed == 1
            
        except Exception as e:
            logger.error(f"Erro ao verificar primeiro módulo para usuário {user_id}: {e}")
            return False

    async def _count_completed_modules(self, user_id: str) -> int:
        """Conta módulos completados"""
        try:
            from app.core.firebase import get_firestore_db
            db = get_firestore_db()
            
            progress_docs = db.collection("user_path_progress")\
                .where("user_id", "==", user_id)\
                .stream()
            
            total_modules_completed = 0
            for doc in progress_docs:
                progress_data = doc.to_dict()
                completed_missions = len(progress_data.get("completed_missions", []))
                # Assumindo 2 missões por módulo
                modules_in_path = completed_missions // 2
                total_modules_completed += modules_in_path
            
            return total_modules_completed
            
        except Exception as e:
            logger.error(f"Erro ao contar módulos completados para usuário {user_id}: {e}")
            return 0

    async def _count_excellent_quizzes(self, user_id: str) -> int:
        """Conta quizzes com score excelente (90%+)"""
        try:
            from app.core.firebase import get_firestore_db
            db = get_firestore_db()
            
            # Buscar recompensas de quiz
            reward_docs = db.collection("user_rewards")\
                .where("user_id", "==", user_id)\
                .where("reward_type", "==", "learning_path_module")\
                .stream()
            
            excellent_count = 0
            for doc in reward_docs:
                reward_data = doc.to_dict()
                context = reward_data.get("context", {})
                score = context.get("score", 0)
                if score >= 90:
                    excellent_count += 1
            
            return excellent_count
            
        except Exception as e:
            logger.error(f"Erro ao contar quizzes excelentes para usuário {user_id}: {e}")
            return 0


# Instância singleton do ValidationService
_validation_service_instance: Optional[ValidationService] = None

def get_validation_service() -> ValidationService:
    """Retorna a instância singleton do ValidationService"""
    global _validation_service_instance
    if _validation_service_instance is None:
        # Importar aqui para evitar dependência circular
        from app.core.firebase import get_firestore_db
        
        # Obter instâncias reais dos repositórios
        db = get_firestore_db()
        user_repo = UserRepository(db)
        badge_repo = BadgeRepository(db)
        _validation_service_instance = ValidationService(user_repo, badge_repo)
    
    return _validation_service_instance
