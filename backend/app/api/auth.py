from fastapi import APIRouter, Depends, HTTPException, logger, status, Header
from typing import Annotated 
import logging

from app.models.user import (
    UserRegister,
    UserLogin,
    AuthSuccess,
    FirebaseUser,
    UserProfile,
)
from app.services.auth_service import AuthService, get_auth_service 
from app.dependencies.auth import get_current_user 
from firebase_admin.auth import UserNotFoundError 

from app.repositories.user_repository import UserRepository, get_user_repository 

router = APIRouter(prefix="/auth", tags=["Auth"])
logger = logging.getLogger(__name__)


@router.post(
    "/register", response_model=AuthSuccess, status_code=status.HTTP_201_CREATED
)
async def register_user_endpoint(
    user_data: UserRegister,
    auth_service: Annotated[AuthService, Depends(get_auth_service)] # Usando Annotated
):
    """
    Endpoint para cadastrar novo usuario
    Cria um usuario no Firebase Auth e o perfil inicial
    """
    try:
        firebase_user, user_profile = await auth_service.register_user(user_data)
        return AuthSuccess(
            message="Usuario registrado com sucesso!",
            uid=firebase_user.uid,
            user_profile=user_profile,
        )
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno do servidor: {error}",
        )

@router.get("/me", response_model=UserProfile)
async def read_current_user_profile(
    current_user: Annotated[FirebaseUser, Depends(get_current_user)],
    user_repo: Annotated[UserRepository, Depends(get_user_repository)], # Usando Annotated
):
    """
    Endpoint para obter o perfil do usuário atualmente autenticado.
    Requer um token de ID do Firebase no cabeçalho Authorization.
    """
    user_profile = await user_repo.get_user_profile(current_user.uid)
    if not user_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil do usuário não encontrado.",
        )
    return user_profile

@router.post("/authenticate", response_model=AuthSuccess)
async def authenticate_user_endpoint(
    authorization: Annotated[str, Header()],
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
):
    """
    Endpoint para autenticar um usuário com token do Firebase.
    """
    logger.info("--- [INÍCIO DO PROCESSO DE AUTENTICAÇÃO] ---")

    if not authorization or not authorization.startswith("Bearer "):
        logger.warning("Token ausente ou mal formatado no cabeçalho Authorization.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticação ausente ou mal informado!"
        )

    id_token = authorization[len("Bearer "):].strip()
    logger.debug(f"Token recebido com {len(id_token)} caracteres")
    logger.debug(f"Token (início): {id_token[:30]}...")

    try:
        firebase_user, user_profile = await auth_service.authenticate_and_get_profile(id_token)
        logger.info(f"Usuário autenticado com sucesso: UID={firebase_user.uid}")
        
        # ✅ LOGS DETALHADOS para debug
        logger.info(f"🔍 [AUTH API] UserProfile retornado:")
        logger.info(f"🔍 [AUTH API] - UID: {user_profile.uid}")
        logger.info(f"🔍 [AUTH API] - has_completed_questionnaire: {user_profile.has_completed_questionnaire}")
        logger.info(f"🔍 [AUTH API] - Level: {user_profile.level}")
        logger.info(f"🔍 [AUTH API] - Points: {user_profile.points}")
        
        return AuthSuccess(
            message="Usuário autenticado com sucesso!",
            uid=firebase_user.uid,
            user_profile=user_profile
        )
    except ValueError as error:
        logger.warning(f"Falha na autenticação: {str(error)}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(error))
    except Exception as error:
        logger.error(f"Erro interno inesperado: {str(error)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno do servidor: {error}",
        )