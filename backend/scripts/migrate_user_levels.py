#!/usr/bin/env python3
"""
Script para migrar usuários existentes para o novo sistema de níveis rebalanceado.

Este script recalcula os níveis de todos os usuários baseado no novo sistema de XP.
"""

import sys
import os
import asyncio
import logging
from typing import Dict, Any

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.repositories.user_repository import UserRepository
from app.core.firebase import get_firestore_db
from app.services.mission_service import LEVEL_UP_REQUIREMENTS

logger = logging.getLogger(__name__)

def calculate_level_from_xp(total_xp: int) -> int:
    """Calcula o nível baseado no XP total usando o novo sistema"""
    level = 1
    
    for required_level, required_xp in LEVEL_UP_REQUIREMENTS.items():
        if total_xp >= required_xp:
            level = required_level
        else:
            break
    
    return level

def migrate_user_levels():
    """Migra todos os usuários para o novo sistema de níveis"""
    try:
        # Inicializar serviços
        db = get_firestore_db()
        user_repo = UserRepository(db)
        
        print("🔄 Iniciando migração do sistema de níveis...")
        
        # Buscar todos os usuários
        users = user_repo.get_all_users()
        print(f"📊 Encontrados {len(users)} usuários para migrar")
        
        migrated_count = 0
        errors_count = 0
        
        for user in users:
            try:
                user_id = user.uid
                current_xp = user.xp or 0
                current_level = user.level or 1
                
                # Calcular novo nível
                new_level = calculate_level_from_xp(current_xp)
                
                # Se o nível mudou, atualizar
                if new_level != current_level:
                    user_repo.update_user_profile(user_id, {
                        'level': new_level
                    })
                    
                    print(f"✅ Usuário {user_id}: Nível {current_level} → {new_level} (XP: {current_xp})")
                    migrated_count += 1
                else:
                    print(f"⏭️  Usuário {user_id}: Nível {current_level} mantido (XP: {current_xp})")
                    
            except Exception as e:
                print(f"❌ Erro ao migrar usuário {getattr(user, 'uid', 'unknown')}: {e}")
                errors_count += 1
        
        print(f"\n🎉 Migração concluída!")
        print(f"✅ Usuários migrados: {migrated_count}")
        print(f"❌ Erros: {errors_count}")
        print(f"📊 Total processado: {len(users)}")
        
    except Exception as e:
        print(f"❌ Erro fatal na migração: {e}")
        raise

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    
    print("🚀 Script de Migração do Sistema de Níveis")
    print("=" * 50)
    
    # Executar migração
    migrate_user_levels()
