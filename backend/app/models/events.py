"""
Modelos de eventos para o sistema de recompensas.
Define a estrutura base de eventos que serão processados pelo sistema.
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from enum import Enum


class EventType(str, Enum):
    """Tipos de eventos do sistema"""
    MISSION_COMPLETED = "mission_completed"
    LEVEL_UP = "level_up"
    STREAK_UPDATED = "streak_updated"
    POINTS_EARNED = "points_earned"
    LEARNING_PATH_COMPLETED = "learning_path_completed"
    QUIZ_COMPLETED = "quiz_completed"
<<<<<<< HEAD
    MODULE_COMPLETED = "module_completed"
=======
>>>>>>> ceffef1 (feat: Implementacao final do sistema de recompensas)


class BaseEvent(BaseModel):
    """Evento base com campos comuns"""
    event_type: EventType
    user_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    context: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        use_enum_values = True


class MissionCompletedEvent(BaseEvent):
    """Evento disparado quando uma missão é completada"""
    event_type: EventType = EventType.MISSION_COMPLETED
    mission_id: str
    score: float
    mission_type: str  # 'daily', 'learning_path', etc.
    points_earned: int = 0
    xp_earned: int = 0


class LevelUpEvent(BaseEvent):
    """Evento disparado quando usuário sobe de nível"""
    event_type: EventType = EventType.LEVEL_UP
    old_level: int
    new_level: int
    points_required: int
    points_earned: int = 0  # Tornar opcional com valor padrão


class StreakUpdatedEvent(BaseEvent):
    """Evento disparado quando streak é atualizado"""
    event_type: EventType = EventType.STREAK_UPDATED
    current_streak: int
    previous_streak: int
    streak_type: str  # 'daily', 'weekly', etc.


class PointsEarnedEvent(BaseEvent):
    """Evento disparado quando pontos são ganhos"""
    event_type: EventType = EventType.POINTS_EARNED
    points_earned: int
    total_points: int
    source: str  # 'mission', 'quiz', 'bonus', etc.


class LearningPathCompletedEvent(BaseEvent):
    """Evento disparado quando trilha de aprendizado é completada"""
    event_type: EventType = EventType.LEARNING_PATH_COMPLETED
<<<<<<< HEAD
    learning_path_id: str
    learning_path_name: str
    total_missions: int
    completed_missions: int
=======
    path_id: str
    total_score: float
    modules_completed: int
    points_earned: int
>>>>>>> ceffef1 (feat: Implementacao final do sistema de recompensas)


class QuizCompletedEvent(BaseEvent):
    """Evento disparado quando quiz é completado"""
    event_type: EventType = EventType.QUIZ_COMPLETED
    quiz_id: str
    score: float
<<<<<<< HEAD
    learning_path_id: Optional[str] = None
    mission_id: Optional[str] = None


class ModuleCompletedEvent(BaseEvent):
    """Evento disparado quando módulo de trilha é completado"""
    event_type: EventType = EventType.MODULE_COMPLETED
    learning_path_id: str
    module_id: str
    module_name: str
=======
    correct_answers: int
    total_questions: int
    points_earned: int
>>>>>>> ceffef1 (feat: Implementacao final do sistema de recompensas)


# Union type para todos os eventos
from typing import Union

Event = Union[
    MissionCompletedEvent,
    LevelUpEvent,
    StreakUpdatedEvent,
    PointsEarnedEvent,
    LearningPathCompletedEvent,
<<<<<<< HEAD
    QuizCompletedEvent,
    ModuleCompletedEvent
=======
    QuizCompletedEvent
>>>>>>> ceffef1 (feat: Implementacao final do sistema de recompensas)
]
