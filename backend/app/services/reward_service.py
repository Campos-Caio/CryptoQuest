from typing import Dict, Any, List
from datetime import datetime
from app.models.reward import UserReward, UserBadge, RewardType
from app.repositories.user_repository import UserRepository, get_user_repository
from app.repositories.reward_repository import RewardRepository, get_reward_repository
from app.repositories.badge_repository import BadgeRepository, get_badge_repository
from app.services.badge_engine import get_badge_engine
from app.services.event_bus import get_event_bus
from app.core.firebase import get_firestore_db_async
from app.core.logging_config import get_cryptoquest_logger
from app.services.fast_cache_service import get_fast_cache
from fastapi import Depends
import logging


logger = logging.getLogger(__name__)
cryptoquest_logger = get_cryptoquest_logger()

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
            # Recompensas base por missão (REBALANCEADAS)
            RewardType.DAILY_MISSION: {"points": 50, "xp": 100},
            RewardType.LEARNING_PATH_MODULE: {"points": 75, "xp": 150},
            RewardType.LEARNING_PATH_COMPLETE: {"points": 250, "xp": 500},
            
            # Recompensas por sequência (MELHORADAS)
            RewardType.STREAK_7_DAYS: {"points": 300, "xp": 200, "badge": "streak_7"},
            RewardType.STREAK_30_DAYS: {"points": 1500, "xp": 1000, "badge": "streak_30"},
            
            # Recompensas por performance (OTIMIZADAS)
            RewardType.PERFECT_SCORE: {"points": 100, "xp": 50, "badge": "perfectionist"},
            RewardType.FIRST_COMPLETION: {"points": 150, "xp": 100, "badge": "first_steps"},
            RewardType.LEVEL_UP: {"points": 0, "xp": 0, "badge": "level_up"},
        }

    async def award_mission_completion(self, user_id: str, mission_id: str, score: float, mission_type: str = 'daily') -> Dict[str, Any]:
        """Concede recompensas por conclusão de missão"""
        try: 
            user = self.user_repo.get_user_profile(user_id)
            if not user: 
                raise ValueError("Usuário não encontrado") 
            
            # Determina tipo de recompensa baseado no tipo de missão
            reward_type = RewardType.DAILY_MISSION if mission_type == 'daily' else RewardType.LEARNING_PATH_MODULE
            base_reward = self.REWARD_CONFIG[reward_type]
            
            points = base_reward['points']
            xp = base_reward['xp']
            
            # Bonus por score perfeito
            if score >= 1.0:
                points += self.REWARD_CONFIG[RewardType.PERFECT_SCORE]['points']
                xp += self.REWARD_CONFIG[RewardType.PERFECT_SCORE]['xp'] 
                await self.award_badge(user_id, "perfectionist", {'mission_id': mission_id, 'score': score})
            
            if len(user.daily_missions) == 0:
                points += self.REWARD_CONFIG[RewardType.FIRST_COMPLETION]['points']
                xp += self.REWARD_CONFIG[RewardType.FIRST_COMPLETION]['xp'] 
                await self.award_badge(user_id, "first_steps", {'mission_id': mission_id})

            # Aplicar recompensas  
            reward_data = await self.apply_rewards(user_id, reward_type, points, xp, {
                'mission_id': mission_id,
                'score': score,
                'mission_type': mission_type
            })
            
            # Verificar streaks
            await self._check_streak_rewards(user_id)

            # Log de evento de negócio
            cryptoquest_logger.log_business_event(
                "mission_reward_awarded",
                {
                    "user_id": user_id,
                    "mission_id": mission_id,
                    "points_earned": points,
                    "xp_earned": xp,
                    "score": score,
                    "mission_type": mission_type
                }
            )

            return reward_data
            
        except Exception as e:
            logger.error(f"Erro ao conceder recompensa de missão: {e}")
            raise

    async def award_learning_path_completion(self, user_id: str, path_id: str, total_score: float) -> Dict[str, Any]: 
        """Concede recompensas por conclusão de trilha de aprendizado"""
        try:
            user = self.user_repo.get_user_profile(user_id)
            if not user:
                raise ValueError("Usuário não encontrado")
            
            base_reward = self.REWARD_CONFIG[RewardType.LEARNING_PATH_COMPLETE]
            points = base_reward['points']
            xp = base_reward['xp']
            
            # Bonus por score alto
            if total_score >= 0.9:
                points += 200
                xp += 100
            
            await self.apply_rewards(user_id, RewardType.LEARNING_PATH_COMPLETE, points, xp, {
                'path_id': path_id,
                'total_score': total_score
            })

            # ✅ CORREÇÃO: Buscar usuário ATUALIZADO
            updated_user = self.user_repo.get_user_profile(user_id)

            # Log de evento de negócio
            cryptoquest_logger.log_business_event(
                "learning_path_reward_awarded",
                {
                    "user_id": user_id,
                    "path_id": path_id,
                    "points_earned": points,
                    "xp_earned": xp,
                    "total_score": total_score
                }
            )

            return {
                'points_earned': points,
                'xp_earned': xp,
                'total_points': updated_user.points if updated_user else 0,  # ✅ Valores ATUALIZADOS!
                'total_xp': updated_user.xp if updated_user else 0
            }
            
        except Exception as e:
            logger.error(f"Erro ao conceder recompensa de trilha: {e}")
            raise

    async def apply_rewards(self, user_id: str, reward_type: RewardType, points: int, xp: int, context: Dict[str, Any]):
        """Aplica recompensas ao usuário"""
        # ✅ CORREÇÃO: Buscar valores atuais e SOMAR (não sobrescrever!)
        user = self.user_repo.get_user_profile(user_id)
        if not user:
            raise ValueError(f"Usuário {user_id} não encontrado")
        
        current_points = user.points if user.points else 0
        current_xp = user.xp if user.xp else 0
        
        # Atualiza perfil de usuário SOMANDO os valores
        new_total_points = current_points + points
        new_total_xp = current_xp + xp
        
        self.user_repo.update_user_profile(user_id, {
            'points': new_total_points,
            'xp': new_total_xp
        })
        
        logger.info(f"✅ Recompensas aplicadas: {user_id} ganhou +{points} pontos e +{xp} XP")
        logger.info(f"   Pontos: {current_points} → {new_total_points}")
        logger.info(f"   XP: {current_xp} → {new_total_xp}")

        # Criar registro de recompensa
        user_reward = UserReward(
            user_id=user_id,
            reward_type=reward_type,
            points=points,
            xp=xp,
            context=context,
            awarded_at=datetime.now()
        )
        
        # Salvar registro de recompensa
        await self.reward_repo.save_user_reward(user_reward)
        
        # Retornar dados de recompensa para o frontend
        return {
            'points_earned': points,
            'xp_earned': xp,
            'total_points': new_total_points,
            'total_xp': new_total_xp,
            'badges_earned': []  # Será populado pelo sistema de badges se funcionar
        }
    
    async def apply_basic_rewards_fast(self, user_id: str, points: int, xp: int):
        """
        ⚡ OTIMIZADO: Versão rápida para aplicar recompensas básicas com cache.
        Sem verificação de badges ou processamento pesado.
        """
        try:
            cache = get_fast_cache()
            cache_key = f"user_profile:{user_id}"
            
            # ⚡ Tentar buscar do cache primeiro
            user = cache.get(cache_key)
            
            if not user:
                # Cache miss - buscar do banco
                user = self.user_repo.get_user_profile(user_id)
                if not user:
                    raise ValueError(f"Usuário {user_id} não encontrado")
                
                # Cachear por 2 minutos
                cache.set(cache_key, user, ttl_seconds=120)
                logger.debug(f"💾 User profile cacheado: {user_id}")
            else:
                logger.debug(f"⚡ Cache hit para user profile: {user_id}")
            
            current_points = user.points if user.points else 0
            current_xp = user.xp if user.xp else 0
            
            # Atualizar perfil (operação única e rápida)
            new_total_points = current_points + points
            new_total_xp = current_xp + xp
            
            self.user_repo.update_user_profile(user_id, {
                'points': new_total_points,
                'xp': new_total_xp
            })
            
            # ⚡ Invalidar cache após atualização
            cache.invalidate(cache_key)
            
            logger.info(f"⚡ [FAST] Recompensas básicas aplicadas: {user_id} (+{points} pts, +{xp} XP)")
            
            return {
                'points_earned': points,
                'xp_earned': xp,
                'total_points': new_total_points,
                'total_xp': new_total_xp
            }
            
        except Exception as e:
            logger.error(f"Erro ao aplicar recompensas rápidas: {e}")
            raise
    
    async def award_badge(self, user_id: str, badge_id: str, context: Dict[str, Any]): 
        """Concede badge ao usuário usando o novo sistema"""
        try:
            success = await self.badge_engine.award_badge(user_id, badge_id, context)
            if success:
                logger.info(f"✅ Badge {badge_id} concedido para usuário {user_id}")
                return True
            else:
                logger.warning(f"⚠️ Badge {badge_id} não pôde ser concedido para usuário {user_id}")
                return False
        except Exception as e:
            logger.error(f"❌ Erro ao conceder badge {badge_id} para usuário {user_id}: {e}")
            return False

    async def _check_streak_rewards(self, user_id: str):
        """Verifica e concede recompensas de streak"""
        # Implementar lógica de streak
        pass

    async def get_user_recent_badges(self, user_id: str, limit: int = 5) -> List[UserBadge]:
        """Busca badges recentes do usuário"""
        # Implementar busca de badges recentes
        pass

def get_reward_service(
    user_repo: UserRepository = Depends(get_user_repository),
    reward_repo: RewardRepository = Depends(get_reward_repository),
    badge_repo: BadgeRepository = Depends(get_badge_repository),
    db_client = Depends(get_firestore_db_async)
) -> RewardService:
    return RewardService(user_repo, reward_repo, badge_repo, db_client)
