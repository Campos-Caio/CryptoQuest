from typing import List, Dict, Any
from app.models.reward import UserReward, UserBadge, Badge
from app.core.firebase import get_firestore_db_async
from fastapi import Depends
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class RewardRepository:
    def __init__(self, db_client):
        self.db = db_client

    def _safe_get_string(self, data: Dict[str, Any], key: str, default: str = "") -> str:
        """Safely get string value from dict, handling null values"""
        value = data.get(key)
        if value is None or not isinstance(value, str):
            return default
        return value

    def _safe_get_int(self, data: Dict[str, Any], key: str, default: int = 0) -> int:
        """Safely get int value from dict, handling null values"""
        value = data.get(key)
        if value is None or not isinstance(value, int):
            return default
        return value

    def _safe_get_datetime(self, data: Dict[str, Any], key: str, default: datetime = None) -> datetime:
        """Safely get datetime value from dict, handling null values and string conversion"""
        if default is None:
            default = datetime.utcnow()
            
        value = data.get(key)
        if value is None:
            return default
        
        if isinstance(value, datetime):
            return value
        elif isinstance(value, str):
            try:
                # Tentar diferentes formatos de string
                if 'T' in value:
                    # Formato ISO
                    return datetime.fromisoformat(value.replace('Z', '+00:00'))
                else:
                    # Formato simples
                    return datetime.fromisoformat(value)
            except Exception:
                try:
                    # Tentar parsing com strptime
                    from dateutil import parser
                    return parser.parse(value)
                except Exception:
                    return default
        elif hasattr(value, 'timestamp'):
            # Firestore Timestamp
            try:
                return value.to_pydatetime()
            except Exception:
                return default
        else:
            return default

    def _safe_get_dict(self, data: Dict[str, Any], key: str, default: Dict[str, Any] = None) -> Dict[str, Any]:
        """Safely get dict value from dict, handling null values"""
        if default is None:
            default = {}
            
        value = data.get(key)
        if value is None or not isinstance(value, dict):
            return default
        return value

    def save_user_reward(self, user_reward: UserReward):
        """Salva recompensa do usuário"""
        try:
            doc_ref = self.db.collection("user_rewards").document()
            doc_ref.set(user_reward.model_dump())
        except Exception as e:
            logger.error(f"Erro ao salvar recompensa: {e}")
            raise

    def save_user_badge(self, user_badge: UserBadge):
        """Salva badge do usuário"""
        try:
            doc_ref = self.db.collection("user_badges").document()
            doc_ref.set(user_badge.model_dump())
        except Exception as e:
            logger.error(f"Erro ao salvar badge: {e}")
            raise

    def get_user_rewards(self, user_id: str, limit: int = 50) -> List[UserReward]:
        """Busca recompensas do usuário"""
        try:
            # Remover order_by para evitar erro de índice
            query = self.db.collection("user_rewards").where("user_id", "==", user_id).limit(limit)
            docs = query.stream()
            
            rewards = []
            for doc in docs:
                try:
                    doc_data = doc.to_dict()
                    
                    # Usar métodos seguros para validar dados
                    safe_data = {
                        'user_id': self._safe_get_string(doc_data, 'user_id', user_id),
                        'reward_id': self._safe_get_string(doc_data, 'reward_id') or None,
                        'reward_type': self._safe_get_string(doc_data, 'reward_type', 'unknown'),
                        'points_earned': self._safe_get_int(doc_data, 'points_earned', 0),
                        'xp_earned': self._safe_get_int(doc_data, 'xp_earned', 0),
                        'earned_at': self._safe_get_datetime(doc_data, 'earned_at'),
                        'context': self._safe_get_dict(doc_data, 'context', {})
                    }
                    
                    rewards.append(UserReward(**safe_data))
                except Exception as doc_error:
                    logger.warning(f"Erro ao processar documento de recompensa: {doc_error}")
                    continue
            
            # Ordenar localmente por data
            rewards.sort(key=lambda x: x.earned_at, reverse=True)
            return rewards
        except Exception as e:
            logger.error(f"Erro ao buscar recompensas: {e}")
            return []

    def get_user_badges(self, user_id: str) -> List[UserBadge]:
        """Busca badges do usuário"""
        try:
            query = self.db.collection("user_badges").where("user_id", "==", user_id)
            docs = query.stream()
            
            badges = []
            for doc in docs:
                try:
                    doc_data = doc.to_dict()
                    
                    # Usar métodos seguros para validar dados
                    safe_data = {
                        'user_id': self._safe_get_string(doc_data, 'user_id', user_id),
                        'badge_id': self._safe_get_string(doc_data, 'badge_id') or None,
                        'earned_at': self._safe_get_datetime(doc_data, 'earned_at'),
                        'context': self._safe_get_dict(doc_data, 'context', {})
                    }
                    
                    badges.append(UserBadge(**safe_data))
                except Exception as doc_error:
                    logger.warning(f"Erro ao processar documento de badge: {doc_error}")
                    continue
            
            return badges
        except Exception as e:
            logger.error(f"Erro ao buscar badges: {e}")
            return []

    def get_all_badges(self) -> List[Badge]:
        """Busca todos os badges disponíveis"""
        try:
            docs = self.db.collection("badges").stream()
            badges = []
            for doc in docs:
                try:
                    doc_data = doc.to_dict()
                    
                    # Usar métodos seguros para validar dados
                    safe_data = {
                        'id': self._safe_get_string(doc_data, 'id', doc.id),
                        'name': self._safe_get_string(doc_data, 'name', 'Badge Desconhecido'),
                        'description': self._safe_get_string(doc_data, 'description', 'Descrição não disponível'),
                        'icon': self._safe_get_string(doc_data, 'icon', '🏆'),
                        'rarity': self._safe_get_string(doc_data, 'rarity', 'common'),
                        'color': self._safe_get_string(doc_data, 'color', '#FFD700'),
                        'requirements': self._safe_get_dict(doc_data, 'requirements', {})
                    }
                    
                    badges.append(Badge(**safe_data))
                except Exception as doc_error:
                    logger.warning(f"Erro ao processar documento de badge disponível: {doc_error}")
                    continue
            return badges
        except Exception as e:
            logger.error(f"Erro ao buscar badges: {e}")
            return []

def get_reward_repository(db_client = Depends(get_firestore_db_async)) -> RewardRepository:
    return RewardRepository(db_client)