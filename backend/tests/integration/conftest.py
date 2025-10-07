"""
Fixtures específicas para testes de integração.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock

@pytest.fixture
async def setup_system():
    """Configura o sistema para testes de integração"""
    from app.services.event_bus import EventBus
    from app.services.badge_engine import get_badge_engine
    from app.repositories.badge_repository import BadgeRepository
    from app.repositories.user_repository import UserRepository
    
    # Criar mock do banco de dados
    mock_db = MagicMock()
    
    # Inicializar componentes
    event_bus = EventBus()
    badge_engine = get_badge_engine()
    badge_repo = BadgeRepository(mock_db)
    user_repo = UserRepository(mock_db)
    
    # Registrar handlers
    await badge_engine._register_event_handlers()
    
    return {
        'db': mock_db,
        'event_bus': event_bus,
        'badge_engine': badge_engine,
        'badge_repo': badge_repo,
        'user_repo': user_repo
    }

@pytest.fixture
def test_data_manager():
    """Gerenciador de dados de teste"""
    from tests.utils.test_helpers import TestDataManager
    return TestDataManager()

@pytest.fixture
def event_helper():
    """Helper para eventos"""
    from tests.utils.test_helpers import EventTestHelper
    return EventTestHelper()
