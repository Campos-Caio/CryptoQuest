"""
Repositório para gerenciar badges com validação de duplicatas.
Implementa operações de CRUD para badges e validação de concessões.
"""

from typing import List, Optional, Dict, Any
from app.models.reward import UserBadge, Badge
from app.core.firebase import get_firestore_db
from fastapi import Depends
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class BadgeRepository:
    """
    Repositório para gerenciar badges com validação de duplicatas.
    
    Funcionalidades:
    - Verificar se usuário já possui badge
    - Conceder badges com validação
    - Buscar badges do usuário
    - Buscar todos os badges disponíveis
    - Estatísticas de badges
    """
    
    def __init__(self, db_client):
        self.db = db_client

    def has_badge(self, user_id: str, badge_id: str) -> bool:
        """
        Verifica se o usuário já possui um badge específico.
        
        Args:
            user_id: ID do usuário
            badge_id: ID do badge
            
        Returns:
            True se o usuário já possui o badge, False caso contrário
        """
        try:
            query = self.db.collection("user_badges")\
                .where("user_id", "==", user_id)\
                .where("badge_id", "==", badge_id)\
                .limit(1)
            
            docs = query.stream()
            has_badge = False
            for doc in docs:
                has_badge = True
                break
            
            logger.debug(f"Verificação de badge {badge_id} para usuário {user_id}: {has_badge}")
            return has_badge
            
        except Exception as e:
            logger.error(f"Erro ao verificar badge {badge_id} para usuário {user_id}: {e}")
            return False

    def award_badge(self, user_id: str, badge_id: str, context: Dict[str, Any]) -> bool:
        """
        Concede um badge ao usuário com validação de duplicatas.
        
        Args:
            user_id: ID do usuário
            badge_id: ID do badge
            context: Contexto da concessão (missão, score, etc.)
            
        Returns:
            True se o badge foi concedido, False se já existia
        """
        try:
            # Verificar se já possui o badge
            if self.has_badge(user_id, badge_id):
                logger.warning(f"Tentativa de duplicar badge {badge_id} para usuário {user_id}")
                return False
            
            # Criar badge do usuário
            user_badge = UserBadge(
                user_id=user_id,
                badge_id=badge_id,
                earned_at=datetime.now(timezone.utc),
                context=context
            )
            
            # Salvar no Firestore
            doc_ref = self.db.collection("user_badges").document()
            doc_ref.set(user_badge.model_dump())
            
            logger.info(f"✅ Badge {badge_id} concedido para usuário {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao conceder badge {badge_id} para usuário {user_id}: {e}")
            return False

    def get_user_badges(self, user_id: str) -> List[UserBadge]:
        """
        Busca todos os badges do usuário.
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Lista de badges do usuário
        """
        try:
            query = self.db.collection("user_badges").where("user_id", "==", user_id)
            docs = query.stream()
            
            badges = []
            for doc in docs:
                try:
                    doc_data = doc.to_dict()
                    
                    # Validação segura dos dados
                    safe_data = {
                        'user_id': doc_data.get('user_id', user_id),
                        'badge_id': doc_data.get('badge_id'),
                        'earned_at': self._safe_get_datetime(doc_data, 'earned_at'),
                        'context': doc_data.get('context', {})
                    }
                    
                    badges.append(UserBadge(**safe_data))
                except Exception as doc_error:
                    logger.warning(f"Erro ao processar badge do usuário: {doc_error}")
                    continue
            
            logger.info(f"Recuperados {len(badges)} badges para usuário {user_id}")
            return badges
            
        except Exception as e:
            logger.error(f"Erro ao buscar badges do usuário {user_id}: {e}")
            return []

    def get_all_badges(self) -> List[Badge]:
        """
        Busca todos os badges disponíveis.
        
        Returns:
            Lista de todos os badges
        """
        try:
            docs = self.db.collection("badges").stream()
            badges = []
            
            for doc in docs:
                try:
                    doc_data = doc.to_dict()
                    
                    # Validação segura dos dados
                    safe_data = {
                        'id': doc_data.get('id', doc.id),
                        'name': doc_data.get('name', 'Badge Desconhecido'),
                        'description': doc_data.get('description', 'Descrição não disponível'),
                        'icon': doc_data.get('icon', '🏆'),
                        'rarity': doc_data.get('rarity', 'common'),
                        'color': doc_data.get('color', '#FFD700'),
                        'requirements': doc_data.get('requirements', {})
                    }
                    
                    badges.append(Badge(**safe_data))
                except Exception as doc_error:
                    logger.warning(f"Erro ao processar badge disponível: {doc_error}")
                    continue
            
            logger.info(f"Recuperados {len(badges)} badges disponíveis")
            return badges
            
        except Exception as e:
            logger.error(f"Erro ao buscar badges disponíveis: {e}")
            return []

    def get_available_badges_for_user(self, user_id: str) -> List[Badge]:
        """
        Busca badges disponíveis para um usuário específico (que ainda não conquistou).
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Lista de badges que o usuário ainda pode conquistar
        """
        try:
            # Buscar todos os badges do sistema
            all_badges = self.get_all_badges()
            
            # Buscar badges que o usuário já conquistou
            user_badges = self.get_user_badges(user_id)
            conquered_badge_ids = {badge.badge_id for badge in user_badges if badge.badge_id}
            
            # Filtrar badges não conquistados
            available_badges = [
                badge for badge in all_badges 
                if badge.id and badge.id not in conquered_badge_ids
            ]
            
            logger.info(f"Badges disponíveis para usuário {user_id}: {len(available_badges)} de {len(all_badges)} total")
            return available_badges
            
        except Exception as e:
            logger.error(f"Erro ao buscar badges disponíveis para usuário {user_id}: {e}")
            return []

    def get_badge_by_id(self, badge_id: str) -> Optional[Badge]:
        """
        Busca um badge específico por ID.
        
        Args:
            badge_id: ID do badge
            
        Returns:
            Badge encontrado ou None
        """
        try:
            doc_ref = self.db.collection("badges").document(badge_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                return None
            
            doc_data = doc.to_dict()
            safe_data = {
                'id': doc_data.get('id', badge_id),
                'name': doc_data.get('name', 'Badge Desconhecido'),
                'description': doc_data.get('description', 'Descrição não disponível'),
                'icon': doc_data.get('icon', '🏆'),
                'rarity': doc_data.get('rarity', 'common'),
                'color': doc_data.get('color', '#FFD700'),
                'requirements': doc_data.get('requirements', {})
            }
            
            return Badge(**safe_data)
            
        except Exception as e:
            logger.error(f"Erro ao buscar badge {badge_id}: {e}")
            return None

    async def get_user_badge_stats(self, user_id: str) -> Dict[str, Any]:
        """
        Retorna estatísticas de badges do usuário.
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Dicionário com estatísticas
        """
        try:
            badges = self.get_user_badges(user_id)
            all_badges = self.get_all_badges()
            
            # Contar por raridade
            rarity_counts = {}
            for badge in badges:
                badge_info = next((b for b in all_badges if b.id == badge.badge_id), None)
                if badge_info:
                    rarity = badge_info.rarity or 'unknown'
                    rarity_counts[rarity] = rarity_counts.get(rarity, 0) + 1
            
            return {
                'total_badges': len(badges),
                'total_available': len(all_badges),
                'completion_percentage': (len(badges) / len(all_badges) * 100) if all_badges else 0,
                'rarity_counts': rarity_counts,
                'recent_badges': sorted(badges, key=lambda x: x.earned_at, reverse=True)[:5]
            }
            
        except Exception as e:
            logger.error(f"Erro ao calcular estatísticas de badges para usuário {user_id}: {e}")
            return {}

    def _safe_get_datetime(self, data: Dict[str, Any], key: str, default: datetime = None) -> datetime:
        """Safely get datetime value from dict"""
        if default is None:
            default = datetime.now(timezone.utc)
            
        value = data.get(key)
        if value is None:
            return default
        
        if isinstance(value, datetime):
            return value
        elif isinstance(value, str):
            try:
                return datetime.fromisoformat(value.replace('Z', '+00:00'))
            except:
                return default
        else:
            return default


def get_badge_repository() -> BadgeRepository:
    """Retorna instância do BadgeRepository"""
    db_client = get_firestore_db()
    return BadgeRepository(db_client)
