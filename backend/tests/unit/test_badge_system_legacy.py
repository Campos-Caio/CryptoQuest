"""
Testes para o sistema de badges baseado em eventos.
Valida a implementação da Fase 1 do sistema de recompensas.
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

from app.models.events import MissionCompletedEvent, LevelUpEvent, EventType
from app.services.event_bus import EventBus
from app.services.badge_engine import BadgeEngine
from app.services.validation_service import ValidationService
from app.repositories.badge_repository import BadgeRepository
from app.repositories.user_repository import UserRepository


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


class TestBadgeRepository:
    """Testes para o BadgeRepository"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock do banco de dados"""
        mock_db = MagicMock()
        
        # Configurar mock para collection
        mock_collection = MagicMock()
        mock_db.collection.return_value = mock_collection
        
        return mock_db
    
    @pytest.fixture
    def badge_repo(self, mock_db):
        """Instância do BadgeRepository com mock"""
        return BadgeRepository(mock_db)

    @pytest.mark.asyncio
    async def test_has_badge_true(self, badge_repo, mock_db):
        """Testa verificação de badge existente"""
        # Mock do Firestore - configurar corretamente para async
        mock_doc = MagicMock()
        
        # Criar um async generator que retorna um documento
        async def mock_stream():
            yield mock_doc
        
        # Configurar a cadeia de mocks
        mock_query = MagicMock()
        mock_query.where.return_value.where.return_value.limit.return_value.stream.return_value = mock_stream()
        
        mock_collection = mock_db.collection.return_value
        mock_collection.where.return_value.where.return_value.limit.return_value.stream.return_value = mock_stream()
        
        # Testar
        result = await badge_repo.has_badge("user1", "badge1")
        
        assert result is True
        mock_db.collection.assert_called_with("user_badges")

    @pytest.mark.asyncio
    async def test_has_badge_false(self, badge_repo, mock_db):
        """Testa verificação de badge inexistente"""
        # Mock do Firestore - sem documentos
        async def mock_empty_stream():
            return
            yield  # Generator vazio
        
        # Configurar a cadeia de mocks
        mock_collection = mock_db.collection.return_value
        mock_collection.where.return_value.where.return_value.limit.return_value.stream.return_value = mock_empty_stream()
        
        # Testar
        result = await badge_repo.has_badge("user1", "badge1")
        
        assert result is False

    @pytest.mark.asyncio
    async def test_award_badge_success(self, badge_repo, mock_db):
        """Testa concessão de badge com sucesso"""
        # Mock - usuário não tem o badge (has_badge retorna False)
        async def mock_empty_stream():
            return
            yield  # Generator vazio
        
        # Configurar a cadeia de mocks para has_badge
        mock_collection = mock_db.collection.return_value
        mock_collection.where.return_value.where.return_value.limit.return_value.stream.return_value = mock_empty_stream()
        
        # Mock para salvar badge
        mock_doc_ref = AsyncMock()
        mock_collection.document.return_value = mock_doc_ref
        
        # Testar
        result = await badge_repo.award_badge("user1", "badge1", {"test": "context"})
        
        assert result is True
        mock_doc_ref.set.assert_called_once()

    @pytest.mark.asyncio
    async def test_award_badge_duplicate(self, badge_repo, mock_db):
        """Testa tentativa de conceder badge duplicado"""
        # Mock - usuário já tem o badge (has_badge retorna True)
        mock_doc = MagicMock()
        
        async def mock_stream_with_doc():
            yield mock_doc
        
        # Configurar a cadeia de mocks
        mock_collection = mock_db.collection.return_value
        mock_collection.where.return_value.where.return_value.limit.return_value.stream.return_value = mock_stream_with_doc()
        
        # Testar
        result = await badge_repo.award_badge("user1", "badge1", {"test": "context"})
        
        assert result is False  # Não deve conceder badge duplicado


class TestValidationService:
    """Testes para o ValidationService"""
    
    @pytest.fixture
    def mock_user_repo(self):
        """Mock do UserRepository"""
        return AsyncMock()
    
    @pytest.fixture
    def mock_badge_repo(self):
        """Mock do BadgeRepository"""
        return AsyncMock()
    
    @pytest.fixture
    def validation_service(self, mock_user_repo, mock_badge_repo):
        """Instância do ValidationService com mocks"""
        return ValidationService(mock_user_repo, mock_badge_repo)

    @pytest.mark.asyncio
    async def test_check_mission_badges_first_mission(self, validation_service, mock_user_repo):
        """Testa verificação de badges para primeira missão"""
        # Mock - usuário sem missões completadas
        mock_user = MagicMock()
        mock_user.completed_missions = {}
        mock_user_repo.get_user_profile.return_value = mock_user
        
        # Mock - streak zero
        validation_service._get_current_streak = AsyncMock(return_value=0)
        
        # Criar evento
        event = MissionCompletedEvent(
            user_id="user1",
            mission_id="mission1",
            score=85.0,
            mission_type="daily"
        )
        
        # Testar
        badges = await validation_service._check_mission_badges("user1", event)
        
        assert "first_steps" in badges

    @pytest.mark.asyncio
    async def test_check_mission_badges_perfect_score(self, validation_service):
        """Testa verificação de badges para score perfeito"""
        # Mock - streak zero
        validation_service._get_current_streak = AsyncMock(return_value=0)
        
        # Criar evento com score perfeito
        event = MissionCompletedEvent(
            user_id="user1",
            mission_id="mission1",
            score=100.0,
            mission_type="daily"
        )
        
        # Testar
        badges = await validation_service._check_mission_badges("user1", event)
        
        assert "perfectionist" in badges

    @pytest.mark.asyncio
    async def test_check_level_badges(self, validation_service):
        """Testa verificação de badges de nível"""
        # Criar evento de level up
        event = LevelUpEvent(
            user_id="user1",
            old_level=4,
            new_level=5,
            points_required=5000,
            points_earned=1000
        )
        
        # Testar
        badges = await validation_service._check_level_badges("user1", event)
        
        assert "level_5" in badges


class TestBadgeEngine:
    """Testes para o BadgeEngine"""
    
    @pytest.fixture
    def mock_validation_service(self):
        """Mock do ValidationService"""
        return AsyncMock()
    
    @pytest.fixture
    def mock_badge_repo(self):
        """Mock do BadgeRepository"""
        return AsyncMock()
    
    @pytest.fixture
    def badge_engine(self, mock_validation_service, mock_badge_repo):
        """Instância do BadgeEngine com mocks"""
        return BadgeEngine(mock_validation_service, mock_badge_repo)

    @pytest.mark.asyncio
    async def test_award_badge_if_eligible_success(self, badge_engine, mock_validation_service, mock_badge_repo):
        """Testa concessão de badge quando elegível"""
        # Mock - usuário não tem o badge ainda
        mock_badge_repo.has_badge.return_value = False
        # Mock - usuário elegível
        mock_validation_service.validate_badge_eligibility.return_value = True
        mock_badge_repo.award_badge.return_value = True
        
        # Testar
        result = await badge_engine._award_badge_if_eligible("user1", "badge1", {"test": "context"})
        
        assert result is True
        mock_badge_repo.has_badge.assert_called_once_with("user1", "badge1")
        mock_validation_service.validate_badge_eligibility.assert_called_once_with("user1", "badge1")
        mock_badge_repo.award_badge.assert_called_once_with("user1", "badge1", {"test": "context"})

    @pytest.mark.asyncio
    async def test_award_badge_if_eligible_not_eligible(self, badge_engine, mock_validation_service, mock_badge_repo):
        """Testa tentativa de concessão quando não elegível"""
        # Mock - usuário não tem o badge ainda
        mock_badge_repo.has_badge.return_value = False
        # Mock - usuário não elegível
        mock_validation_service.validate_badge_eligibility.return_value = False
        
        # Testar
        result = await badge_engine._award_badge_if_eligible("user1", "badge1", {"test": "context"})
        
        assert result is False
        mock_badge_repo.has_badge.assert_called_once_with("user1", "badge1")
        mock_validation_service.validate_badge_eligibility.assert_called_once_with("user1", "badge1")
        mock_badge_repo.award_badge.assert_not_called()

    def test_get_engine_stats(self, badge_engine):
        """Testa estatísticas do BadgeEngine"""
        # Adicionar alguns logs de concessão
        badge_engine._awarded_badges_log = [
            {
                'user_id': 'user1',
                'badge_id': 'badge1',
                'event_type': 'mission_completed',
                'timestamp': datetime.now()
            },
            {
                'user_id': 'user2',
                'badge_id': 'badge2',
                'event_type': 'level_up',
                'timestamp': datetime.now()
            }
        ]
        
        # Testar
        stats = badge_engine.get_engine_stats()
        
        assert stats['total_awards'] == 2
        assert stats['awards_by_event_type']['mission_completed'] == 1
        assert stats['awards_by_event_type']['level_up'] == 1


# Teste de integração
class TestBadgeSystemIntegration:
    """Testes de integração do sistema de badges"""
    
    @pytest.mark.asyncio
    async def test_full_badge_flow(self):
        """Testa fluxo completo de concessão de badge"""
        # Criar instâncias reais (sem mocks para teste de integração)
        event_bus = EventBus()
        
        # Mock dos repositórios
        mock_user_repo = AsyncMock()
        mock_badge_repo = AsyncMock()
        
        # Configurar mocks
        mock_user_repo.get_user_profile.return_value = MagicMock(completed_missions={})
        mock_badge_repo.has_badge.return_value = False
        mock_badge_repo.award_badge.return_value = True
        
        # Criar serviços
        validation_service = ValidationService(mock_user_repo, mock_badge_repo)
        badge_engine = BadgeEngine(validation_service, mock_badge_repo)
        
        # Criar e emitir evento
        event = MissionCompletedEvent(
            user_id="user1",
            mission_id="mission1",
            score=100.0,
            mission_type="daily"
        )
        
        await event_bus.emit(event)
        
        # Verificar se o evento foi processado
        assert len(event_bus._event_log) == 1
        assert event_bus._event_log[0].user_id == "user1"


if __name__ == "__main__":
    # Executar testes
    pytest.main([__file__, "-v"])
