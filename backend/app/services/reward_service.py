from typing import Dict, Any, List
from app.models.reward import UserReward, UserBadge, RewardType
from app.repositories.user_repository import UserRepository, get_user_repository
from app.repositories.reward_repository import RewardRepository, get_reward_repository
from app.repositories.badge_repository import BadgeRepository, get_badge_repository
from app.services.badge_engine import get_badge_engine
from app.services.event_bus import get_event_bus
from app.core.firebase import get_firestore_db_async
from fastapi import Depends
import logging


logger = logging.getLogger(__name__)

class RewardService:
    def __init__(self, user_repo: UserRepository, reward_repo: RewardRepository, badge_repo: BadgeRepository, db_client):
        self.user_repo = user_repo
        self.reward_repo = reward_repo
        self.badge_repo = badge_repo
        self.db = db_client
        self.badge_engine = get_badge_engine()
        self.event_bus = get_event_bus()

        # Config de recompensas 
        self.REWARD_CONFIG = {
            RewardType.DAILY_MISSION: {"points": 100, "xp": 50},
            RewardType.LEARNING_PATH_MODULE: {"points": 200, "xp": 100},
            RewardType.LEARNING_PATH_COMPLETE: {"points": 500, "xp": 250},
            RewardType.STREAK_7_DAYS: {"points": 300, "xp": 150, "badge": "streak_7"},
            RewardType.STREAK_30_DAYS: {"points": 1000, "xp": 500, "badge": "streak_30"},
            RewardType.PERFECT_SCORE: {"points": 150, "xp": 75, "badge": "perfectionist"},
            RewardType.FIRST_COMPLETION: {"points": 100, "xp": 50, "badge": "first_steps"},
            RewardType.LEVEL_UP: {"points": 0, "xp": 0, "badge": "level_up"},
        }

    async def award_mission_completion(self, user_id: str, mission_id: str, score: float, mission_type: str = 'daily') -> Dict[str, Any]:
            """Concede recompensas por ocnclusao de missao"""
            try: 
                user = self.user_repo.get_user_profile(user_id)
                if not user: 
                    raise ValueError("Usuario nao encontrado") 
                
                # Determina tipo de recompensa 
                reward_type = RewardType.DAILY_MISSION if mission_type == 'daily' else RewardType.LEARNING_PATH_MODULE

                # calcular pontos baseado no score 
                base_config = self.REWARD_CONFIG[reward_type]
                points = base_config['points']
                xp = base_config['xp'] 

                # Bonus por score perfeito 
                if score >= 100: 
                    points += self.REWARD_CONFIG[RewardType.PERFECT_SCORE]['points']
                    xp += self.REWARD_CONFIG[RewardType.PERFECT_SCORE]['xp'] 
                    await self.award_badge(user_id, "perfectionist", {'mission_id': mission_id, 'score': score})
                
                if len(user.daily_missions) == 0:
                    points += self.REWARD_CONFIG[RewardType.FIRST_COMPLETION]['points']
                    xp += self.REWARD_CONFIG[RewardType.FIRST_COMPLETION]['xp'] 
                    await self.award_badge(user_id, "first_steps", {'mission_id': mission_id})

                # Aplicar recompensas  
                await self.apply_rewards(user_id, reward_type, points, xp, {
                    'mission_id': mission_id,
                    "score": score,
                    "mission_type": mission_type
                })

                await self._check_streak_rewards(user_id)

                return {
                    'points_earned': points,
                    'xp_earned': xp,
                    'badges_earned': await self._get_recent_badges(user_id), 
                    "level_up": await self._check_level_up(user_id, xp)
                }

            except Exception as e:
                logger.error(f'Erro ao conceder recompensas: {e}')
                raise 
        
    async def award_learning_path_completion(self, user_id: str, path_id: str, total_score: float) -> Dict[str, Any]: 
            """Concede recompensas por conclusao de trilha"""
            try: 
                config = self.REWARD_CONFIG[RewardType.LEARNING_PATH_COMPLETE]
                points = config['points']
                xp = config['xp']

                # Bonus por score alto 
                if total_score >= 90:
                    points += 200 
                    xp += 100 

                await self.apply_rewards(user_id, RewardType.LEARNING_PATH_COMPLETE, points, xp, {
                    'path_id': path_id,
                    'total_score': total_score
                })

                return {
                    'points_earned': points,
                    'xp_earned': xp,
                    'badges_earned': await self._get_recent_badges(user_id), 
                }
            except Exception as e:
                logger.error(f"Erro ao conceder recompensas de trilha: {e}")
                raise 
        
    async def apply_rewards(self, user_id: str, reward_type: RewardType, points: int, xp: int, context: Dict[str, Any]):
        """Aplica recompensas ao usuário"""
        # Atualiza perfil de usuário 
        await self.user_repo.update_user_Profile(user_id, {
            'points': points,
            'xp': xp
        })

        # Registra recompensa 
        user_reward = UserReward(
            user_id=user_id,
            reward_type=reward_type.value,
            points_earned=points,
            xp_earned=xp,
            context=context
        )

        self.reward_repo.save_user_reward(user_reward)
    
    async def award_badge(self, user_id: str, badge_id: str, context: Dict[str, Any]): 
        """Concede badge ao usuário usando o novo sistema"""
        try:
            # Usar BadgeRepository para conceder badge com validação de duplicatas
            success = self.badge_repo.award_badge(user_id, badge_id, context)
            if success:
                logger.info(f"✅ Badge {badge_id} concedido para usuário {user_id}")
                return True
            else:
                logger.warning(f"⚠️ Badge {badge_id} já existe para usuário {user_id}")
                return False
        except Exception as e:
            logger.error(f"❌ Erro ao conceder badge {badge_id}: {e}")
            return False

    async def _check_streak_rewards(self, user_id: str):
        """Verifica e concede recompensas de streak"""
        # Implementar lógica de streak
        pass

    async def _check_level_up(self, user_id: str, xp_earned: int) -> bool:
        """Verifica se o usuário subiu de nível"""
        # Implementar lógica de level up
        pass

    async def _get_recent_badges(self, user_id: str) -> List[str]:
        """Retorna badges recentemente conquistados"""
        # Implementar busca de badges recentes
        pass

def get_reward_service(
    user_repo = Depends(get_user_repository),
    reward_repo = Depends(get_reward_repository),
    badge_repo = Depends(get_badge_repository),
    db_client = Depends(get_firestore_db_async)
) -> RewardService:
    return RewardService(user_repo, reward_repo, badge_repo, db_client)


