import logging
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from app.core.firebase import get_firestore_db_async
from app.models.mission import Quiz
from app.dependencies.auth import get_current_user
from app.models.user import FirebaseUser

router = APIRouter(prefix="/quizzes", tags=["Quizzes"])
logger = logging.getLogger(__name__)


@router.get(
    "/{quiz_id}",
    response_model=Quiz,
    summary="Busca um quiz específico por ID"
)
async def get_quiz_endpoint(
    quiz_id: str,
    db_client=Depends(get_firestore_db_async),
    current_user: Annotated[FirebaseUser, Depends(get_current_user)] = None
):
    """
    Recupera um quiz específico do Firestore pelo seu ID.
    
    Args:
        quiz_id: O ID do quiz a ser recuperado
        db_client: Instância do cliente Firestore assíncrono
        current_user: Usuário autenticado (garante que só usuários logados acessem)
        
    Raises:
        HTTPException(404): Se o quiz não for encontrado
        
    Returns:
        Quiz: O objeto quiz com suas perguntas e opções
    """
    logger.info(f"Buscando quiz com ID: {quiz_id}")
    
    try:
        quiz_ref = db_client.collection("quizzes").document(quiz_id)
        quiz_doc = await quiz_ref.get()
        
        if not quiz_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quiz não encontrado!"
            )
        
        quiz_data = quiz_doc.to_dict()
        quiz_data["_id"] = quiz_doc.id
        
        return Quiz(**quiz_data)
        
    except HTTPException:
        raise
    except Exception as error:
        logger.error(f"Erro ao buscar quiz {quiz_id}: {error}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao buscar quiz"
        )
