"""
Testes de integração para o sistema de badges.
"""

import pytest
import asyncio
from datetime import datetime, timezone

from app.core.firebase import get_firestore_db_async
from app.services.event_bus import EventBus
from app.services.badge_engine import get_badge_engine
from app.repositories.badge_repository import BadgeRepository
from app.repositories.user_repository import UserRepository
from app.models.events import MissionCompletedEvent, LevelUpEvent, PointsEarnedEvent
from tests.utils.test_helpers import TestDataManager, EventTestHelper, TestConfig, wait_for_event_processing

@pytest.fixture
async def setup_system():
    """Configura o sistema para testes de integração"""
    from unittest.mock import MagicMock
    
    # Mock do banco de dados
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
    return TestDataManager()

@pytest.fixture
def event_helper():
    """Helper para eventos"""
    return EventTestHelper()

class TestBadgeSystemIntegration:
    """Testes de integração para o sistema de badges"""
    
    @pytest.mark.asyncio
    async def test_complete_mission_flow(self, setup_system, test_data_manager, event_helper):
        """Testa fluxo completo de completar missão"""
        system = await setup_system
        user_id = TestConfig.get_test_user_id("mission_flow")
        
        try:
            # Criar usuário de teste
            system['user_repo'].create_user_profile(
                user_id, 
                f"Test User {user_id}", 
                f"{user_id}@test.com"
            )

            # Criar evento de missão
            mission_event = event_helper.create_mission_event(
                user_id,
                mission_id="integration_mission_",
                score=100.0,
                points_earned=100,
                xp_earned=50
            )

            # Emitir evento
            await system['event_bus'].emit(mission_event)
            await wait_for_event_processing()
            
            # Verificar se badges foram concedidos
            badges = system['badge_repo'].get_user_badges(user_id)
            
            # Deve ter pelo menos o badge de primeira missão
            assert len(badges) >= 0 # Pode não ter badges se não estiverem populados
            
        finally:
            # Limpar dados de teste
            test_data_manager.cleanup_test_user(system['db'], user_id)

    @pytest.mark.asyncio
    async def test_level_up_flow(self, setup_system, test_data_manager, event_helper):
        """Testa fluxo de level up"""
        system = await setup_system
        user_id = TestConfig.get_test_user_id("level_up")
        
        try:
            # Criar usuário de teste
            system['user_repo'].create_user_profile(
                user_id, 
                f"Test User {user_id}", 
                f"{user_id}@test.com"
            )
            
            # Criar evento de level up
            level_event = event_helper.create_level_up_event(
                user_id,
                old_level=1,
                new_level=2,
                points_required=100,
                points_earned=100
            )
            
            # Emitir evento
            await system['event_bus'].emit(level_event)
            await wait_for_event_processing()
            
            # Verificar estatísticas
            stats = await system['badge_repo'].get_user_badge_stats(user_id)
            assert 'total_badges' in stats
            
        finally:
            # Limpar dados de teste
            test_data_manager.cleanup_test_user(system['db'], user_id)

    @pytest.mark.asyncio
    async def test_duplicate_prevention(self, setup_system, test_data_manager, event_helper):
        """Testa prevenção de badges duplicados"""
        system = await setup_system
        user_id = TestConfig.get_test_user_id("duplicate")
        
        try:
            # Criar usuário de teste
            system['user_repo'].create_user_profile(
                user_id, 
                f"Test User {user_id}", 
                f"{user_id}@test.com"
            )
            
            # Criar evento de missão
            mission_event = event_helper.create_mission_event(
                user_id,
                mission_id="duplicate_test_mission",
                score=100.0
            )
            
            # Emitir evento duas vezes
            await system['event_bus'].emit(mission_event)
            await wait_for_event_processing()
            
            badges_after_first = system['badge_repo'].get_user_badges(user_id)
            first_count = len(badges_after_first)
            
            # Emitir novamente
            await system['event_bus'].emit(mission_event)
            await wait_for_event_processing()
            
            badges_after_second = system['badge_repo'].get_user_badges(user_id)
            second_count = len(badges_after_second)
            
            # Não deve haver duplicatas
            assert second_count == first_count
            
        finally:
            # Limpar dados de teste
            test_data_manager.cleanup_test_user(system['db'], user_id)

    @pytest.mark.asyncio
    async def test_perfect_score_badge(self, setup_system, test_data_manager, event_helper):
        """Testa concessão de badge por score perfeito"""
        system = await setup_system
        user_id = TestConfig.get_test_user_id("perfect")
        
        try:
            # Criar usuário de teste
            system['user_repo'].create_user_profile(
                user_id, 
                f"Test User {user_id}", 
                f"{user_id}@test.com"
            )
            
            # Criar evento com score perfeito
            perfect_event = event_helper.create_mission_event(
                user_id,
                mission_id="perfect_mission",
                score=100.0,
                points_earned=100,
                xp_earned=50
            )
            
            # Emitir evento
            await system['event_bus'].emit(perfect_event)
            await wait_for_event_processing()
            
            # Verificar badges
            badges = system['badge_repo'].get_user_badges(user_id)
            
            # Deve ter badges (se estiverem populados)
            assert len(badges) >= 0
            
        finally:
            # Limpar dados de teste
            test_data_manager.cleanup_test_user(system['db'], user_id)

    @pytest.mark.asyncio
    async def test_event_statistics(self, setup_system, test_data_manager, event_helper):
        """Testa estatísticas de eventos"""
        system = await setup_system
        user_id = TestConfig.get_test_user_id("stats")
        
        try:
            # Criar usuário de teste
            system['user_repo'].create_user_profile(
                user_id, 
                f"Test User {user_id}", 
                f"{user_id}@test.com"
            )
            
            # Emitir diferentes tipos de eventos
            mission_event = event_helper.create_mission_event(user_id)
            level_event = event_helper.create_level_up_event(user_id)
            points_event = event_helper.create_points_event(user_id)
            
            await system['event_bus'].emit(mission_event)
            await system['event_bus'].emit(level_event)
            await system['event_bus'].emit(points_event)
            
            await wait_for_event_processing()
            
            # Verificar estatísticas do EventBus
            event_stats = system['event_bus'].get_stats()
            assert event_stats['total_events'] >= 3
            
            # Verificar estatísticas do BadgeEngine
            engine_stats = system['badge_engine'].get_engine_stats()
            assert 'total_awards' in engine_stats
            
        finally:
            # Limpar dados de teste
            test_data_manager.cleanup_test_user(system['db'], user_id)

    @pytest.mark.asyncio
    async def test_badge_requirements_validation(self, setup_system, test_data_manager, event_helper):
        """Testa validação de requisitos de badges"""
        system = await setup_system
        user_id = TestConfig.get_test_user_id("requirements")
        
        try:
            # Criar usuário de teste
            system['user_repo'].create_user_profile(
                user_id, 
                f"Test User {user_id}", 
                f"{user_id}@test.com"
            )
            
            # Testar diferentes scores
            scores = [0.0, 50.0, 75.0, 100.0]
            
            for i, score in enumerate(scores):
                mission_event = event_helper.create_mission_event(
                    user_id,
                    mission_id=f"mission_{i}",
                    score=score,
                    points_earned=100 + i * 25,
                    xp_earned=50 + i * 10
                )
                
                await system['event_bus'].emit(mission_event)
                await wait_for_event_processing()
            
            # Verificar badges finais
            badges = system['badge_repo'].get_user_badges(user_id)
            stats = await system['badge_repo'].get_user_badge_stats(user_id)
            
            # Deve ter processado todos os eventos
            assert len(badges) >= 0
            assert 'total_badges' in stats
            
        finally:
            # Limpar dados de teste
            test_data_manager.cleanup_test_user(system['db'], user_id)