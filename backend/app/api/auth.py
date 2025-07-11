from fastapi import APIRouter, Depends, HTTPException, status, Header
from typing import Annotated 

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
async def authenticate_user_endpoint(authorization: Annotated[str, Header()], auth_service: Annotated[AuthService, Depends(get_auth_service)]): 
    """
    Endpoint para autenticar um usuario no backend apos ele ter feito login
    Com sucesso no frontend (Flutter) usando o Firebase Client SDK.
    Recebe o Firebase ID Token no cabecalho 'Authorization: Bearer <ID_TOKEN>'.
    Verifica o token, e retorna o perfil do usuario do Firestore.
    """

    if not authorization or not authorization.startswith("Bearer"): 
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token de autenticacao ausente ou mal informado!")
    
    id_token = authorization[len("Bearer "):].strip()

    try: 
        firebase_user, user_profile = await auth_service.authenticate_and_get_profile(id_token)
        return AuthSuccess(message="Usuario autenticado e perfil carregador com sucesso!", uid=firebase_user.uid, user_profile=user_profile)
    except ValueError as error: 
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(error))
    except Exception as error: 
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail= f"Erro interno do servidor: {error}", 
        )