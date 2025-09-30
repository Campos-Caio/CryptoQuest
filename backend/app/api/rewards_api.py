from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.models.reward import UserReward, UserBadge, Badge
from app.models.user import FirebaseUser
from app.dependencies.auth import get_current_user
from app.services.reward_service import RewardService, get_reward_service
from app.repositories.reward_repository import RewardRepository, get_reward_repository
from app.repositories.badge_repository import BadgeRepository, get_badge_repository
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/rewards", tags=["rewards"])

@router.get("/user/{user_id}/history", response_model=List[UserReward])
async def get_user_rewards_history(
    user_id: str,
    current_user: FirebaseUser = Depends(get_current_user),
    reward_repo: RewardRepository = Depends(get_reward_repository)
):
    """Busca histórico de recompensas do usuário"""
    try:
        if current_user.uid != user_id:
            raise HTTPException(status_code=403, detail="Acesso negado")
        
        rewards = reward_repo.get_user_rewards(user_id)
        logger.info(f"Histórico de recompensas recuperado para usuário {user_id}: {len(rewards)} itens")
        return rewards
    except Exception as e:
        logger.error(f"Erro ao buscar histórico de recompensas: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/user/{user_id}/badges", response_model=List[UserBadge])
async def get_user_badges(
    user_id: str,
    current_user: FirebaseUser = Depends(get_current_user),
    badge_repo: BadgeRepository = Depends(get_badge_repository)
):
    """Busca badges do usuário usando o novo sistema"""
    try:
        if current_user.uid != user_id:
            raise HTTPException(status_code=403, detail="Acesso negado")
        
        badges = badge_repo.get_user_badges(user_id)
        logger.info(f"Badges do usuário recuperados para usuário {user_id}: {len(badges)} itens")
        return badges
    except Exception as e:
        logger.error(f"Erro ao buscar badges do usuário: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/badges", response_model=List[Badge])
async def get_all_badges(
    badge_repo: BadgeRepository = Depends(get_badge_repository)
):
    """Busca todos os badges disponíveis usando o novo sistema"""
    try:
        badges = badge_repo.get_all_badges()
        logger.info(f"Badges disponíveis recuperados: {len(badges)} itens")
        return badges
    except Exception as e:
        logger.error(f"Erro ao buscar badges disponíveis: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/user/{user_id}/available-badges", response_model=List[Badge])
async def get_available_badges_for_user(
    user_id: str,
    current_user: FirebaseUser = Depends(get_current_user),
    badge_repo: BadgeRepository = Depends(get_badge_repository)
):
    """Busca badges disponíveis para um usuário específico (que ainda não conquistou)"""
    try:
        if current_user.uid != user_id:
            raise HTTPException(status_code=403, detail="Acesso negado")
        
        badges = badge_repo.get_available_badges_for_user(user_id)
        logger.info(f"Badges disponíveis para usuário {user_id}: {len(badges)} itens")
        return badges
    except Exception as e:
        logger.error(f"Erro ao buscar badges disponíveis para usuário: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.post("/award/mission")
async def award_mission_completion(
    user_id: str,
    mission_id: str,
    score: float,
    mission_type: str = "daily",
    current_user: FirebaseUser = Depends(get_current_user),
    reward_service: RewardService = Depends(get_reward_service)
):
    """Concede recompensas por conclusão de missão (sistema legado)"""
    try:
        if current_user.uid != user_id:
            raise HTTPException(status_code=403, detail="Acesso negado")
        
        return await reward_service.award_mission_completion(user_id, mission_id, score, mission_type)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao conceder recompensas por missão: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/user/{user_id}/badge-stats")
async def get_user_badge_stats(
    user_id: str,
    current_user: FirebaseUser = Depends(get_current_user),
    badge_repo: BadgeRepository = Depends(get_badge_repository)
):
    """Busca estatísticas de badges do usuário"""
    try:
        if current_user.uid != user_id:
            raise HTTPException(status_code=403, detail="Acesso negado")
        
        stats = await badge_repo.get_user_badge_stats(user_id)
        logger.info(f"Estatísticas de badges recuperadas para usuário {user_id}")
        return stats
    except Exception as e:
        logger.error(f"Erro ao buscar estatísticas de badges: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/badges/{badge_id}")
async def get_badge_by_id(
    badge_id: str,
    badge_repo: BadgeRepository = Depends(get_badge_repository)
):
    """Busca um badge específico por ID"""
    try:
        badge = badge_repo.get_badge_by_id(badge_id)
        if not badge:
            raise HTTPException(status_code=404, detail="Badge não encontrado")
        
        logger.info(f"Badge {badge_id} recuperado com sucesso")
        return badge
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar badge {badge_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")
