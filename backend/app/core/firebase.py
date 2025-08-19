import os
import json
import firebase_admin
import google.auth
from firebase_admin import credentials, auth, firestore
from google.cloud.firestore_v1.async_client import AsyncClient
from google.auth import credentials as google_auth_credentials 

# --- Lógica de Carregamento de Credenciais (continua a mesma) ---
def _load_credentials():
    """
    Carrega as credenciais e retorna o objeto de credencial.
    """
    creds_json_str = os.getenv("FIREBASE_CREDENTIALS_JSON")
    if creds_json_str:
        creds_dict = json.loads(creds_json_str)
        return credentials.Certificate(creds_dict)
    else:
        cred_path = "firebase_key.json"
        if not os.path.exists(cred_path):
            raise FileNotFoundError(f"Arquivo de credenciais não encontrado: {cred_path}")
        return credentials.Certificate(cred_path)

# --- Inicialização ---
_db_client_async = None
_cred_object = _load_credentials()

def initialize_firebase():
    """
    Inicializa o app Firebase Admin se ainda não existir.
    """
    if not firebase_admin._apps:
        try:
            print("Inicializando Firebase App...")
            firebase_admin.initialize_app(_cred_object)
            print("Firebase inicializado com sucesso!")
        except Exception as e:
            print(f"!!! ERRO CRÍTICO AO INICIALIZAR FIREBASE: {e} !!!")
            raise e

# --- Funções de Dependência ---
def get_firebase_auth():
    return auth

async def get_firestore_db_async() -> AsyncClient:
    """
    Retorna uma instância assíncrona do Cliente Firestore.
    """
    global _db_client_async
    if _db_client_async is None:
        print("Criando instância do Firestore AsyncClient...")
        
        # a partir do app Firebase já inicializado.
        project_id = firebase_admin.get_app().project_id
        
        # A biblioteca google-auth sabe como encontrar as credenciais padrão do ambiente
        # que o firebase-admin já configurou.
        creds, _ = google.auth.default()

        _db_client_async = AsyncClient(project=project_id, credentials=creds)
        print("Instância do Firestore AsyncClient criada.")
    return _db_client_async

# --- Execução da Inicialização ---
initialize_firebase()