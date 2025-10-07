from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timedelta
from app.models.ranking import Ranking, UserRankingStats
from app.models.user import FirebaseUser
from app.dependencies.auth import get_current_user
from app.services.ranking_service import RankingService, get_ranking_service
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ranking", tags=["ranking"])

@router.get("/global", response_model=Ranking)
async def get_global_ranking(
    limit: int = 100,
    ranking_service: RankingService = Depends(get_ranking_service)
):
    """Busca ranking global"""
    return await ranking_service.generate_global_ranking(limit)

@router.get("/weekly", response_model=Ranking)
async def get_weekly_ranking(
    ranking_service: RankingService = Depends(get_ranking_service)
):
    """Busca ranking semanal"""
    week_start = datetime.now() - timedelta(days=7)
    return await ranking_service.generate_weekly_ranking(week_start)

@router.get("/user/{user_id}/stats", response_model=UserRankingStats)
async def get_user_ranking_stats(
    user_id: str,
    current_user: FirebaseUser = Depends(get_current_user),
    ranking_service: RankingService = Depends(get_ranking_service)
):
    """Busca estatísticas de ranking do usuário"""
    if current_user.uid != user_id:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    return await ranking_service.get_user_ranking_stats(user_id)
