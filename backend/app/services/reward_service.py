from typing import Dict, Any, List
from datetime import datetime, timedelta
from app.models.reward import UserReward, UserBadge, RewardType
from app.repositories.user_repository import UserRepository, get_user_repository
from app.repositories.reward_repository import RewardRepository, get_reward_repository
from app.repositories.badge_repository import BadgeRepository, get_badge_repository
from app.services.badge_engine import get_badge_engine
from app.services.event_bus import get_event_bus
from app.core.firebase import get_firestore_db
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
            RewardType.LEVEL_UP: {"points": 0, "xp": 0, "badge": "level_up"}
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
                    self.award_badge(user_id, "perfectionist", {'mission_id': mission_id, 'score': score})
                
                if len(user.daily_missions) == 0:
                    points += self.REWARD_CONFIG[RewardType.FIRST_COMPLETION]['points']
                    xp += self.REWARD_CONFIG[RewardType.FIRST_COMPLETION]['xp'] 
                    self.award_badge(user_id, "first_steps", {'mission_id': mission_id})

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
        # Buscar pontos atuais do usuário
        user = self.user_repo.get_user_profile(user_id)
        if not user:
            raise ValueError(f"Usuário {user_id} não encontrado")
        
        current_points = user.points or 0
        current_xp = user.xp or 0
        
        # Atualiza perfil de usuário com pontos incrementais
        self.user_repo.update_user_Profile(user_id, {
            'points': current_points + points,
            'xp': current_xp + xp
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
    
    def award_badge(self, user_id: str, badge_id: str, context: Dict[str, Any]): 
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
        try:
            user = self.user_repo.get_user_profile(user_id)
            if not user:
                return
            
            # Calcular streak baseado em daily_missions
            current_streak = user.current_streak or 0
            
            # Verificar se completou missão hoje
            today = datetime.now().date()
            completed_today = False
            
            for mission_id in user.daily_missions:
                # Verificar se a missão foi completada hoje
                # Por simplicidade, assumimos que se está na lista, foi completada recentemente
                completed_today = True
                break
            
            if completed_today:
                new_streak = current_streak + 1
                
                # Atualizar streak do usuário
                self.user_repo.update_user_profile(user_id, {'current_streak': new_streak})
                
                # Verificar recompensas de streak
                if new_streak == 7:
                    await self.apply_rewards(user_id, RewardType.STREAK_7_DAYS, 300, 150, {
                        'streak_days': 7,
                        'achieved_at': datetime.now().isoformat()
                    })
                    self.award_badge(user_id, "streak_7", {'streak_days': 7})
                    
                elif new_streak == 30:
                    await self.apply_rewards(user_id, RewardType.STREAK_30_DAYS, 1000, 500, {
                        'streak_days': 30,
                        'achieved_at': datetime.now().isoformat()
                    })
                    self.award_badge(user_id, "streak_30", {'streak_days': 30})
            else:
                # Reset streak se não completou missão hoje
                if current_streak > 0:
                    self.user_repo.update_user_profile(user_id, {'current_streak': 0})
                    
        except Exception as e:
            logger.error(f'Erro ao verificar streak rewards: {e}')

    async def _check_level_up(self, user_id: str, xp_earned: int) -> bool:
        """Verifica se o usuário subiu de nível"""
        try:
            user = self.user_repo.get_user_profile(user_id)
            if not user:
                return False
            
            # Calcular novo nível baseado no XP total
            total_xp = user.xp + xp_earned
            new_level = self._calculate_level_from_xp(total_xp)
            
            if new_level > user.level:
                # Usuário subiu de nível
                old_level = user.level
                
                # Atualizar nível do usuário (XP já foi atualizado em apply_rewards)
                self.user_repo.update_user_profile(user_id, {
                    'level': new_level
                })
                
                # Conceder badge de level up
                self.award_badge(user_id, "level_up", {
                    'old_level': old_level,
                    'new_level': new_level,
                    'achieved_at': datetime.now().isoformat()
                })
                
                # Emitir evento de level up
                from app.services.event_bus import get_event_bus
                from app.models.events import LevelUpEvent
                event_bus = get_event_bus()
                await event_bus.emit(LevelUpEvent(
                    user_id=user_id,
                    old_level=old_level,
                    new_level=new_level,
                    points_required=total_xp,
                    points_earned=xp_earned
                ))
                
                logger.info(f'Usuário {user_id} subiu do nível {old_level} para {new_level}')
                return True
            
            return False
            
        except Exception as e:
            logger.error(f'Erro ao verificar level up: {e}')
            return False
    
    def _calculate_level_from_xp(self, xp: int) -> int:
        """Calcula o nível baseado no XP total"""
        # Fórmula simples: cada nível requer 100 XP a mais que o anterior
        # Nível 1: 0-99 XP
        # Nível 2: 100-299 XP  
        # Nível 3: 300-599 XP
        # Nível 4: 600-999 XP
        # etc.
        
        if xp < 100:
            return 1
        elif xp < 300:
            return 2
        elif xp < 600:
            return 3
        elif xp < 1000:
            return 4
        elif xp < 1500:
            return 5
        elif xp < 2100:
            return 6
        elif xp < 2800:
            return 7
        elif xp < 3600:
            return 8
        elif xp < 4500:
            return 9
        else:
            return 10  # Nível máximo

    async def _get_recent_badges(self, user_id: str) -> List[str]:
        """Retorna badges recentemente conquistados"""
        try:
            # Buscar badges do usuário
            user_badges = self.badge_repo.get_user_badges(user_id)
            
            # Filtrar badges conquistados nas últimas 24 horas
            recent_badges = []
            cutoff_time = datetime.now() - timedelta(hours=24)
            
            for badge in user_badges:
                if badge.earned_at >= cutoff_time:
                    recent_badges.append(badge.badge_id)
            
            return recent_badges
            
        except Exception as e:
            logger.error(f'Erro ao buscar badges recentes: {e}')
            return []

def get_reward_service(
    user_repo = Depends(get_user_repository),
    reward_repo = Depends(get_reward_repository),
    badge_repo = Depends(get_badge_repository),
    db_client = Depends(get_firestore_db)
) -> RewardService:
    return RewardService(user_repo, reward_repo, badge_repo, db_client)


