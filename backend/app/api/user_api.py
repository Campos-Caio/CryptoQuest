from fastapi import APIRouter, Depends, status
from typing import Annotated
from app.models.user import UserProfile, UserProfileUpdate, FirebaseUser
from app.dependencies.auth import get_current_user
from app.repositories.user_repository import UserRepository, get_user_repository

router = APIRouter(prefix='/users', tags=['Users'])

@router.put(
    '/me', 
    response_model=UserProfile, 
    summary="Atualiza o perfil do usuario autenticado!"
)

async def update_current_user_profile(
    update_data: UserProfileUpdate, 
    current_user: Annotated[FirebaseUser, Depends(get_current_user)], 
    user_repo: Annotated[UserRepository, Depends(get_user_repository)], 
): 
    """
        Atualiza os dados do perfil do usuario logado

        Apenas os campos fornecidos no corpo da requisicao serao atualizados
    """

    # Converte o modelo Pydantic em um dict, removendo valores nulos 
    update_dict = update_data.model_dump(exclude_unset=True)

    # Atualiza o perfil no banco de dados 
    user_repo.update_user_Profile(current_user.uid, update_dict)

    # Retorna o perfil atualizado 
    updated_profile = user_repo.get_user_profile(current_user.uid)
    return updated_profile 
