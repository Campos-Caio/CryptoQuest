"""
Script para criar badges específicos para trilhas de aprendizado.
"""

import sys
from pathlib import Path
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# Adicionar o diretório pai ao path para importar os módulos
sys.path.append(str(Path(__file__).resolve().parents[1]))

def _configure_credentials():
    """Configura as credenciais para o ambiente"""
    import os
    creds_json_str = os.getenv("FIREBASE_CREDENTIALS_JSON")
    
    if creds_json_str:
        temp_credentials_path = "/tmp/firebase_credentials.json"
        with open(temp_credentials_path, "w") as f:
            f.write(creds_json_str)
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_credentials_path
        print("✅ Credenciais configuradas a partir da variável de ambiente.")
    else:
        print("🔧 Configurando credenciais a partir de arquivo local...")
        cred_path = Path(__file__).resolve().parents[1] / "firebase_key.json"
        if not cred_path.exists():
            raise FileNotFoundError(f"Arquivo de credenciais não encontrado: {cred_path}")
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(cred_path)
        print("✅ Credenciais configuradas a partir do arquivo local.")

def initialize_firebase():
    """Inicializa o Firebase Admin SDK"""
    if not firebase_admin._apps:
        try:
            print("🚀 Inicializando Firebase App...")
            firebase_admin.initialize_app()
            print("✅ Firebase inicializado com sucesso!")
        except Exception as e:
            print(f"❌ Erro ao inicializar Firebase: {e}")
            sys.exit(1)

def get_learning_path_badges():
    """Retorna os badges específicos para trilhas de aprendizado"""
    return [
        # Badges por trilha completada
        {
            "id": "fundamentos_bitcoin_master",
            "name": "Mestre dos Fundamentos",
            "description": "Completou a trilha 'Fundamentos de Dinheiro e Bitcoin'",
            "icon": "🎓",
            "rarity": "common",
            "color": "#4CAF50",
            "requirements": {
                "type": "learning_path_completed",
                "learning_path_id": "fundamentos_dinheiro_bitcoin"
            }
        },
        {
            "id": "bitcoin_tech_expert",
            "name": "Especialista em Bitcoin",
            "description": "Completou a trilha 'Aprofundando no Bitcoin'",
            "icon": "⚡",
            "rarity": "rare",
            "color": "#FF9800",
            "requirements": {
                "type": "learning_path_completed",
                "learning_path_id": "aprofundando_bitcoin_tecnologia"
            }
        },
        {
            "id": "bitcoin_ecosystem_master",
            "name": "Mestre do Ecossistema Bitcoin",
            "description": "Completou a trilha 'Bitcoin no Ecossistema Financeiro'",
            "icon": "🏆",
            "rarity": "epic",
            "color": "#9C27B0",
            "requirements": {
                "type": "learning_path_completed",
                "learning_path_id": "bitcoin_ecossistema_financeiro"
            }
        },
        
        # Badges por módulos completados
        {
            "id": "first_module_completed",
            "name": "Primeiro Passo",
            "description": "Completou seu primeiro módulo de trilha",
            "icon": "👶",
            "rarity": "common",
            "color": "#2196F3",
            "requirements": {
                "type": "modules_completed",
                "count": 1
            }
        },
        {
            "id": "module_explorer",
            "name": "Explorador de Módulos",
            "description": "Completou 5 módulos de trilhas",
            "icon": "🗺️",
            "rarity": "uncommon",
            "color": "#00BCD4",
            "requirements": {
                "type": "modules_completed",
                "count": 5
            }
        },
        {
            "id": "module_master",
            "name": "Mestre dos Módulos",
            "description": "Completou 10 módulos de trilhas",
            "icon": "🎯",
            "rarity": "rare",
            "color": "#FF5722",
            "requirements": {
                "type": "modules_completed",
                "count": 10
            }
        },
        
        # Badges por trilhas completadas
        {
            "id": "learning_path_beginner",
            "name": "Iniciante das Trilhas",
            "description": "Completou sua primeira trilha de aprendizado",
            "icon": "🌱",
            "rarity": "common",
            "color": "#4CAF50",
            "requirements": {
                "type": "learning_paths_completed",
                "count": 1
            }
        },
        {
            "id": "learning_path_enthusiast",
            "name": "Entusiasta das Trilhas",
            "description": "Completou 2 trilhas de aprendizado",
            "icon": "🔥",
            "rarity": "uncommon",
            "color": "#FF9800",
            "requirements": {
                "type": "learning_paths_completed",
                "count": 2
            }
        },
        {
            "id": "learning_path_master",
            "name": "Mestre das Trilhas",
            "description": "Completou todas as trilhas de aprendizado",
            "icon": "👑",
            "rarity": "legendary",
            "color": "#FFD700",
            "requirements": {
                "type": "learning_paths_completed",
                "count": 3
            }
        },
        
        # Badges por pontuação em quizzes
        {
            "id": "perfect_quiz_score",
            "name": "Perfeição Absoluta",
            "description": "Acertou 100% em um quiz de trilha",
            "icon": "💯",
            "rarity": "rare",
            "color": "#E91E63",
            "requirements": {
                "type": "perfect_quiz_score",
                "score": 100
            }
        },
        {
            "id": "excellent_quiz_score",
            "name": "Excelência em Quizzes",
            "description": "Acertou 90% ou mais em 5 quizzes de trilhas",
            "icon": "⭐",
            "rarity": "uncommon",
            "color": "#FFC107",
            "requirements": {
                "type": "excellent_quiz_scores",
                "count": 5,
                "min_score": 90
            }
        },
        
        # Badges especiais
        {
            "id": "bitcoin_curious",
            "name": "Curioso do Bitcoin",
            "description": "Iniciou sua jornada de aprendizado sobre Bitcoin",
            "icon": "🤔",
            "rarity": "common",
            "color": "#607D8B",
            "requirements": {
                "type": "questionnaire_completed",
                "profile": "Explorador Curioso"
            }
        },
        {
            "id": "bitcoin_promising",
            "name": "Promissor do Bitcoin",
            "description": "Mostrou conhecimento promissor sobre Bitcoin",
            "icon": "🚀",
            "rarity": "uncommon",
            "color": "#3F51B5",
            "requirements": {
                "type": "questionnaire_completed",
                "profile": "Iniciante Promissor"
            }
        },
        {
            "id": "bitcoin_enthusiast",
            "name": "Entusiasta do Bitcoin",
            "description": "Demonstrou conhecimento avançado sobre Bitcoin",
            "icon": "💎",
            "rarity": "rare",
            "color": "#673AB7",
            "requirements": {
                "type": "questionnaire_completed",
                "profile": "Entusiasta Preparado"
            }
        }
    ]

def create_learning_path_badges():
    """Cria os badges das trilhas no Firestore"""
    try:
        db = firestore.client()
        badges_collection = db.collection('badges')
        
        badges_data = get_learning_path_badges()
        
        print(f"🏆 Criando {len(badges_data)} badges para trilhas de aprendizado...")
        
        for badge_data in badges_data:
            badge_id = badge_data['id']
            print(f"  🎖️ Criando badge: {badge_id}")
            
            try:
                # Preparar dados para Firestore (remover id do payload)
                firestore_data = badge_data.copy()
                firestore_data.pop('id', None)
                
                # Adicionar timestamp de criação
                firestore_data['created_at'] = datetime.utcnow()
                firestore_data['is_active'] = True
                
                # Salvar no Firestore
                badges_collection.document(badge_id).set(firestore_data)
                print(f"    ✅ Badge '{badge_id}' criado com sucesso!")
                print(f"    🎯 Nome: {badge_data['name']}")
                print(f"    🎨 Raridade: {badge_data['rarity']}")
                
            except Exception as e:
                print(f"    ❌ Erro ao criar badge '{badge_id}': {e}")
                continue
        
        print(f"🎉 Processo de criação concluído!")
        print(f"📈 Total de badges criados: {len(badges_data)}")
        
    except Exception as e:
        print(f"❌ Erro ao criar badges: {e}")
        sys.exit(1)

def main():
    """Função principal"""
    print("🏆 Iniciando criação dos badges para trilhas de aprendizado...")
    
    try:
        _configure_credentials()
        initialize_firebase()
        create_learning_path_badges()
        
        print("✅ Processo concluído com sucesso!")
        print("\n🏆 Badges criados:")
        print("🔹 Por Trilha Completada:")
        print("  - fundamentos_bitcoin_master")
        print("  - bitcoin_tech_expert")
        print("  - bitcoin_ecosystem_master")
        print("🔹 Por Módulos Completados:")
        print("  - first_module_completed")
        print("  - module_explorer")
        print("  - module_master")
        print("🔹 Por Trilhas Completadas:")
        print("  - learning_path_beginner")
        print("  - learning_path_enthusiast")
        print("  - learning_path_master")
        print("🔹 Por Pontuação em Quizzes:")
        print("  - perfect_quiz_score")
        print("  - excellent_quiz_score")
        print("🔹 Especiais por Questionário:")
        print("  - bitcoin_curious")
        print("  - bitcoin_promising")
        print("  - bitcoin_enthusiast")
        
        print("\n🎯 Próximos passos:")
        print("1. ✅ Badges das trilhas criados")
        print("2. ✅ Sistema de níveis unificado")
        print("3. ✅ Integração com sistema de recompensas")
        print("4. 🧪 Testar sistema completo")
        
    except Exception as e:
        print(f"❌ Erro durante a execução: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
