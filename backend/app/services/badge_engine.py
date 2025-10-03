"""
Motor centralizado de badges para o sistema de recompensas.
Coordena a verificação e concessão de badges baseado em eventos.
"""

from typing import List, Dict, Any, Optional
from app.models.events import BaseEvent, EventType
from app.services.event_bus import event_bus
from app.services.validation_service import ValidationService
from app.repositories.badge_repository import BadgeRepository
from app.repositories.user_repository import UserRepository
import logging

logger = logging.getLogger(__name__)


class BadgeEngine:
    """
    Motor centralizado para processar badges baseado em eventos.
    
    Responsabilidades:
    - Processar eventos e verificar condições de badges
    - Conceder badges elegíveis
    - Manter log de auditoria
    - Coordenar validações
    """
    
    def __init__(self, validation_service: ValidationService, badge_repo: BadgeRepository):
        self.validation_service = validation_service
        self.badge_repo = badge_repo
        self._awarded_badges_log: List[Dict[str, Any]] = []
        
        # Registrar handlers de eventos (será chamado quando necessário)
        self._handlers_registered = False

    async def _register_event_handlers(self):
        """Registra handlers para diferentes tipos de eventos"""
        await event_bus.subscribe(EventType.MISSION_COMPLETED, self._handle_mission_completed)
        await event_bus.subscribe(EventType.LEVEL_UP, self._handle_level_up)
        await event_bus.subscribe(EventType.POINTS_EARNED, self._handle_points_earned)
        await event_bus.subscribe(EventType.LEARNING_PATH_COMPLETED, self._handle_learning_path_completed)
        await event_bus.subscribe(EventType.QUIZ_COMPLETED, self._handle_quiz_completed)
<<<<<<< HEAD
        await event_bus.subscribe(EventType.MODULE_COMPLETED, self._handle_module_completed)
=======
>>>>>>> ceffef1 (feat: Implementacao final do sistema de recompensas)
        
        logger.info("🎯 Handlers de eventos registrados no BadgeEngine")

    async def _handle_mission_completed(self, event: BaseEvent):
        """Handler para eventos de missão completada"""
        try:
            logger.info(f"🎯 Processando missão completada para usuário {event.user_id}")
            await self._process_event_for_badges(event)
        except Exception as e:
            logger.error(f"Erro ao processar missão completada: {e}")

    async def _handle_level_up(self, event: BaseEvent):
        """Handler para eventos de subida de nível"""
        try:
            logger.info(f"🎯 Processando level up para usuário {event.user_id}")
            await self._process_event_for_badges(event)
        except Exception as e:
            logger.error(f"Erro ao processar level up: {e}")

    async def _handle_points_earned(self, event: BaseEvent):
        """Handler para eventos de pontos ganhos"""
        try:
            logger.info(f"🎯 Processando pontos ganhos para usuário {event.user_id}")
            await self._process_event_for_badges(event)
        except Exception as e:
            logger.error(f"Erro ao processar pontos ganhos: {e}")

    async def _handle_learning_path_completed(self, event: BaseEvent):
        """Handler para eventos de trilha completada"""
        try:
            logger.info(f"🎯 Processando trilha completada para usuário {event.user_id}")
            await self._process_event_for_badges(event)
        except Exception as e:
            logger.error(f"Erro ao processar trilha completada: {e}")

    async def _handle_quiz_completed(self, event: BaseEvent):
        """Handler para eventos de quiz completado"""
        try:
            logger.info(f"🎯 Processando quiz completado para usuário {event.user_id}")
            await self._process_event_for_badges(event)
        except Exception as e:
            logger.error(f"Erro ao processar quiz completado: {e}")

<<<<<<< HEAD
    async def _handle_module_completed(self, event: BaseEvent):
        """Handler para eventos de módulo completado"""
        try:
            logger.info(f"🎯 Processando módulo completado para usuário {event.user_id}")
            await self._process_event_for_badges(event)
        except Exception as e:
            logger.error(f"Erro ao processar módulo completado: {e}")

=======
>>>>>>> ceffef1 (feat: Implementacao final do sistema de recompensas)
    async def _process_event_for_badges(self, event: BaseEvent):
        """
        Processa um evento e verifica badges elegíveis.
        
        Args:
            event: Evento a ser processado
        """
        try:
            # Registrar handlers se ainda não foram registrados
            if not self._handlers_registered:
                await self._register_event_handlers()
                self._handlers_registered = True
            
            # Verificar badges elegíveis
            eligible_badges = await self.validation_service.check_badge_conditions(
                event.user_id, event
            )
            
            if not eligible_badges:
                logger.debug(f"Nenhum badge elegível para usuário {event.user_id}")
                return
            
            # Conceder badges elegíveis
            awarded_badges = []
            for badge_id in eligible_badges:
<<<<<<< HEAD
                success = self._award_badge_if_eligible(
=======
                success = await self._award_badge_if_eligible(
>>>>>>> ceffef1 (feat: Implementacao final do sistema de recompensas)
                    event.user_id, 
                    badge_id, 
                    event.context
                )
                
                if success:
                    awarded_badges.append(badge_id)
            
            if awarded_badges:
                logger.info(f"🏆 Badges concedidos para usuário {event.user_id}: {awarded_badges}")
                await self._log_badge_awards(event.user_id, awarded_badges, event)
            
        except Exception as e:
            logger.error(f"Erro ao processar evento para badges: {e}")

<<<<<<< HEAD
    def _award_badge_if_eligible(self, user_id: str, badge_id: str, context: Dict[str, Any]) -> bool:
=======
    async def _award_badge_if_eligible(self, user_id: str, badge_id: str, context: Dict[str, Any]) -> bool:
>>>>>>> ceffef1 (feat: Implementacao final do sistema de recompensas)
        """
        Concede um badge se o usuário for elegível.
        
        Args:
            user_id: ID do usuário
            badge_id: ID do badge
            context: Contexto da concessão
            
        Returns:
            True se o badge foi concedido, False caso contrário
        """
        try:
            # Verificar se já possui o badge
<<<<<<< HEAD
            has_badge = self.badge_repo.has_badge(user_id, badge_id)
=======
            has_badge = await self.badge_repo.has_badge(user_id, badge_id)
>>>>>>> ceffef1 (feat: Implementacao final do sistema de recompensas)
            if has_badge:
                logger.debug(f"Usuário {user_id} já possui badge {badge_id}")
                return False
            
            # Verificar elegibilidade
<<<<<<< HEAD
            is_eligible = self.validation_service.validate_badge_eligibility(
=======
            is_eligible = await self.validation_service.validate_badge_eligibility(
>>>>>>> ceffef1 (feat: Implementacao final do sistema de recompensas)
                user_id, badge_id
            )
            
            if not is_eligible:
                logger.debug(f"Usuário {user_id} não é elegível para badge {badge_id}")
                return False
            
            # Conceder badge
<<<<<<< HEAD
            success = self.badge_repo.award_badge(user_id, badge_id, context)
=======
            success = await self.badge_repo.award_badge(user_id, badge_id, context)
>>>>>>> ceffef1 (feat: Implementacao final do sistema de recompensas)
            
            if success:
                logger.info(f"✅ Badge {badge_id} concedido para usuário {user_id}")
            else:
                logger.warning(f"❌ Falha ao conceder badge {badge_id} para usuário {user_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Erro ao conceder badge {badge_id} para usuário {user_id}: {e}")
            return False

    async def _log_badge_awards(self, user_id: str, badge_ids: List[str], event: BaseEvent):
        """
        Registra concessões de badges no log de auditoria.
        
        Args:
            user_id: ID do usuário
            badge_ids: Lista de IDs de badges concedidos
            event: Evento que disparou a concessão
        """
        try:
            for badge_id in badge_ids:
                award_log = {
                    'user_id': user_id,
                    'badge_id': badge_id,
                    'event_type': event.event_type,
                    'event_context': event.context,
                    'timestamp': event.timestamp
                }
                self._awarded_badges_log.append(award_log)
            
            # Manter apenas os últimos 1000 registros
            if len(self._awarded_badges_log) > 1000:
                self._awarded_badges_log = self._awarded_badges_log[-1000:]
                
        except Exception as e:
            logger.error(f"Erro ao registrar concessão de badges: {e}")

    async def get_user_badge_progress(self, user_id: str) -> Dict[str, Any]:
        """
        Retorna o progresso de badges do usuário.
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Dicionário com informações de progresso
        """
        try:
            # Buscar badges do usuário
            user_badges = await self.badge_repo.get_user_badges(user_id)
            all_badges = await self.badge_repo.get_all_badges()
            
            # Calcular progresso para cada badge
            progress_info = {}
            for badge in all_badges:
                if not badge.id:
                    continue
                    
                progress = await self.validation_service.get_user_progress(user_id, badge.id)
                progress_info[badge.id] = {
                    'badge': badge,
                    'progress': progress,
                    'has_badge': any(ub.badge_id == badge.id for ub in user_badges)
                }
            
            return {
                'user_id': user_id,
                'total_badges': len(all_badges),
                'earned_badges': len(user_badges),
                'completion_percentage': (len(user_badges) / len(all_badges) * 100) if all_badges else 0,
                'badge_progress': progress_info
            }
            
        except Exception as e:
            logger.error(f"Erro ao calcular progresso de badges para usuário {user_id}: {e}")
            return {}

    async def get_recent_awards(self, user_id: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retorna as concessões recentes de badges.
        
        Args:
            user_id: Filtrar por usuário específico
            limit: Limite de registros
            
        Returns:
            Lista de concessões recentes
        """
        try:
            awards = self._awarded_badges_log.copy()
            
            if user_id:
                awards = [a for a in awards if a['user_id'] == user_id]
            
            # Ordenar por timestamp (mais recentes primeiro)
            awards.sort(key=lambda x: x['timestamp'], reverse=True)
            
            return awards[:limit]
            
        except Exception as e:
            logger.error(f"Erro ao buscar concessões recentes: {e}")
            return []

    def get_engine_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas do BadgeEngine.
        
        Returns:
            Dicionário com estatísticas
        """
        try:
            total_awards = len(self._awarded_badges_log)
            
            # Contar por tipo de evento
            event_counts = {}
            for award in self._awarded_badges_log:
                event_type = award['event_type']
                event_counts[event_type] = event_counts.get(event_type, 0) + 1
            
            return {
                'total_awards': total_awards,
                'awards_by_event_type': event_counts,
                'recent_awards': self._awarded_badges_log[-10:] if self._awarded_badges_log else []
            }
            
        except Exception as e:
            logger.error(f"Erro ao calcular estatísticas do BadgeEngine: {e}")
            return {}

    async def force_check_badges(self, user_id: str) -> List[str]:
        """
        Força verificação de todos os badges para um usuário.
        Útil para migração ou correção de dados.
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Lista de badges concedidos
        """
        try:
            logger.info(f"🔍 Verificação forçada de badges para usuário {user_id}")
            
            # Buscar todos os badges disponíveis
            all_badges = await self.badge_repo.get_all_badges()
            awarded_badges = []
            
            for badge in all_badges:
                if not badge.id:
                    continue
                    
                # Verificar elegibilidade
                is_eligible = await self.validation_service.validate_badge_eligibility(
                    user_id, badge.id
                )
                
                if is_eligible:
                    # Conceder badge
<<<<<<< HEAD
                    success = self.badge_repo.award_badge(
=======
                    success = await self.badge_repo.award_badge(
>>>>>>> ceffef1 (feat: Implementacao final do sistema de recompensas)
                        user_id, 
                        badge.id, 
                        {'source': 'force_check', 'timestamp': 'now'}
                    )
                    
                    if success:
                        awarded_badges.append(badge.id)
            
            logger.info(f"🏆 Badges concedidos na verificação forçada: {awarded_badges}")
            return awarded_badges
            
        except Exception as e:
            logger.error(f"Erro na verificação forçada de badges para usuário {user_id}: {e}")
            return []


# Instância singleton do BadgeEngine
_badge_engine_instance: Optional[BadgeEngine] = None

def get_badge_engine() -> BadgeEngine:
    """Retorna a instância singleton do BadgeEngine"""
    global _badge_engine_instance
    if _badge_engine_instance is None:
        # Importar aqui para evitar dependência circular
        from app.services.validation_service import get_validation_service
        from app.repositories.badge_repository import get_badge_repository
        
        validation_service = get_validation_service()
        badge_repo = get_badge_repository()
        _badge_engine_instance = BadgeEngine(validation_service, badge_repo)
    
    return _badge_engine_instance
