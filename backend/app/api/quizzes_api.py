import logging
from typing import Annotated
from app.models.quizz import Quiz
from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies.auth import get_current_user
from app.models.mission import Quiz
from app.models.user import FirebaseUser
from app.core.firebase import get_firestore_db_async

router = APIRouter(prefix="/quizzes", tags=["Quizzes"])
logger = logging.getLogger(__name__) 

@router.get('/{quiz_id}', response_model=Quiz, summary='Busca o conteudo de um quiz pelo ID')
async def get_quiz_content_endpoint(
    quiz_id: str, 
    db = Depends(get_firestore_db_async), 
    current_user: Annotated[FirebaseUser, Depends(get_current_user)] = None
):
    """
    Recupera o documento completo de um quiz da coleção 'quizzes'.

    Args:
        quiz_id (str): O ID do documento do quiz a ser buscado.
        db: Instância do cliente Firestore assíncrono.
        current_user: Usuário autenticado (garante que só usuários logados acessem).

    Returns:
        Quiz: O objeto do quiz com título e a lista de perguntas.
    """

    logger.info(f"Buscando conteudo do Quiz de ID: {quiz_id}")
    quiz_doc = await db.collection('quizzes').document(quiz_id).get()

    if not quiz_doc.exist: 
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND, 
            detail=f"Quiz com ID: {quiz_id} nao foi encontrado!"
        )
    
    quiz_data = quiz_doc.to_dict()
    quiz_data['_id'] = quiz_doc.id 
    return quiz_data