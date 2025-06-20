from fastapi import APIRouter, Depends, HTTPException, status
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