from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime, UTC
from enum import Enum


class RewardType(str, Enum): 
    DAILY_MISSION = "daily_mission"
    LEARNING_PATH_MODULE = "learning_path_module"
    LEARNING_PATH_COMPLETE = "learning_path_complete"
    STREAK_7_DAYS = "streak_7_days"
    STREAK_30_DAYS = "streak_30_days"
    PERFECT_SCORE = "perfect_score"
    FIRST_COMPLETION = "first_completion"
    LEVEL_UP = "level_up"


class Reward(BaseModel): 
    id: str 
    type: RewardType 
    title: str 
    description: str 
    points: int 
    xp: int = 0 
    badge_id: Optional[str] = None 
    requirements: Dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

class UserReward(BaseModel): 
    user_id: str 
    reward_id: Optional[str] = None  # Tornar opcional
    reward_type: Optional[str] = None  # Tornar opcional para evitar erro de null
    earned_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    points_earned: int = 0  # Tornar opcional com valor padrão
    xp_earned: int = 0 
    context: Dict[str, Any] = Field(default_factory=dict) # Missao, trilha, etc


class Badge(BaseModel): 
    id: Optional[str] = None  # Tornar opcional com fallback
    name: Optional[str] = None  # Tornar opcional com fallback
    description: Optional[str] = None  # Tornar opcional com fallback
    icon: Optional[str] = None  # Tornar opcional com fallback
    rarity: Optional[str] = None  # Tornar opcional com fallback
    color: Optional[str] = None  # Já opcional
    requirements: Dict[str, Any] = Field(default_factory=dict)


class UserBadge(BaseModel): 
    user_id: str 
    badge_id: Optional[str] = None  # Tornar opcional para evitar erro de null
    earned_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    context: Dict[str, Any] = Field(default_factory=dict) # Missao, trilha, etc