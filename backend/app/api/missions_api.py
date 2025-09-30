import logging
from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies.auth import get_current_user
from app.models.mission import Mission, QuizSubmision
from app.models.user import FirebaseUser, UserProfile
from app.repositories.user_repository import UserRepository, get_user_repository
from app.services.mission_service import MissionService, get_mission_service


router = APIRouter(prefix="/missions", tags=["Missions"])
logger = logging.getLogger(__name__)


@router.get(
    "/daily",
    response_model=List[Mission],
    summary="Busca as missões elegíveis para o usuário autenticado!",
)
async def get_daily_missions_endpoint(
    current_user: Annotated[FirebaseUser, Depends(get_current_user)],
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    mission_service: Annotated[MissionService, Depends(get_mission_service)],
):
    """
    Recupera uma lista de missões elegíveis para o usuário atualmente logado.
    As missões são filtradas por nível e não incluem missões já completadas.

    Args:
        Current_user: O usuario autenticado, injetado pela dependencia get_current_user
        user_repo: A instancia do repositorio de usuario para buscar perfil completo
        mission_service: A instancia do servico de missoes que contem a logica de negocio

    Raises:
        httpException(404): Se o perfil do usuario nao for encontrado

    Returns:
        List[Mission]: Uma lista de objetos de missoes elegíveis para o usuário
    """

    logger.info(f"Buscando missões elegíveis para o usuario {current_user.uid}")

    user_profile = user_repo.get_user_profile(current_user.uid)
    if not user_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil do usuario nao encontrado!",
        )

    eligible_missions = await mission_service.get_daily_missions_for_user(user_profile)
    return eligible_missions





@router.post(
    "/{mission_id}/complete",
    response_model=UserProfile,
    summary="Submete uma missao como concluida e recebe recompensas",
)
async def complete_mission_endpoint(
    mission_id: str,
    submission: QuizSubmision,
    current_user: Annotated[FirebaseUser, Depends(get_current_user)],
    mission_service: Annotated[MissionService, Depends(get_mission_service)],
):
    """
    Processa a conclusão de uma missão por um usuário.

    Esta rota valida a missão, calcula e atribui as recompensas (pontos),
    e atualiza o perfil do usuário, retornando-o com os novos valores.

    Args:
        mission_id (str): O ID da missão que está sendo concluída (da URL).
        current_user: O usuário autenticado.
        mission_service: O serviço que contém a lógica de conclusão da missão.

    Raises:
        HTTPException(400): Se a missão for inválida ou não puder ser concluída.
        HTTPException(500): Se ocorrer um erro interno durante o processamento.

    Returns:
        UserProfile: O perfil do usuário atualizado após receber as recompensas.
    """

    logger.info(
        f"Usuario {current_user.uid} esta tentando completar a missao {mission_id}"
    )

    try:
        updated_user_profile = await mission_service.complete_mission(
            user_id=current_user.uid, mission_id=mission_id, submission=submission
        )
        return updated_user_profile

    except ValueError as error:
        # Tratar especificamente o erro de missão já concluída
        if "já foi concluída anteriormente" in str(error):  # ALTERADO
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Esta missão já foi concluída anteriormente."  # ALTERADO
            )
        elif "Nível insuficiente" in str(error):  # NOVO
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(error)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=str(error)
            )
    except Exception as error:
        logger.error(
            f"Erro inesperado ao completar missão para {current_user.uid}: {error}", 
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocorreu um erro ao processar a conclusão da missão"
    )
