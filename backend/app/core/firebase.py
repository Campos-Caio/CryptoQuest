import os
import json
import firebase_admin
from firebase_admin import credentials, auth, firestore
from google.cloud.firestore_v1.async_client import AsyncClient

# --- Lógica de Carregamento de Credenciais Centralizada ---

def _load_credentials():
    """
    Carrega as credenciais e retorna o objeto de credencial.
    """
    creds_json_str = os.getenv("FIREBASE_CREDENTIALS_JSON")
    if creds_json_str:
        print("Carregando credenciais da variável de ambiente...")
        creds_dict = json.loads(creds_json_str)
        return credentials.Certificate(creds_dict)
    else:
        print("Carregando credenciais de arquivo local...")
        cred_path = "cryptoquest-90a7b-firebase-adminsdk-hwp98-415277cd9f.json" # Seu arquivo local
        if not os.path.exists(cred_path):
            raise FileNotFoundError(f"Arquivo de credenciais não encontrado: {cred_path}")
        return credentials.Certificate(cred_path)

# --- Inicialização ---
_db_client_async = None
_cred_object = _load_credentials() # Carrega as credenciais uma única vez

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
        
        # passamos diretamente as credenciais que já carregamos.
        project_id = _cred_object.project_id
        
        _db_client_async = AsyncClient(project=project_id, credentials=_cred_object)
        
        print("Instância do Firestore AsyncClient criada.")
    return _db_client_async

# --- Execução da Inicialização ---
initialize_firebase()