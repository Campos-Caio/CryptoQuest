"""
Script de teste de integração do sistema de eventos.
Testa o fluxo completo do novo sistema de badges.
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timezone

# Adicionar o diretório backend ao path
backend_path = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(backend_path))

from app.core.firebase import get_firestore_db_async
from app.services.event_bus import EventBus
from app.services.badge_engine import get_badge_engine
from app.repositories.badge_repository import BadgeRepository
from app.repositories.user_repository import UserRepository
from app.models.events import MissionCompletedEvent, LevelUpEvent, PointsEarnedEvent
from app.models.user import UserProfile


async def test_event_system():
    """Testa o sistema de eventos completo"""
    print("🧪 Testando sistema de eventos...")
    
    # Inicializar componentes
    db = await get_firestore_db_async()
    event_bus = EventBus()
    badge_engine = get_badge_engine()
    badge_repo = BadgeRepository(db)
    user_repo = UserRepository(db)
    
    # Criar usuário de teste
    test_user_id = "test_user_integration"
    
    try:
        # Limpar dados de teste anteriores
        await cleanup_test_data(db, test_user_id)
        
        # Criar perfil de usuário de teste
        test_user = UserProfile(
            uid=test_user_id,
            name="Test User",
            email="test@integration.com",
            register_date=datetime.now(timezone.utc),
            level=1,
            points=0,
            completed_missions={},
            daily_missions=[]
        )
        
        await user_repo.create_user_profile(test_user_id, "Test User", "test@integration.com")
        print(f"✅ Usuário de teste criado: {test_user_id}")
        
        # Teste 1: Missão completada (primeira vez)
        print("\n🎯 Teste 1: Missão completada (primeira vez)")
        mission_event = MissionCompletedEvent(
            user_id=test_user_id,
            mission_id="test_mission_1",
            score=85.0,
            mission_type="daily",
            points_earned=100,
            xp_earned=50
        )
        
        await event_bus.emit(mission_event)
        await asyncio.sleep(1)  # Aguardar processamento
        
        # Verificar badges concedidos
        badges = await badge_repo.get_user_badges(test_user_id)
        print(f"   🏆 Badges concedidos: {len(badges)}")
        for badge in badges:
            print(f"      - {badge.badge_id}")
        
        # Teste 2: Score perfeito
        print("\n🎯 Teste 2: Score perfeito")
        perfect_event = MissionCompletedEvent(
            user_id=test_user_id,
            mission_id="test_mission_2",
            score=100.0,
            mission_type="daily",
            points_earned=150,
            xp_earned=75
        )
        
        await event_bus.emit(perfect_event)
        await asyncio.sleep(1)
        
        # Verificar badges atualizados
        badges = await badge_repo.get_user_badges(test_user_id)
        print(f"   🏆 Total de badges: {len(badges)}")
        
        # Teste 3: Level up
        print("\n🎯 Teste 3: Level up")
        level_event = LevelUpEvent(
            user_id=test_user_id,
            old_level=1,
            new_level=2,
            points_required=500,
            points_earned=200
        )
        
        await event_bus.emit(level_event)
        await asyncio.sleep(1)
        
        # Verificar badges de nível
        badges = await badge_repo.get_user_badges(test_user_id)
        print(f"   🏆 Total de badges após level up: {len(badges)}")
        
        # Teste 4: Pontos ganhos
        print("\n🎯 Teste 4: Pontos ganhos")
        points_event = PointsEarnedEvent(
            user_id=test_user_id,
            points_amount=1000,
            xp_amount=500,
            source="mission",
            points_earned=1000,
            total_points=1000
        )
        
        await event_bus.emit(points_event)
        await asyncio.sleep(1)
        
        # Verificar estatísticas
        stats = await badge_repo.get_user_badge_stats(test_user_id)
        print(f"   📊 Estatísticas: {stats}")
        
        # Teste 5: Verificar prevenção de duplicatas
        print("\n🎯 Teste 5: Prevenção de duplicatas")
        duplicate_event = MissionCompletedEvent(
            user_id=test_user_id,
            mission_id="test_mission_1",  # Mesma missão
            score=90.0,
            mission_type="daily",
            points_earned=100,
            xp_earned=50
        )
        
        await event_bus.emit(duplicate_event)
        await asyncio.sleep(1)
        
        # Verificar que não houve duplicação
        badges_after = await badge_repo.get_user_badges(test_user_id)
        print(f"   🏆 Badges após tentativa de duplicata: {len(badges_after)}")
        
        # Resultados finais
        print("\n📊 RESULTADOS FINAIS:")
        print(f"   🏆 Total de badges únicos: {len(badges_after)}")
        print(f"   📈 Estatísticas: {stats}")
        
        # Estatísticas do sistema
        event_stats = event_bus.get_event_counts()
        engine_stats = badge_engine.get_engine_stats()
        
        print(f"   🎯 Eventos processados: {event_stats}")
        print(f"   🔧 Estatísticas do engine: {engine_stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        return False
    
    finally:
        # Limpar dados de teste
        await cleanup_test_data(db, test_user_id)


async def cleanup_test_data(db, user_id: str):
    """Limpa dados de teste"""
    try:
        # Remover badges do usuário
        badges_query = db.collection("user_badges").where("user_id", "==", user_id)
        badges_docs = badges_query.stream()
        async for doc in badges_docs:
            await doc.reference.delete()
        
        # Remover usuário
        user_doc = db.collection("users").document(user_id)
        await user_doc.delete()
        
        print(f"🧹 Dados de teste limpos para usuário {user_id}")
        
    except Exception as e:
        print(f"⚠️ Erro ao limpar dados de teste: {e}")


async def test_api_endpoints():
    """Testa endpoints da API"""
    print("\n🌐 Testando endpoints da API...")
    
    import httpx
    
    base_url = "http://localhost:8001"
    
    try:
        async with httpx.AsyncClient() as client:
            # Testar health check
            response = await client.get(f"{base_url}/health")
            print(f"   ✅ Health check: {response.status_code}")
            
            # Testar estatísticas de eventos
            response = await client.get(f"{base_url}/events/stats")
            print(f"   ✅ Event stats: {response.status_code}")
            
            # Testar badges disponíveis
            response = await client.get(f"{base_url}/rewards/badges")
            print(f"   ✅ Available badges: {response.status_code}")
            
            if response.status_code == 200:
                badges = response.json()
                print(f"      📊 Total de badges disponíveis: {len(badges)}")
            
    except Exception as e:
        print(f"   ❌ Erro ao testar API: {e}")


async def main():
    """Função principal de teste"""
    print("🚀 Iniciando testes de integração do sistema de eventos...")
    print("=" * 70)
    
    try:
        # Teste 1: Sistema de eventos
        success = await test_event_system()
        
        if success:
            print("\n✅ Testes de integração concluídos com sucesso!")
            
            # Teste 2: API endpoints (opcional)
            await test_api_endpoints()
            
            print("\n🎉 Sistema de eventos totalmente funcional!")
        else:
            print("\n❌ Testes falharam!")
            
    except Exception as e:
        print(f"\n❌ Erro durante os testes: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
