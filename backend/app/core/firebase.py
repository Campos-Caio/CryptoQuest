import os
import json
import firebase_admin
from firebase_admin import credentials, auth, firestore
from google.cloud.firestore_v1.async_client import AsyncClient

# Arquivo que centraliza a inicializacao do Firebase 
# Fornece as instancias de Auth e firebase de forma eficiente 
# Flag para iniciar firebase somente uma vez 
_firebase_app = None 
_firestore_async_db_client_instance = None 

def initialize_firebase():
    """
    Inicializa o app Firebase Admin usando variáveis de ambiente (para produção)
    ou um arquivo local (para desenvolvimento).
    """
    if not firebase_admin._apps:
        try:
            # Procura pela variável de ambiente primeiro (usada na Render)
            creds_json_str = os.getenv("FIREBASE_CREDENTIALS_JSON")

            if creds_json_str:
                print("Firebase inicializando com credenciais de variável de ambiente...")
                creds_dict = json.loads(creds_json_str)
                cred = credentials.Certificate(creds_dict)
            else:
                # Se não encontrar, procura pelo arquivo local (para rodar no seu PC)
                print("Firebase inicializando com arquivo de credenciais local...")
                cred_path = "cryptoquest-90a7b-firebase-adminsdk-hwp98-415277cd9f.json" # Verifique se o nome está correto
                if not os.path.exists(cred_path):
                    raise FileNotFoundError(f"Arquivo de credenciais não encontrado: {cred_path}")
                cred = credentials.Certificate(cred_path)

            firebase_admin.initialize_app(cred)
            print("Firebase inicializado com sucesso!")

        except Exception as e:
            print(f"!!! ERRO CRÍTICO AO INICIALIZAR FIREBASE: {e} !!!")
            raise e

def get_firebase_app(): 
    """ Retorna uma instancia do Firebase App """
    if _firebase_app is None: 
        initialize_firebase()
    return _firebase_app 

def get_firebase_auth(): 
    """ Retorna o servico de auth do Firebase """
    get_firebase_app() # Garante que esteja inicilizado 
    return auth 

def get_firestore_db(): 
    """ Retorna uma instancia do Cliente Firestore """
    get_firebase_app() 
    return firestore.client() 

async def get_firestore_db_async():
    """Retorna uma instância assíncrona do Cliente Firestore."""
    global _firestore_async_db_client_instance
    if _firestore_async_db_client_instance is None:
        get_firebase_app()
        # Cria e retorna um cliente assíncrono do Firestore
        _firestore_async_db_client_instance = AsyncClient.from_service_account_json(settings.FIREBASE_CREDENTIALS)
    return _firestore_async_db_client_instance

initialize_firebase() 