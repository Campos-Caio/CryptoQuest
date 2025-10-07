"""
Testes unitários para EventBus.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.services.event_bus import EventBus
from app.models.events import MissionCompletedEvent, LevelUpEvent, EventType
from tests.utils.test_helpers import assert_event_emitted


class TestEventBus:
    """Testes para o EventBus"""
    
    def test_event_bus_creation(self):
        """Testa criação do EventBus"""
        event_bus = EventBus()
        assert event_bus is not None
        assert len(event_bus._handlers) == 0
        assert len(event_bus._event_log) == 0

    @pytest.mark.asyncio
    async def test_emit_event_without_handlers(self):
        """Testa emissão de evento sem handlers registrados"""
        event_bus = EventBus()
        
        event = MissionCompletedEvent(
            user_id="test_user",
            mission_id="test_mission",
            score=85.0,
            mission_type="daily"
        )
        
        # Não deve gerar erro mesmo sem handlers
        await event_bus.emit(event)
        
        # Evento deve estar no log
        assert len(event_bus._event_log) == 1
        assert event_bus._event_log[0].user_id == "test_user"

    @pytest.mark.asyncio
    async def test_subscribe_and_emit(self):
        """Testa registro de handler e emissão de evento"""
        event_bus = EventBus()
        
        # Mock handler
        handler_called = False
        received_event = None
        
        async def test_handler(event):
            nonlocal handler_called, received_event
            handler_called = True
            received_event = event
        
        # Registrar handler
        await event_bus.subscribe(EventType.MISSION_COMPLETED, test_handler)
        
        # Emitir evento
        event = MissionCompletedEvent(
            user_id="test_user",
            mission_id="test_mission",
            score=85.0,
            mission_type="daily"
        )
        
        await event_bus.emit(event)
        
        # Verificar se handler foi chamado
        assert handler_called
        assert received_event.user_id == "test_user"
        assert received_event.mission_id == "test_mission"

    @pytest.mark.asyncio
    async def test_multiple_handlers(self):
        """Testa múltiplos handlers para o mesmo evento"""
        event_bus = EventBus()
        
        handler1_called = False
        handler2_called = False
        
        async def handler1(event):
            nonlocal handler1_called
            handler1_called = True
        
        async def handler2(event):
            nonlocal handler2_called
            handler2_called = True
        
        # Registrar handlers
        await event_bus.subscribe(EventType.MISSION_COMPLETED, handler1)
        await event_bus.subscribe(EventType.MISSION_COMPLETED, handler2)
        
        # Emitir evento
        event = MissionCompletedEvent(
            user_id="test_user",
            mission_id="test_mission",
            score=85.0,
            mission_type="daily"
        )
        
        await event_bus.emit(event)
        
        # Ambos handlers devem ser chamados
        assert handler1_called
        assert handler2_called

    def test_get_stats(self):
        """Testa estatísticas do EventBus"""
        event_bus = EventBus()
        
        # Adicionar alguns eventos ao log
        event1 = MissionCompletedEvent(
            user_id="user1",
            mission_id="mission1",
            score=85.0,
            mission_type="daily"
        )
        event2 = LevelUpEvent(
            user_id="user2",
            old_level=1,
            new_level=2,
            points_required=500,
            points_earned=100
        )
        
        event_bus._add_to_log(event1)
        event_bus._add_to_log(event2)
        
        stats = event_bus.get_stats()
        
        assert stats['total_events'] == 2
        assert stats['event_counts']['mission_completed'] == 1
        assert stats['event_counts']['level_up'] == 1

    @pytest.mark.asyncio
    async def test_event_log_filtering(self):
        """Testa filtragem de eventos por usuário"""
        event_bus = EventBus()
        
        # Criar eventos para diferentes usuários
        event1 = MissionCompletedEvent(
            user_id="user1",
            mission_id="mission1",
            score=85.0,
            mission_type="daily"
        )
        event2 = MissionCompletedEvent(
            user_id="user2",
            mission_id="mission2",
            score=90.0,
            mission_type="daily"
        )
        
        await event_bus.emit(event1)
        await event_bus.emit(event2)
        
        # Filtrar por usuário
        user1_events = event_bus.get_event_log(user_id="user1")
        user2_events = event_bus.get_event_log(user_id="user2")
        
        assert len(user1_events) == 1
        assert len(user2_events) == 1
        assert user1_events[0].user_id == "user1"
        assert user2_events[0].user_id == "user2"

    @pytest.mark.asyncio
    async def test_handler_exception_handling(self):
        """Testa tratamento de exceções em handlers"""
        event_bus = EventBus()
        
        # Handler que gera exceção
        async def failing_handler(event):
            raise Exception("Handler error")
        
        # Handler normal
        normal_handler_called = False
        async def normal_handler(event):
            nonlocal normal_handler_called
            normal_handler_called = True
        
        # Registrar handlers
        await event_bus.subscribe(EventType.MISSION_COMPLETED, failing_handler)
        await event_bus.subscribe(EventType.MISSION_COMPLETED, normal_handler)
        
        # Emitir evento - não deve falhar mesmo com handler com erro
        event = MissionCompletedEvent(
            user_id="test_user",
            mission_id="test_mission",
            score=85.0,
            mission_type="daily"
        )
        
        await event_bus.emit(event)
        
        # Handler normal deve ter sido chamado
        assert normal_handler_called

