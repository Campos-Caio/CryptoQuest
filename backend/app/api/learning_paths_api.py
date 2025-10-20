from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Dict, Any, Union
from datetime import datetime, UTC
import logging
from app.models.learning_path import LearningPath, UserPathProgress, LearningPathResponse
from app.models.user import FirebaseUser
from app.models.mission import QuizSubmision, EnhancedQuizSubmission
from app.services.learning_path_service import LearningPathService
from app.services.reward_service import RewardService, get_reward_service
from app.dependencies.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/learning-paths", tags=["Learning Paths"])

# Função de dependência para criar o service com RewardService
def get_service(reward_service: RewardService = Depends(get_reward_service)) -> LearningPathService:
    return LearningPathService(reward_service=reward_service)

# ==================== ENDPOINTS PÚBLICOS ====================

@router.get("/", response_model=List[LearningPath])
async def get_all_learning_paths(
    service: LearningPathService = Depends(get_service)
):
    """
    Busca todas as trilhas de aprendizado ativas
    
    Returns:
        List[LearningPath]: Lista de trilhas ativas
    """
    try:
        paths = await service.get_all_learning_paths()
        return paths
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar trilhas: {str(e)}"
        )

@router.get("/recommended")
async def get_recommended_learning_paths(
    current_user: FirebaseUser = Depends(get_current_user),
    service: LearningPathService = Depends(get_service),
    limit: int = 5
):
    """
    🆕 FASE 2: Busca learning paths recomendados pela IA baseado no perfil do usuário
    
    Args:
        current_user: Usuário autenticado
        limit: Número máximo de recomendações (padrão: 5)
    
    Returns:
        List[Dict]: Lista de trilhas recomendadas com scores e reasoning
    """
    try:
        user_id = current_user.uid
        recommendations = await service.get_recommended_learning_paths(user_id, limit)
        
        return {
            "user_id": user_id,
            "recommendations": recommendations,
            "total_found": len(recommendations),
            "generated_at": datetime.now(UTC).isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar recomendações: {str(e)}"
        )

@router.get("/{path_id}", response_model=LearningPath)
async def get_learning_path_by_id(
    path_id: str,
    service: LearningPathService = Depends(get_service)
):
    """
    Busca uma trilha específica por ID
    
    Args:
        path_id: ID da trilha
        
    Returns:
        LearningPath: Trilha encontrada
    """
    try:
        path = await service.get_learning_path_by_id(path_id)
        if not path:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Trilha {path_id} não encontrada"
            )
        return path
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar trilha: {str(e)}"
        )

# ==================== ENDPOINTS AUTENTICADOS ====================

@router.get("/{path_id}/details", response_model=LearningPathResponse)
async def get_user_path_details(
    path_id: str,
    current_user: FirebaseUser = Depends(get_current_user),
    service: LearningPathService = Depends(get_service)
):
    """
    Busca detalhes completos de uma trilha com progresso do usuário
    
    Args:
        path_id: ID da trilha
        current_user: Usuário autenticado
        
    Returns:
        LearningPathResponse: Detalhes da trilha com progresso
    """
    try:
        user_id = current_user.uid
        details = await service.get_user_path_details(user_id, path_id)
        
        if not details:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Trilha {path_id} não encontrada"
            )
        
        return details
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar detalhes da trilha: {str(e)}"
        )

@router.post("/{path_id}/start", response_model=UserPathProgress)
async def start_learning_path(
    path_id: str,
    current_user: FirebaseUser = Depends(get_current_user),
    service: LearningPathService = Depends(get_service)
):
    """
    Inicia uma trilha para o usuário
    
    Args:
        path_id: ID da trilha
        current_user: Usuário autenticado
        
    Returns:
        UserPathProgress: Progresso inicial da trilha
    """
    try:
        user_id = current_user.uid
        progress = await service.start_learning_path(user_id, path_id)
        return progress
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao iniciar trilha: {str(e)}"
        )


@router.get("/user/progress", response_model=List[UserPathProgress])
async def get_user_progress(
    current_user: FirebaseUser = Depends(get_current_user),
    service: LearningPathService = Depends(get_service)
):
    """
    Busca o progresso do usuário em todas as trilhas
    
    Args:
        current_user: Usuário autenticado
        
    Returns:
        List[UserPathProgress]: Lista de progresso em todas as trilhas
    """
    try:
        user_id = current_user.uid
        progress_list = service.repository.get_all_user_progress(user_id)
        return progress_list
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar progresso do usuário: {str(e)}"
        )

# ==================== ENDPOINTS DE ESTATÍSTICAS ====================

@router.get("/{path_id}/stats")
async def get_path_stats(
    path_id: str,
    current_user: FirebaseUser = Depends(get_current_user),
    service: LearningPathService = Depends(get_service)
):
    """
    Busca estatísticas de uma trilha para o usuário
    
    Args:
        path_id: ID da trilha
        current_user: Usuário autenticado
        
    Returns:
        Dict: Estatísticas da trilha
    """
    try:
        user_id = current_user.uid
        details = await service.get_user_path_details(user_id, path_id)
        
        if not details:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Trilha {path_id} não encontrada"
            )
        
        return details.stats
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar estatísticas: {str(e)}"
        )

@router.post(
    "/{path_id}/missions/{mission_id}/complete",
    response_model=Dict[str, Any],
    summary="Completa uma missão de uma trilha de aprendizado"
)
async def complete_learning_path_mission(
    path_id: str,
    mission_id: str,
    submission: Union[QuizSubmision, EnhancedQuizSubmission],
    current_user: FirebaseUser = Depends(get_current_user),
    service: LearningPathService = Depends(get_service)
):
    """
    Completa uma missão específica de uma trilha de aprendizado.
    
    Args:
        path_id: ID da trilha de aprendizado
        mission_id: ID da missão dentro da trilha
        submission: Respostas do quiz
        current_user: Usuário autenticado
        
    Returns:
        Dict com resultado da missão (score, success, etc.)
    """
    try:
        # 🆕 DEBUG: Log do tipo de submission recebido
        logger.info(f"🔍 [DEBUG] Tipo de submission recebido: {type(submission).__name__}")
        logger.info(f"🔍 [DEBUG] Submission data: {submission}")
        logger.info(f"🔍 [DEBUG] Tem time_per_question: {hasattr(submission, 'time_per_question')}")
        logger.info(f"🔍 [DEBUG] Tem confidence_levels: {hasattr(submission, 'confidence_levels')}")
        
        # 🆕 Usar método com IA se submission for EnhancedQuizSubmission
        if hasattr(submission, 'time_per_question') and hasattr(submission, 'confidence_levels'):
            # É EnhancedQuizSubmission - usar IA
            logger.info(f"🤖 [DEBUG] Usando complete_mission_with_ai para usuário {current_user.uid}")
            result = await service.complete_mission_with_ai(
                user_id=current_user.uid,
                path_id=path_id,
                mission_id=mission_id,
                submission=submission
            )
        else:
            # É QuizSubmision normal - usar método tradicional
            logger.info(f"📝 [DEBUG] Usando complete_mission tradicional para usuário {current_user.uid}")
            result = await service.complete_mission(
                user_id=current_user.uid,
                path_id=path_id,
                mission_id=mission_id,
                submission=submission
            )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno ao completar missão: {str(e)}"
        )
