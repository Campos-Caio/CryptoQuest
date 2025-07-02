import logging
from fastapi import Depends
from app.core.firebase import get_firebase_auth
from app.repositories.user_repository import UserRepository, get_user_repository
from app.models.user import UserProfile, FirebaseUser, UserRegister
from firebase_admin.auth import UserNotFoundError, InvalidIdTokenError, EmailAlreadyExistsError
from firebase_admin.exceptions import FirebaseError

# Configura o logger para este módulo
logger = logging.getLogger(__name__)

class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.auth = get_firebase_auth()
        self.user_repo = user_repo

    async def register_user(self, user_data: UserRegister) -> tuple[FirebaseUser, UserProfile]:
        """
        Cria um novo usuário no Firebase Auth e seu perfil no Firestore.
        """
        try:
            user = self.auth.create_user(
                email=user_data.email,
                password=user_data.password,
                display_name=user_data.name
            )

            user_profile = await self.user_repo.create_user_profile(
                uid=user.uid,
                name=user_data.name,
                email=user_data.email
            )
            firebase_user_info = FirebaseUser(uid=user.uid, email=user.email, name=user_data.name)
            return firebase_user_info, user_profile

        except EmailAlreadyExistsError:
            raise ValueError("Email já cadastrado.")
        except FirebaseError as e:
            logger.error(f"Erro no Firebase durante o cadastro: {e.code} - {str(e)}", exc_info=True)
            if e.code == "auth/weak-password":
                raise ValueError("Senha muito fraca. Mínimo de 6 caracteres.")
            raise ValueError(f"Erro no Firebase Auth durante o cadastro: {e.code}")
        except Exception as e:
            logger.error(f"Erro inesperado no registro: {e}", exc_info=True)
            raise Exception("Erro inesperado no cadastro.")

    async def verify_id_token(self, id_token: str) -> FirebaseUser:
        """
        Verifica e decodifica o token de ID do Firebase.
        """
        try:
            decoded_token = self.auth.verify_id_token(id_token)
            return FirebaseUser(
                uid=decoded_token['uid'],
                email=decoded_token.get('email'),
                name=decoded_token.get('name')
            )
        except InvalidIdTokenError:
            raise ValueError("Token de ID inválido ou expirado!")
        except FirebaseError as e:
            logger.error(f"Erro ao verificar token do Firebase: {e.code} - {str(e)}", exc_info=True)
            raise Exception(f"Erro ao verificar token do Firebase: {e.code}")
        except Exception as e:
            logger.error(f"Erro inesperado na verificação de token: {e}", exc_info=True)
            raise Exception("Erro inesperado ao verificar token.")

    async def authenticate_and_get_profile(self, id_token: str) -> tuple[FirebaseUser, UserProfile]:
        """
        Verifica o ID Token, busca ou cria o perfil do usuário no Firestore
        e retorna as informações do usuário e seu perfil.
        """
        try:
            # 1. Verificar e decodificar o token de ID do Firebase
            decoded_token = self.auth.verify_id_token(id_token)
            uid = decoded_token['uid']
            email = decoded_token.get('email')
            name = decoded_token.get('name')

            firebase_user_info = FirebaseUser(uid=uid, email=email, name=name)

            # 2. Buscar ou criar perfil de usuário no Firestore
            user_profile = await self.user_repo.get_user_profile(uid)
            if not user_profile:
                logger.warning(f"Perfil de usuário {uid} não encontrado. Criando um novo perfil.")
                user_profile = await self.user_repo.create_user_profile(uid=uid, email=email, name=name)

            return firebase_user_info, user_profile

        except InvalidIdTokenError:
            raise ValueError("Token de ID inválido ou expirado! Faça login novamente.")
        except FirebaseError as e:
            logger.error(f"Erro no Firebase durante a autenticação: {e.code} - {str(e)}", exc_info=True)
            raise ValueError(f"Erro nos serviços Firebase: {e.code}")
        except Exception as e:
            logger.error(f"Erro inesperado na autenticação/perfil: {e}", exc_info=True)
            raise Exception("Erro inesperado durante a autenticação.")

async def get_auth_service(user_repo: UserRepository = Depends(get_user_repository)) -> AuthService:
    return AuthService(user_repo)