import os
import json
import logging
import firebase_admin
import google.auth 
from firebase_admin import credentials, auth, firestore
from google.cloud.firestore_v1.async_client import AsyncClient

logger = logging.getLogger(__name__)

# --- Lógica de Carregamento de Credenciais ---

def _configure_credentials():
    """
    Configura as credenciais para o ambiente, preparando para a autenticação.
    Prioriza variáveis de ambiente para maior segurança.
    """
    # Procura pela variável de ambiente (usada em produção)
    creds_json_str = os.getenv("FIREBASE_CREDENTIALS_JSON")
    
    if creds_json_str:
        # Em produção, escreve o conteúdo da variável em um arquivo temporário
        # para que o google.auth.default() possa encontrá-lo.
        temp_credentials_path = "/tmp/firebase_credentials.json"
        with open(temp_credentials_path, "w") as f:
            f.write(creds_json_str)
        # Define a variável de ambiente padrão que a biblioteca do Google procura
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_credentials_path
        logger.info("Credenciais configuradas a partir da variável de ambiente.")
    else:
        # Localmente, aponta para o arquivo .json na raiz do backend
        logger.warning("Configurando credenciais a partir de arquivo local - NÃO RECOMENDADO PARA PRODUÇÃO")
        cred_path = "firebase_key.json"
        if not os.path.exists(cred_path):
            raise FileNotFoundError(f"Arquivo de credenciais não encontrado: {cred_path}. Configure FIREBASE_CREDENTIALS_JSON")
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
            logger.info("Inicializando Firebase App...")
            # O firebase_admin agora usa as credenciais padrão do ambiente
            firebase_admin.initialize_app()
            logger.info("Firebase inicializado com sucesso!")
        except Exception as e:
            logger.error(f"Erro crítico ao inicializar Firebase: {e}")
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
        logger.debug("Criando instância do Firestore AsyncClient...")
        
        # Usa as credenciais que foram configuradas pelo _configure_credentials.
        creds, project_id = google.auth.default()

        _db_client_async = AsyncClient(project=project_id, credentials=creds)
        logger.debug("Instância do Firestore AsyncClient criada.")
    return _db_client_async

# --- Execução da Inicialização ---
_configure_credentials() 
initialize_firebase()    