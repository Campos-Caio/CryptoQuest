from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, UTC
from enum import Enum


class RankingType(str, Enum): 
    GLOBAL = "global"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    LEVEL_BASED = "level_based"
    LEARNING_PATH = "learning_path"


class RankingEntry(BaseModel):
    user_id: str
    name: str
    email: str
    points: int
    xp: int
    level: int
    rank: int 
    avatar_url: Optional[str] = None
    badges: List[str] = Field(default_factory=list)
    last_activity: datetime

class Ranking(BaseModel): 
    type: RankingType
    period: str 
    entries: List["RankingEntry"] = Field(default_factory=list)
    total_users: int 
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    context: Dict[str, Any] = Field(default_factory=dict)

class UserRankingStats(BaseModel): 
    user_id: str
    global_rank: int
    weekly_rank: int
    monthly_rank: int
    level_rank: int
    total_users: int 
    percentile: float 
    last_update: datetime = Field(default_factory=lambda: datetime.now(UTC))
    