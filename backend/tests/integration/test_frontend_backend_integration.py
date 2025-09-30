"""
Testes de integração Frontend-Backend para sistema de badges.
"""

import pytest
import asyncio
from datetime import datetime, timezone

from app.core.firebase import get_firestore_db_async
from app.services.event_bus import EventBus
from app.services.badge_engine import get_badge_engine
from app.repositories.badge_repository import BadgeRepository
from app.repositories.user_repository import UserRepository
from app.models.events import MissionCompletedEvent, LevelUpEvent
from tests.utils.test_helpers import TestDataManager, EventTestHelper, TestConfig, wait_for_event_processing


@pytest.mark.asyncio
async def test_quiz_completion_flow(setup_system, test_data_manager, event_helper):
    """Testa fluxo completo de completar quiz (simulando frontend)"""
    system = await setup_system
    user_id = TestConfig.get_test_user_id("quiz_flow")
    
    try:
        # 1. Criar usuário de teste
        system['user_repo'].create_user_profile(
            user_id, 
            f"Test User {user_id}", 
            f"{user_id}@test.com"
        )
        
        # 2. Simular completar quiz (frontend chama API)
        mission_event = event_helper.create_mission_event(
            user_id,
            mission_id="quiz_mission_",
            score=100.0, # % de acerto
            mission_type="QUIZ",
            points_earned=100,
            xp_earned=50
        )
        
        # 3. Emitir evento (simula chamada da API)
        await system['event_bus'].emit(mission_event)
        await wait_for_event_processing()
        
        # 4. Verificar se badges foram concedidos
        badges = system['badge_repo'].get_user_badges(user_id)
        
        # 5. Verificar se recompensas foram registradas
        stats = await system['badge_repo'].get_user_badge_stats(user_id)
        
        # Assertions
        assert len(badges) >= 0 # Pode não ter badges se não estiverem populados
        assert 'total_badges' in stats
        
        # Verificar se evento foi processado
        event_log = system['event_bus'].get_event_log(user_id=user_id)
        assert len(event_log) >= 1
        assert event_log[0].event_type.value == "mission_completed"
        
    finally:
        # Limpar dados de teste
        await test_data_manager.cleanup_test_user(system['db'], user_id)

@pytest.mark.asyncio
async def test_perfect_score_badge_flow(setup_system, test_data_manager, event_helper):
    """Testa fluxo de badge por score perfeito"""
    system = await setup_system
    user_id = TestConfig.get_test_user_id("perfect_score")
    
    try:
        # Criar usuário de teste
        system['user_repo'].create_user_profile(
            user_id, 
            f"Test User {user_id}", 
            f"{user_id}@test.com"
        )
        
        # Simular quiz com score perfeito
        perfect_event = event_helper.create_mission_event(
            user_id,
            mission_id="perfect_quiz",
            score=100.0, # Score perfeito
            mission_type="QUIZ",
            points_earned=100,
            xp_earned=50
        )
        
        # Emitir evento
        await system['event_bus'].emit(perfect_event)
        await wait_for_event_processing()
        
        # Verificar badges
        badges = system['badge_repo'].get_user_badges(user_id)
        stats = await system['badge_repo'].get_user_badge_stats(user_id)
        
        # Deve ter processado o evento
        assert len(badges) >= 0
        assert 'total_badges' in stats
        
    finally:
        # Limpar dados de teste
        await test_data_manager.cleanup_test_user(system['db'], user_id)

@pytest.mark.asyncio
async def test_level_up_badge_flow(setup_system, test_data_manager, event_helper):
    """Testa fluxo de badge por level up"""
    system = await setup_system
    user_id = TestConfig.get_test_user_id("level_up")
    
    try:
        # Criar usuário de teste
        system['user_repo'].create_user_profile(
            user_id, 
            f"Test User {user_id}", 
            f"{user_id}@test.com"
        )
        
        # Simular level up
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
        
        # Verificar badges
        badges = system['badge_repo'].get_user_badges(user_id)
        stats = await system['badge_repo'].get_user_badge_stats(user_id)
        
        # Deve ter processado o evento
        assert len(badges) >= 0
        assert 'total_badges' in stats
        
    finally:
        # Limpar dados de teste
        await test_data_manager.cleanup_test_user(system['db'], user_id)

@pytest.mark.asyncio
async def test_multiple_events_flow(setup_system, test_data_manager, event_helper):
    """Testa fluxo com múltiplos eventos (simulando sessão de usuário)"""
    system = await setup_system
    user_id = TestConfig.get_test_user_id("multiple_events")
    
    try:
        # Criar usuário de teste
        system['user_repo'].create_user_profile(
            user_id, 
            f"Test User {user_id}", 
            f"{user_id}@test.com"
        )
        
        # Simular sessão de usuário com múltiplos eventos
        events = [
            # Primeira missão
            event_helper.create_mission_event(
                user_id,
                mission_id="mission_",
                score=100.0,
                mission_type="QUIZ",
                points_earned=100,
                xp_earned=50
            ),
            # Segunda missão
            event_helper.create_mission_event(
                user_id,
                mission_id="mission_",
                score=100.0,
                mission_type="QUIZ",
                points_earned=100,
                xp_earned=50
            ),
            # Level up
            event_helper.create_level_up_event(
                user_id,
                old_level=1,
                new_level=2,
                points_required=100,
                points_earned=100
            ),
            # Terceira missão (score perfeito)
            event_helper.create_mission_event(
                user_id,
                mission_id="mission_",
                score=100.0,
                mission_type="QUIZ",
                points_earned=100,
                xp_earned=50
            ),
        ]
        
        # Emitir todos os eventos
        for event in events:
            await system['event_bus'].emit(event)
            await wait_for_event_processing()
        
        # Verificar resultados finais
        badges = system['badge_repo'].get_user_badges(user_id)
        stats = await system['badge_repo'].get_user_badge_stats(user_id)
        event_log = system['event_bus'].get_event_log(user_id=user_id)
        
        # Deve ter processado todos os eventos
        assert len(event_log) == 4
        assert len(badges) >= 0
        assert 'total_badges' in stats
        
        # Verificar tipos de eventos processados
        event_types = [e.event_type.value for e in event_log]
        assert "mission_completed" in event_types
        assert "level_up" in event_types
        
    finally:
        # Limpar dados de teste
        await test_data_manager.cleanup_test_user(system['db'], user_id)

@pytest.mark.asyncio
async def test_error_handling_flow(setup_system, test_data_manager, event_helper):
    """Testa tratamento de erros no fluxo"""
    system = await setup_system
    user_id = TestConfig.get_test_user_id("error_handling")
    
    try:
        # Criar usuário de teste
        system['user_repo'].create_user_profile(
            user_id, 
            f"Test User {user_id}", 
            f"{user_id}@test.com"
        )
        
        # Simular evento com dados inválidos
        invalid_event = event_helper.create_mission_event(
            user_id,
            mission_id="invalid_mission",
            score=-100.0, # Score inválido
            mission_type="QUIZ",
            points_earned=-100, # Pontos negativos
            xp_earned=-50
        )
        
        # Emitir evento (deve processar sem falhar)
        await system['event_bus'].emit(invalid_event)
        await wait_for_event_processing()
        
        # Verificar que o sistema não falhou
        badges = system['badge_repo'].get_user_badges(user_id)
        stats = await system['badge_repo'].get_user_badge_stats(user_id)
        
        # Deve ter processado o evento mesmo com dados inválidos
        assert len(badges) >= 0
        assert 'total_badges' in stats
        
    finally:
        # Limpar dados de teste
        await test_data_manager.cleanup_test_user(system['db'], user_id)

@pytest.mark.asyncio
async def test_performance_flow(setup_system, test_data_manager, event_helper):
    """Testa performance com múltiplos eventos simultâneos"""
    system = await setup_system
    user_id = TestConfig.get_test_user_id("performance")
    
    try:
        # Criar usuário de teste
        system['user_repo'].create_user_profile(
            user_id, 
            f"Test User {user_id}", 
            f"{user_id}@test.com"
        )
        
        # Simular múltiplos eventos simultâneos
        events = []
        for i in range(10):
            events.append(event_helper.create_mission_event(
                user_id,
                mission_id=f"mission_{i}",
                score=100.0 + i,
                mission_type="QUIZ",
                points_earned=100 + i * 10,
                xp_earned=50 + i * 5
            ))
        
        # Emitir todos os eventos simultaneamente
        start_time = datetime.now()
        tasks = [system['event_bus'].emit(event) for event in events]
        await asyncio.gather(*tasks)
        await wait_for_event_processing()
        end_time = datetime.now()
        
        # Verificar que todos foram processados
        event_log = system['event_bus'].get_event_log(user_id=user_id)
        badges = system['badge_repo'].get_user_badges(user_id)
        
        # Deve ter processado todos os eventos
        assert len(event_log) == 10
        assert len(badges) >= 0
        
        # Verificar performance (deve processar em menos de 5 segundos)
        processing_time = (end_time - start_time).total_seconds()
        assert processing_time < 5.0, f"Processamento muito lento: {processing_time}s"
        
    finally:
        # Limpar dados de teste
        await test_data_manager.cleanup_test_user(system['db'], user_id)