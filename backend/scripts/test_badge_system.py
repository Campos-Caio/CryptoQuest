"""
Script para testar o sistema de badges e identificar problemas.
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

def test_badge_system():
    """Testa o sistema de badges"""
    print("🧪 TESTANDO SISTEMA DE BADGES")
    print("=" * 60)
    
    try:
        db = firestore.client()
        
        # Teste 1: Verificar badges de learning paths
        print("\n🏆 TESTE 1: Badges de Learning Paths")
        print("-" * 40)
        
        badges_collection = db.collection('badges')
        badge_docs = badges_collection.stream()
        
        learning_path_badges = []
        for doc in badge_docs:
            badge_data = doc.to_dict()
            badge_id = doc.id
            
            # Verificar se é badge de learning path
            if any(keyword in badge_id for keyword in ['fundamentos', 'bitcoin', 'learning_path', 'module', 'quiz']):
                learning_path_badges.append({
                    'id': badge_id,
                    'name': badge_data.get('name', 'Sem nome'),
                    'description': badge_data.get('description', 'Sem descrição'),
                    'requirements': badge_data.get('requirements', {})
                })
        
        print(f"✅ Badges de learning paths encontrados: {len(learning_path_badges)}")
        for badge in learning_path_badges:
            print(f"   - {badge['id']}: {badge['name']}")
            print(f"     Descrição: {badge['description']}")
            print(f"     Requisitos: {badge['requirements']}")
            print()
        
        # Teste 2: Verificar badges do usuário específico
        print("\n👤 TESTE 2: Badges do Usuário")
        print("-" * 40)
        
        # Usar o UID do log: Qqzrrvenc5NajYFpZm4jHaVXYlN2
        user_id = "Qqzrrvenc5NajYFpZm4jHaVXYlN2"
        
        user_badges_collection = db.collection('user_badges')
        user_badges_query = user_badges_collection.where('user_id', '==', user_id)
        user_badges_docs = user_badges_query.stream()
        
        user_badges = []
        for doc in user_badges_docs:
            badge_data = doc.to_dict()
            user_badges.append({
                'badge_id': badge_data.get('badge_id'),
                'earned_at': badge_data.get('earned_at'),
                'context': badge_data.get('context', {})
            })
        
        print(f"✅ Badges do usuário {user_id}: {len(user_badges)}")
        for badge in user_badges:
            print(f"   - {badge['badge_id']}: {badge['earned_at']}")
            print(f"     Contexto: {badge['context']}")
        
        # Teste 3: Verificar progresso das trilhas
        print("\n📚 TESTE 3: Progresso das Trilhas")
        print("-" * 40)
        
        user_progress_collection = db.collection('user_path_progress')
        user_progress_query = user_progress_collection.where('user_id', '==', user_id)
        user_progress_docs = user_progress_query.stream()
        
        user_progress = []
        for doc in user_progress_docs:
            progress_data = doc.to_dict()
            user_progress.append({
                'path_id': progress_data.get('path_id'),
                'progress_percentage': progress_data.get('progress_percentage'),
                'completed_missions': len(progress_data.get('completed_missions', [])),
                'completed_at': progress_data.get('completed_at')
            })
        
        print(f"✅ Progresso das trilhas do usuário: {len(user_progress)}")
        for progress in user_progress:
            print(f"   - Trilha: {progress['path_id']}")
            print(f"     Progresso: {progress['progress_percentage']}%")
            print(f"     Missões completadas: {progress['completed_missions']}")
            print(f"     Completada em: {progress['completed_at']}")
        
        # Teste 4: Verificar se deveria ter badges
        print("\n🎯 TESTE 4: Análise de Badges Esperados")
        print("-" * 40)
        
        expected_badges = []
        
        # Verificar se completou trilha "fundamentos_dinheiro_bitcoin"
        for progress in user_progress:
            if progress['path_id'] == 'fundamentos_dinheiro_bitcoin' and progress['completed_at']:
                expected_badges.append('fundamentos_bitcoin_master')
                print(f"✅ Deveria ter badge: fundamentos_bitcoin_master (trilha completada)")
        
        # Verificar se completou módulos
        total_modules_completed = 0
        for progress in user_progress:
            # Assumindo que cada trilha tem 3 módulos
            modules_in_path = 3
            missions_per_module = 2  # Assumindo 2 missões por módulo
            total_missions = modules_in_path * missions_per_module
            
            if progress['completed_missions'] >= missions_per_module:
                total_modules_completed += 1
                print(f"✅ Módulo completado na trilha {progress['path_id']}")
        
        if total_modules_completed >= 1:
            expected_badges.append('first_module_completed')
            print(f"✅ Deveria ter badge: first_module_completed (primeiro módulo)")
        
        if total_modules_completed >= 3:
            expected_badges.append('module_explorer')
            print(f"✅ Deveria ter badge: module_explorer (3+ módulos)")
        
        # Verificar badges que o usuário tem
        user_badge_ids = [badge['badge_id'] for badge in user_badges]
        
        print(f"\n📊 RESUMO:")
        print(f"   Badges esperados: {expected_badges}")
        print(f"   Badges conquistados: {user_badge_ids}")
        
        missing_badges = [badge for badge in expected_badges if badge not in user_badge_ids]
        if missing_badges:
            print(f"   ❌ Badges faltando: {missing_badges}")
        else:
            print(f"   ✅ Todos os badges esperados foram conquistados!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO NO TESTE: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Função principal"""
    print("🧪 Iniciando teste do sistema de badges...")
    
    try:
        _configure_credentials()
        initialize_firebase()
        
        success = test_badge_system()
        
        if success:
            print("\n✅ TESTE CONCLUÍDO!")
        else:
            print("\n❌ TESTE FALHOU!")
        
    except Exception as e:
        print(f"❌ Erro durante a execução: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
