
"""
Script para popular o banco de dados Firestore com missões e quizzes
para o sistema CryptoQuest.

Uso:
    python populate_missions.py [--seed-file seed_expanded.json] [--clear-existing]
"""

import json
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

def upsert_collection(db, collection_name, docs_map, clear_first=False):
    """Insere ou atualiza documentos em uma coleção"""
    if clear_first:
        clear_collection(db, collection_name)
    
    print(f"📝 Populando coleção '{collection_name}'...")
    success_count = 0
    error_count = 0
    
    for doc_id, data in docs_map.items():
        try:
            # Adiciona timestamp de criação/atualização
            data['created_at'] = datetime.now()
            data['updated_at'] = datetime.now()
            
            db.collection(collection_name).document(doc_id).set(data, merge=True)
            print(f"  ✅ {collection_name}/{doc_id}")
            success_count += 1
        except Exception as e:
            print(f"  ❌ Erro ao criar {collection_name}/{doc_id}: {e}")
            error_count += 1
    
    print(f"📊 {collection_name}: {success_count} sucessos, {error_count} erros")
    return success_count, error_count

def validate_data(data):
    """Valida a estrutura dos dados"""
    print("🔍 Validando estrutura dos dados...")
    
    required_collections = ['quizzes', 'missions']
    for collection in required_collections:
        if collection not in data:
            print(f"❌ Coleção '{collection}' não encontrada no arquivo")
            return False
    
    # Validar quizzes
    for quiz_id, quiz_data in data['quizzes'].items():
        if 'title' not in quiz_data:
            print(f"❌ Quiz '{quiz_id}' não tem título")
            return False
        if 'questions' not in quiz_data:
            print(f"❌ Quiz '{quiz_id}' não tem perguntas")
            return False
        
        for i, question in enumerate(quiz_data['questions']):
            if 'text' not in question:
                print(f"❌ Pergunta {i} do quiz '{quiz_id}' não tem texto")
                return False
            if 'options' not in question:
                print(f"❌ Pergunta {i} do quiz '{quiz_id}' não tem opções")
                return False
            if 'correct_answer_index' not in question:
                print(f"❌ Pergunta {i} do quiz '{quiz_id}' não tem índice da resposta correta")
                return False
            
            # Validar opções
            for j, option in enumerate(question['options']):
                if 'text' not in option:
                    print(f"❌ Opção {j} da pergunta {i} do quiz '{quiz_id}' não tem texto")
                    return False
    
    # Validar missões
    for mission_id, mission_data in data['missions'].items():
        required_fields = ['title', 'description', 'type', 'reward_points', 'required_level', 'content_id']
        for field in required_fields:
            if field not in mission_data:
                print(f"❌ Missão '{mission_id}' não tem campo '{field}'")
                return False
    
    print("✅ Validação concluída com sucesso!")
    return True

def main():
    parser = argparse.ArgumentParser(description='Popula o banco de dados com missões e quizzes')
    parser.add_argument('--seed-file', default='seed_expanded.json', 
                       help='Arquivo JSON com os dados (padrão: seed_expanded.json)')
    parser.add_argument('--clear-existing', action='store_true',
                       help='Limpa as coleções existentes antes de popular')
    parser.add_argument('--validate-only', action='store_true',
                       help='Apenas valida os dados sem inserir no banco')
    
    args = parser.parse_args()
    
    # Verificar se o arquivo firebase_key.json existe
    firebase_key_path = Path(__file__).resolve().parents[1] / "firebase_key.json"
    if not firebase_key_path.exists():
        print(f"❌ Arquivo firebase_key.json não encontrado em: {firebase_key_path}")
        print("💡 Certifique-se de que o arquivo existe na pasta backend/")
        sys.exit(1)
    
    # Carregar arquivo de seed
    seed_file = Path(__file__).parent / args.seed_file
    if not seed_file.exists():
        print(f"❌ Arquivo de seed não encontrado: {seed_file}")
        sys.exit(1)
    
    print(f"📖 Carregando dados de: {seed_file}")
    try:
        with open(seed_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Erro ao carregar arquivo JSON: {e}")
        sys.exit(1)
    
    # Validar dados
    if not validate_data(data):
        print("❌ Validação falhou. Corrija os erros antes de continuar.")
        sys.exit(1)
    
    if args.validate_only:
        print("✅ Validação concluída. Saindo...")
        return
    
    # Configurar credenciais e inicializar Firebase
    try:
        _configure_credentials()
        initialize_firebase()
        db = firestore.client()
    except Exception as e:
        print(f"❌ Erro ao configurar Firebase: {e}")
        print("💡 Verifique se o arquivo firebase_key.json está correto")
        sys.exit(1)
    
    # Popular coleções
    total_success = 0
    total_errors = 0
    
    if 'quizzes' in data:
        success, errors = upsert_collection(db, 'quizzes', data['quizzes'], args.clear_existing)
        total_success += success
        total_errors += errors
    
    if 'missions' in data:
        success, errors = upsert_collection(db, 'missions', data['missions'], args.clear_existing)
        total_success += success
        total_errors += errors
    
    # Resumo final
    print("\n" + "="*50)
    print("📊 RESUMO DA OPERAÇÃO")
    print("="*50)
    print(f"✅ Documentos criados/atualizados: {total_success}")
    print(f"❌ Erros: {total_errors}")
    
    if total_errors == 0:
        print("🎉 População concluída com sucesso!")
        print("\n💡 Próximos passos:")
        print("   1. Teste o sistema fazendo login")
        print("   2. Verifique se as missões diárias aparecem")
        print("   3. Tente completar um quiz")
    else:
        print("⚠️  Alguns erros ocorreram. Verifique os logs acima.")

if __name__ == "__main__":
    main()
