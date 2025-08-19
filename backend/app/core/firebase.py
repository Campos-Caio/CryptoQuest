import os
import json
import firebase_admin
from firebase_admin import credentials, auth, firestore
from google.cloud.firestore_v1.async_client import AsyncClient

# --- Lógica de Carregamento de Credenciais Centralizada ---

def _load_credentials():
    """
    Carrega as credenciais do Firebase a partir de uma variável de ambiente
    (para produção) ou de um arquivo local (para desenvolvimento).
    Retorna o objeto de credencial ou o dicionário de credenciais.
    """
    # Tenta pegar as credenciais da variável de ambiente primeiro (usada na Render)
    creds_json_str = os.getenv("FIREBASE_CREDENTIALS_JSON")
    
    if creds_json_str:
        print("Carregando credenciais da variável de ambiente...")
        creds_dict = json.loads(creds_json_str)
        return credentials.Certificate(creds_dict), creds_dict
    else:
        # Se não encontrar, tenta usar o arquivo local (para rodar no seu PC)
        print("Carregando credenciais de arquivo local...")
        cred_path = "cryptoquest-90a7b-firebase-adminsdk-hwp98-415277cd9f.json" # Verifique o nome do arquivo
        if not os.path.exists(cred_path):
            raise FileNotFoundError(f"Arquivo de credenciais não encontrado: {cred_path}")
        return credentials.Certificate(cred_path), cred_path

# --- Inicialização ---

_db_client_async = None

def initialize_firebase():
    """
    Inicializa o app Firebase Admin, mas SOMENTE se ele ainda não existir.
    """
    if not firebase_admin._apps:
        try:
            cred_object, _ = _load_credentials() # Carrega as credenciais
            firebase_admin.initialize_app(cred_object)
            print("Firebase inicializado com sucesso!")
        except Exception as e:
            print(f"!!! ERRO CRÍTICO AO INICIALIZAR FIREBASE: {e} !!!")
            raise e

# --- Funções de Dependência ---

def get_firebase_auth():
    """Retorna o serviço de auth do Firebase."""
    return auth

async def get_firestore_db_async() -> AsyncClient:
    """Retorna uma instância assíncrona do Cliente Firestore."""
    global _db_client_async
    if _db_client_async is None:
        # Usa a mesma lógica centralizada para obter as credenciais
        _, cred_source = _load_credentials()
        
        # O AsyncClient pode ser inicializado a partir do dicionário ou do caminho do arquivo
        if isinstance(cred_source, dict):
             _db_client_async = AsyncClient(credentials=credentials.Certificate(cred_source))
        else:
             _db_client_async = AsyncClient.from_service_account_json(cred_source)

    return _db_client_async

# --- Execução da Inicialização ---
initialize_firebase()