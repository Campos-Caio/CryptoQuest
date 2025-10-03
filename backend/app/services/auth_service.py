import logging
from fastapi import Depends
from app.core.firebase import get_firebase_auth
from app.repositories.user_repository import UserRepository, get_user_repository
from app.models.user import UserProfile, FirebaseUser, UserRegister
from firebase_admin.auth import UserNotFoundError, InvalidIdTokenError, EmailAlreadyExistsError
from firebase_admin.exceptions import FirebaseError

logger = logging.getLogger(__name__)

class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.auth = get_firebase_auth()
        self.user_repo = user_repo

    async def authenticate_and_get_profile(self, id_token: str) -> tuple[FirebaseUser, UserProfile]:
        logger.info("--- [AUTH SERVICE] Iniciando verificação do token ---")

        try:
            logger.debug("Verificando token com Firebase")
            decoded_token = self.auth.verify_id_token(id_token, clock_skew_seconds=30)

            uid = decoded_token['uid']
            email = decoded_token.get('email')
            name = decoded_token.get('name')
            logger.info(f"Token válido. UID: {uid}, Email: {email}")

            firebase_user_info = FirebaseUser(uid=uid, email=email, name=name)

            logger.debug(f"Buscando perfil no Firestore para UID: {uid}")
            user_profile = self.user_repo.get_user_profile(uid)

            if not user_profile:
                logger.warning(f"Perfil do usuário {uid} não encontrado. Criando novo perfil.")
                user_profile = self.user_repo.create_user_profile(uid=uid, email=email, name=name)
                logger.info(f"Perfil criado com sucesso para UID: {uid}")
                logger.info(f"🔍 [AuthService] Novo perfil criado - has_completed_questionnaire: {user_profile.has_completed_questionnaire}")
            else:
                logger.info(f"Perfil encontrado para UID: {uid}")
                logger.info(f"🔍 [AuthService] Perfil existente - has_completed_questionnaire: {user_profile.has_completed_questionnaire}")

            return firebase_user_info, user_profile

        except InvalidIdTokenError as e:
            logger.error(f"Token inválido ou expirado! Detalhes: {str(e)}", exc_info=True)
            raise ValueError("Token de ID inválido ou expirado! Faça login novamente.")
        except FirebaseError as e:
            logger.error(f"Erro do Firebase ao verificar o token: {e.code} - {str(e)}", exc_info=True)
            raise ValueError(f"Erro nos serviços Firebase: {e.code}")
        except Exception as e:
            logger.error(f"Erro inesperado na autenticação: {str(e)}", exc_info=True)
            raise Exception("Erro inesperado durante a autenticação.")

    async def register_user(self, user_data: UserRegister) -> tuple[FirebaseUser, UserProfile]:
        try:
            user = self.auth.create_user(
                email=user_data.email,
                password=user_data.password,
                display_name=user_data.name
            )

            user_profile = self.user_repo.create_user_profile(
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

async def get_auth_service(user_repo: UserRepository = Depends(get_user_repository)) -> AuthService:
    return AuthService(user_repo)
