import os
import firebase_admin 
from firebase_admin import credentials, firestore, auth
from .config import settings
from google.cloud.firestore_v1.async_client import AsyncClient

# Arquivo que centraliza a inicializacao do Firebase 
# Fornece as instancias de Auth e firebase de forma eficiente 

# Flag para iniciar firebase somente uma vez 
_firebase_app = None 
_firestore_async_db_client_instance = None 

def initialize_firebase(): 
    """
        Iniaciliza o Firebase SDK 
    """
    global _firebase_app 
    if _firebase_app is None: 
        try: 
            # Tenta encontrar o arquivo da credencial
            cred_path = settings.FIREBASE_CREDENTIALS 
            if not os.path.exists(cred_path): 
                raise FileNotFoundError(f"Arquivo de credenciais nao foi encontrado!")
            
            cred = credentials.Certificate(cred_path)
            _firebase_app = firebase_admin.initialize_app(cred)
            print(f"Firebase inicilizado com sucesso!")
        except Exception as error: 
            print(f"Erro ao inicilizar Firebase: {error}")
            raise 

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