"""
Script para popular o banco de dados Firestore com badges
para o sistema CryptoQuest.

Uso:
    python populate_badges.py [--clear-existing]
"""

import sys
import os
import argparse
from pathlib import Path
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

def _configure_credentials():
    """
    Configura as credenciais para o ambiente, usando a mesma lógica do projeto.
    """
    # Procura pela variável de ambiente (usada na Render)
    creds_json_str = os.getenv("FIREBASE_CREDENTIALS_JSON")
    
    if creds_json_str:
        # Na Render, escreve o conteúdo da variável em um arquivo temporário
        temp_credentials_path = "/tmp/firebase_credentials.json"
        with open(temp_credentials_path, "w") as f:
            f.write(creds_json_str)
        # Define a variável de ambiente padrão que a biblioteca do Google procura
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_credentials_path
        print("✅ Credenciais configuradas a partir da variável de ambiente.")
    else:
        # Localmente, aponta para o arquivo .json na raiz do backend
        print("🔧 Configurando credenciais a partir de arquivo local...")
        cred_path = Path(__file__).resolve().parents[1] / "firebase_key.json"
        if not cred_path.exists():
            raise FileNotFoundError(f"Arquivo de credenciais não encontrado: {cred_path}")
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(cred_path)
        print("✅ Credenciais configuradas a partir do arquivo local.")

def initialize_firebase():
    """Inicializa o Firebase Admin SDK usando a mesma lógica do projeto"""
    if not firebase_admin._apps:
        try:
            print("🚀 Inicializando Firebase App...")
            # O firebase_admin agora usa as credenciais padrão do ambiente
            firebase_admin.initialize_app()
            print("✅ Firebase inicializado com sucesso!")
        except Exception as e:
            print(f"❌ ERRO CRÍTICO AO INICIALIZAR FIREBASE: {e}")
            raise e

def clear_collection(db, collection_name):
    """Limpa uma coleção inteira (CUIDADO!)"""
    print(f"🗑️  Limpando coleção '{collection_name}'...")
    docs = db.collection(collection_name).stream()
    deleted_count = 0
    for doc in docs:
        doc.reference.delete()
        deleted_count += 1
    print(f"✅ {deleted_count} documentos deletados da coleção '{collection_name}'")

def create_badges_data():
    """Cria os dados dos badges"""
    return {
        # Badges de Streak
        "streak_7": {
            "name": "Streak de 7 dias",
            "description": "Complete missões por 7 dias consecutivos",
            "icon": "🔥",
            "rarity": "common",
            "color": "#FF6B35",
            "category": "streak",
            "requirements": {
                "type": "streak",
                "value": 7
            }
        },
        "streak_30": {
            "name": "Streak de 30 dias",
            "description": "Complete missões por 30 dias consecutivos",
            "icon": "🏆",
            "rarity": "rare",
            "color": "#FFD700",
            "category": "streak",
            "requirements": {
                "type": "streak",
                "value": 30
            }
        },
        
        # Badges de Performance
        "perfectionist": {
            "name": "Perfeccionista",
            "description": "Acerte 100% em uma missão",
            "icon": "💯",
            "rarity": "uncommon",
            "color": "#00FF00",
            "category": "performance",
            "requirements": {
                "type": "perfect_score",
                "value": 100
            }
        },
        "first_steps": {
            "name": "Primeiros Passos",
            "description": "Complete sua primeira missão",
            "icon": "👶",
            "rarity": "common",
            "color": "#87CEEB",
            "category": "milestone",
            "requirements": {
                "type": "first_completion",
                "value": 1
            }
        },
        
        # Badges de Nível
        "level_up": {
            "name": "Subiu de Nível",
            "description": "Alcance um novo nível",
            "icon": "⬆️",
            "rarity": "common",
            "color": "#9370DB",
            "category": "level",
            "requirements": {
                "type": "level_up",
                "value": 1
            }
        },
        "level_5": {
            "name": "Nível 5",
            "description": "Alcance o nível 5",
            "icon": "⭐",
            "rarity": "uncommon",
            "color": "#FFA500",
            "category": "level",
            "requirements": {
                "type": "level",
                "value": 5
            }
        },
        "level_10": {
            "name": "Nível 10",
            "description": "Alcance o nível 10",
            "icon": "🌟",
            "rarity": "rare",
            "color": "#FF69B4",
            "category": "level",
            "requirements": {
                "type": "level",
                "value": 10
            }
        },
        
        # Badges de Trilhas
        "path_complete": {
            "name": "Trilha Completa",
            "description": "Complete uma trilha de aprendizado",
            "icon": "🎓",
            "rarity": "uncommon",
            "color": "#32CD32",
            "category": "learning",
            "requirements": {
                "type": "path_complete",
                "value": 1
            }
        },
        "crypto_expert": {
            "name": "Especialista em Crypto",
            "description": "Complete 5 trilhas de aprendizado",
            "icon": "🚀",
            "rarity": "epic",
            "color": "#FF1493",
            "category": "learning",
            "requirements": {
                "type": "paths_completed",
                "value": 5
            }
        },
        
        # Badges de Pontuação
        "point_collector": {
            "name": "Colecionador de Pontos",
            "description": "Acumule 1000 pontos",
            "icon": "💰",
            "rarity": "uncommon",
            "color": "#FFD700",
            "category": "points",
            "requirements": {
                "type": "points",
                "value": 1000
            }
        },
        "point_master": {
            "name": "Mestre dos Pontos",
            "description": "Acumule 5000 pontos",
            "icon": "💎",
            "rarity": "rare",
            "color": "#C0C0C0",
            "category": "points",
            "requirements": {
                "type": "points",
                "value": 5000
            }
        }
    }

def upsert_badges(db, badges_data, clear_first=False):
    """Insere ou atualiza badges na coleção"""
    if clear_first:
        clear_collection(db, "badges")
    
    print(f"📝 Populando coleção 'badges'...")
    success_count = 0
    error_count = 0
    
    for badge_id, data in badges_data.items():
        try:
            # Adiciona timestamp de criação/atualização
            data['created_at'] = datetime.now()
            data['updated_at'] = datetime.now()
            data['id'] = badge_id  # Adiciona o ID como campo
            
            db.collection("badges").document(badge_id).set(data, merge=True)
            print(f"  ✅ badges/{badge_id} - {data['name']}")
            success_count += 1
        except Exception as e:
            print(f"  ❌ Erro ao criar badges/{badge_id}: {e}")
            error_count += 1
    
    print(f"📊 badges: {success_count} sucessos, {error_count} erros")
    return success_count, error_count

def main():
    parser = argparse.ArgumentParser(description='Popula o banco de dados com badges')
    parser.add_argument('--clear-existing', action='store_true',
                       help='Limpa a coleção existente antes de popular')
    
    args = parser.parse_args()
    
    # Verificar se o arquivo firebase_key.json existe
    firebase_key_path = Path(__file__).resolve().parents[1] / "firebase_key.json"
    if not firebase_key_path.exists():
        print(f"❌ Arquivo firebase_key.json não encontrado em: {firebase_key_path}")
        print("💡 Certifique-se de que o arquivo existe na pasta backend/")
        sys.exit(1)
    
    # Configurar credenciais e inicializar Firebase
    try:
        _configure_credentials()
        initialize_firebase()
        db = firestore.client()
    except Exception as e:
        print(f"❌ Erro ao configurar Firebase: {e}")
        print("💡 Verifique se o arquivo firebase_key.json está correto")
        sys.exit(1)
    
    # Criar dados dos badges
    badges_data = create_badges_data()
    
    # Popular coleção de badges
    success, errors = upsert_badges(db, badges_data, args.clear_existing)
    
    # Resumo final
    print("\n" + "="*50)
    print("📊 RESUMO DA OPERAÇÃO")
    print("="*50)
    print(f"✅ Badges criados/atualizados: {success}")
    print(f"❌ Erros: {errors}")
    
    if errors == 0:
        print("🎉 População de badges concluída com sucesso!")
        print("\n💡 Próximos passos:")
        print("   1. Teste o sistema completando missões")
        print("   2. Verifique se os badges aparecem nas recompensas")
        print("   3. Confirme se o sistema de recompensas está funcionando")
    else:
        print("⚠️  Alguns erros ocorreram. Verifique os logs acima.")

if __name__ == "__main__":
    main()
