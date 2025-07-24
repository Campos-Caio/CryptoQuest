from fastapi import APIRouter, Depends, HTTPException, status 
from typing import Annotated 
import logging

from app.models.questionnaire import InitialQuestionnaire, QuestionnaireSubmission, KnowledgeProfile
from app.models.user import FirebaseUser
from app.dependencies.auth import get_current_user
from app.services.questionnaire_service import QuestionnaireService 
from app.repositories.user_repository import UserRepository, get_user_repository

# Function para injetar o service 
def get_questionnaire_service(
        user_repo: Annotated[UserRepository, Depends(get_user_repository)]
) -> QuestionnaireService: 
    return QuestionnaireService(user_repo)

router = APIRouter(prefix='/questionnaire',tags=['Questionnaire'])
logger = logging.getLogger(__name__)

@router.get("/initial", response_model=InitialQuestionnaire, summary="Obtem O questionario de nivelamento inicial!")
def get_initial_questionnaire_endpoint(
    service: Annotated[QuestionnaireService,  Depends(get_questionnaire_service)], 
): 
    '''
        Retorna a lista de perguntas e opcoes para o questionario inicial 
        O usuario deve estar autenticado para acessar
    '''
    return service.get_initial_questionnaire()

@router.post(
    '/initial/submit', 
    response_model=KnowledgeProfile, 
    status_code=status.HTTP_201_CREATED, 
    summary='Submete as respostas ao questionario inicial', 
)
async def submit_initial_questionnaire_endpoint(
    submission: QuestionnaireSubmission, 
    current_user: Annotated[FirebaseUser, Depends(get_current_user)], 
    service: Annotated[QuestionnaireService, Depends(get_questionnaire_service)], 
    user_repo: Annotated[UserRepository, Depends(get_user_repository)], 
): 
    """
        Recebe as respostas do Usuario, calcula seu perfil de conhecimento, 
        gera sua trilha de aprendizado inicial e salva os resultados. 

        **Esta operacao so pode ser realizada uma vez por usuario. 
    """

    # Verifica se o usuario ja respondeu o questionario
    user_profile = await user_repo.get_user_profile(current_user.uid)
    if user_profile and user_profile.has_completed_questionnaire: 
        raise HTTPException(
            status_code = status.HTTP_404_BAD_REQUEST, 
            detail="O usuario ja respondeu o questionario inicial!"
        )
    
    try: 
        knowledge_profile = await service.process_submission(current_user.uid, submission)
        return knowledge_profile 
    except Exception as error: 
        logger.error(f"Erro ao processar questionario para UID {current_user.uid}: {error}",exc_info=True)
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail='Ocorreu um erro ao processar suas respostas.'
        )