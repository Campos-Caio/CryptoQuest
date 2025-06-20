from fastapi import Depends
from app.core.firebase import get_firestore_db, get_firebase_auth
from app.repositories.user_repository import UserRepository, get_user_repository 
from app.models.user import UserProfile, FirebaseUser, UserRegister
from firebase_admin.auth import UserNotFoundError, InvalidIdTokenError, EmailAlreadyExistsError
from firebase_admin.exceptions import FirebaseError 
import traceback

class AuthService: 
    def __init__(self, user_repo: UserRepository):
        self.auth = get_firebase_auth()
        self.user_repo = user_repo 

    async def register_user(self, user_data: UserRegister) -> tuple[FirebaseUser, UserProfile]: 
        """
        Cria um novo usuario no Firebase Auth e seu perfil no Firestore 
        """

        try: 
            # 1. Criar Usuario no Firebase Auth
            user = self.auth.create_user(
                email = user_data.email,
                password = user_data.password, 
                display_name = user_data.name 
            )

            # 2. Criar perfil no Firestore usando o UID do usuario 
            user_profile = await self.user_repo.create_user_profile(
                uid=user.uid, 
                name = user_data.name, 
                email = user_data.email 
            )
            firebase_user_info = FirebaseUser(uid=user.uid, email=user.email, name=user_data.name)
            return firebase_user_info, user_profile
        except EmailAlreadyExistsError:
            raise ValueError("Email já cadastrado.")
        except FirebaseError as e: 
            print(f"FirebaseError capturada: {e.code} - {str(e)}")
            traceback.print_exc() 
            if e.code == "auth/weak-password":
                raise ValueError("Senha muito fraca. Mínimo de 6 caracteres.")
            raise ValueError(f"Erro no Firebase Auth durante o cadastro: {e.code} - {str(e)}") 
        except Exception as e: 
            print(f"Erro inesperado capturado no registro: {e}")
            traceback.print_exc()
            raise Exception("Erro inesperado no cadastro. Consulte os logs do servidor para mais detalhes.")
        

    async def verify_id_token(self, id_token: str) -> FirebaseUser: 
        """
        Verifica e decodifica o token de ID do Firebase
        """ 

        try: 
            decoded_token = self.auth.verify_id_token(id_token)

            return FirebaseUser(
                uid = decoded_token['uid'], 
                email=decoded_token.get('email'), 
                name = decoded_token.get('name')
            )
        except InvalidIdTokenError: # Exceção mais específica primeiro
            raise ValueError("Token de ID inválido ou expirado!")
        except FirebaseError as e: # Erros gerais do Firebase
            print(f"FirebaseError capturada: {e.code} - {str(e)}")
            traceback.print_exc() 
            raise Exception(f"Erro ao verificar token do Firebase: {e.code} - {str(e)}")
        except Exception as e: 
            print(f"Erro inesperado capturado na verificação de token: {e}")
            traceback.print_exc()
            raise Exception (f"Erro inesperado ao verificar token. Consulte os logs do servidor para mais detalhes.")
        
async def get_auth_service(user_repo: UserRepository = Depends(get_user_repository)) -> AuthService:
    return AuthService(user_repo)

