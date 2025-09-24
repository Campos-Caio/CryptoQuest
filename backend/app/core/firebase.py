import os
import json
import firebase_admin
import google.auth 
from firebase_admin import credentials, auth, firestore
from google.cloud.firestore_v1.async_client import AsyncClient

# --- Lógica de Carregamento de Credenciais ---

def _configure_credentials():
    """
    Configura as credenciais para o ambiente, preparando para a autenticação.
    """
    # Procura pela variável de ambiente (usada na Render)
    creds_json_str = os.getenv("FIREBASE_CREDENTIALS_JSON")
    
    if creds_json_str:
        # Na Render, escreve o conteúdo da variável em um arquivo temporário
        # para que o google.auth.default() possa encontrá-lo.
        temp_credentials_path = "/tmp/firebase_credentials.json"
        with open(temp_credentials_path, "w") as f:
            f.write(creds_json_str)
        # Define a variável de ambiente padrão que a biblioteca do Google procura
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_credentials_path
        print("Credenciais configuradas a partir da variável de ambiente.")
    else:
        # Localmente, aponta para o arquivo .json na raiz do backend
        print("Configurando credenciais a partir de arquivo local...")
        cred_path = "firebase_key.json"
        if not os.path.exists(cred_path):
            raise FileNotFoundError(f"Arquivo de credenciais não encontrado: {cred_path}")
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = cred_path

# --- Inicialização ---

_db_client_async = None

def initialize_firebase():
    """
    Inicializa o app Firebase Admin se ainda não existir.
    Usa as credenciais padrão configuradas por _configure_credentials.
    """
    if not firebase_admin._apps:
        try:
            print("Inicializando Firebase App...")
            # O firebase_admin agora usa as credenciais padrão do ambiente
            firebase_admin.initialize_app()
            print("Firebase inicializado com sucesso!")
        except Exception as e:
            print(f"!!! ERRO CRÍTICO AO INICIALIZAR FIREBASE: {e} !!!")
            raise e

# --- Funções de Dependência ---
def get_firebase_auth():
    return auth

def get_firestore_db():
    """
    Retorna uma instância síncrona do Cliente Firestore.
    """
    return firestore.client()

async def get_firestore_db_async() -> AsyncClient:
    """
    Retorna uma instância assíncrona do Cliente Firestore.
    """
    global _db_client_async
    if _db_client_async is None:
        print("Criando instância do Firestore AsyncClient...")
        
        # que foram configuradas pelo _configure_credentials.
        creds, project_id = google.auth.default()

        _db_client_async = AsyncClient(project=project_id, credentials=creds)
        print("Instância do Firestore AsyncClient criada.")
    return _db_client_async

# --- Execução da Inicialização ---
_configure_credentials() 
initialize_firebase()    