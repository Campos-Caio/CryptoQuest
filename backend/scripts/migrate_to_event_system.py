"""
Script de migração para o sistema de eventos.
Migra dados existentes do sistema legado para o novo sistema de badges.
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timezone

# Adicionar o diretório backend ao path
backend_path = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(backend_path))

from app.core.firebase import get_firestore_db_async
from app.repositories.badge_repository import BadgeRepository
from app.repositories.user_repository import UserRepository
from app.services.event_bus import get_event_bus
from app.models.events import MissionCompletedEvent, LevelUpEvent


async def migrate_user_badges():
    """Migra badges existentes para o novo sistema"""
    print("🔄 Iniciando migração de badges...")
    
    db = await get_firestore_db_async()
    badge_repo = BadgeRepository(db)
    user_repo = UserRepository(db)
    
    # Buscar todos os usuários
    users = await user_repo.get_all_users()
    print(f"📊 Encontrados {len(users)} usuários para migração")
    
    migrated_count = 0
    error_count = 0
    
    for user in users:
        try:
            user_id = user.uid
            
            # Verificar se já tem badges no novo sistema
            existing_badges = await badge_repo.get_user_badges(user_id)
            if existing_badges:
                print(f"⏭️ Usuário {user_id} já tem badges no novo sistema, pulando...")
                continue
            
            # Migrar badges baseados no perfil do usuário
            badges_to_award = []
            
            # Badge de primeira missão
            if user.completed_missions and len(user.completed_missions) > 0:
                badges_to_award.append({
                    'badge_id': 'first_steps',
                    'context': {'migration': True, 'source': 'legacy_system'}
                })
            
            # Badge de level up
            if user.level > 1:
                badges_to_award.append({
                    'badge_id': 'level_up',
                    'context': {'migration': True, 'level': user.level, 'source': 'legacy_system'}
                })
            
            # Badge de nível específico
            if user.level >= 5:
                badges_to_award.append({
                    'badge_id': 'level_5',
                    'context': {'migration': True, 'level': user.level, 'source': 'legacy_system'}
                })
            
            if user.level >= 10:
                badges_to_award.append({
                    'badge_id': 'level_10',
                    'context': {'migration': True, 'level': user.level, 'source': 'legacy_system'}
                })
            
            # Badge de pontos
            if user.points >= 1000:
                badges_to_award.append({
                    'badge_id': 'point_collector',
                    'context': {'migration': True, 'points': user.points, 'source': 'legacy_system'}
                })
            
            if user.points >= 5000:
                badges_to_award.append({
                    'badge_id': 'point_master',
                    'context': {'migration': True, 'points': user.points, 'source': 'legacy_system'}
                })
            
            # Conceder badges
            for badge_data in badges_to_award:
                await badge_repo.award_badge(
                    user_id, 
                    badge_data['badge_id'], 
                    badge_data['context']
                )
            
            if badges_to_award:
                migrated_count += 1
                print(f"✅ Usuário {user_id}: {len(badges_to_award)} badges migrados")
            
        except Exception as e:
            error_count += 1
            print(f"❌ Erro ao migrar usuário {user.uid}: {e}")
    
    print(f"\n📊 Migração concluída:")
    print(f"   ✅ Usuários migrados: {migrated_count}")
    print(f"   ❌ Erros: {error_count}")


async def simulate_legacy_events():
    """Simula eventos baseados em dados existentes"""
    print("\n🔄 Simulando eventos para dados existentes...")
    
    db = await get_firestore_db_async()
    user_repo = UserRepository(db)
    event_bus = get_event_bus()
    
    users = await user_repo.get_all_users()
    events_simulated = 0
    
    for user in users:
        try:
            # Simular eventos de missões completadas
            if user.completed_missions:
                for mission_id, completion_date in user.completed_missions.items():
                    # Criar evento de missão completada
                    mission_event = MissionCompletedEvent(
                        user_id=user.uid,
                        mission_id=mission_id,
                        score=85.0,  # Score padrão para migração
                        mission_type="daily",
                        points_earned=100,
                        xp_earned=50,
                        context={'migration': True, 'source': 'legacy_system'}
                    )
                    
                    # Emitir evento
                    await event_bus.emit(mission_event)
                    events_simulated += 1
            
            # Simular evento de level up
            if user.level > 1:
                level_event = LevelUpEvent(
                    user_id=user.uid,
                    old_level=1,
                    new_level=user.level,
                    points_required=500,
                    points_earned=user.points,
                    context={'migration': True, 'source': 'legacy_system'}
                )
                
                await event_bus.emit(level_event)
                events_simulated += 1
                
        except Exception as e:
            print(f"❌ Erro ao simular eventos para usuário {user.uid}: {e}")
    
    print(f"✅ {events_simulated} eventos simulados")


async def verify_migration():
    """Verifica se a migração foi bem-sucedida"""
    print("\n🔍 Verificando migração...")
    
    db = await get_firestore_db_async()
    badge_repo = BadgeRepository(db)
    user_repo = UserRepository(db)
    
    users = await user_repo.get_all_users()
    total_badges = 0
    
    for user in users:
        badges = await badge_repo.get_user_badges(user.uid)
        total_badges += len(badges)
        
        if badges:
            print(f"👤 {user.uid}: {len(badges)} badges")
            for badge in badges:
                print(f"   🏆 {badge.badge_id}")
    
    print(f"\n📊 Total de badges migrados: {total_badges}")
    
    # Verificar estatísticas do sistema
    stats = badge_repo.get_user_badge_stats(user.uid) if users else {}
    print(f"📈 Estatísticas do sistema: {stats}")


async def main():
    """Função principal de migração"""
    print("🚀 Iniciando migração para o sistema de eventos...")
    print("=" * 60)
    
    try:
        # 1. Migrar badges existentes
        await migrate_user_badges()
        
        # 2. Simular eventos para dados existentes
        await simulate_legacy_events()
        
        # 3. Verificar migração
        await verify_migration()
        
        print("\n✅ Migração concluída com sucesso!")
        print("🎯 O sistema de eventos está pronto para uso!")
        
    except Exception as e:
        print(f"\n❌ Erro durante a migração: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
