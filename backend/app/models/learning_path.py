from pydantic import BaseModel, Field
from typing import List, Optional, Union
from datetime import datetime, UTC
from enum import Enum


class DifficultyLevel(str, Enum): 
    BEGINNER = 'beginner' 
    INTERMEDIATE = 'intermediate' 
    ADVANCED = 'advanced' 

class MissionReference(BaseModel): 
    """Referencia a uma missao em um modulo da trilha"""
    id:  str = Field(..., description='ID da missão')
    mission_id: str = Field(..., description='ID real do quiz/missão')
    order: int = Field(default=1, description='Ordem da missão no modulo')
    required_score: int = Field(default=70, description='Pontuação necessária para completar a missão')

class Module(BaseModel): 
    """Modulo de uma trilha de aprendizado"""
    id: str = Field(..., description='ID unico do modulo')
    name: str = Field(..., description='Nome do modulo')
    description: str = Field(..., description='Descrição do modulo')
    order: int = Field(..., description='Ordem do modulo na trilha')
    missions: List[MissionReference] = Field(default_factory=list, description='Missões do modulo')

class LearningPath(BaseModel):
    """Trilha de aprendizado completa"""
    id: str = Field(..., description="ID único da trilha")
    name: str = Field(..., description="Nome da trilha")
    description: str = Field(..., description="Descrição da trilha")
    difficulty: DifficultyLevel = Field(..., description="Nível de dificuldade")
    estimated_duration: str = Field(..., description="Duração estimada")
    prerequisites: List[str] = Field(default_factory=list, description="Pré-requisitos")
    modules: List[Module] = Field(default_factory=list, description="Módulos da trilha")
    is_active: bool = Field(default=True, description="Se a trilha está ativa")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Data de criação")
    updated_at: Optional[datetime] = Field(default=None, description="Data de atualização")

class UserPathProgress(BaseModel):
    """Progresso do usuário em uma trilha"""
    user_id: str = Field(..., description="ID do usuário")
    path_id: str = Field(..., description="ID da trilha")
    started_at: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Data de início")
    completed_at: Optional[datetime] = Field(default=None, description="Data de conclusão")
    current_module_id: Optional[str] = Field(default=None, description="Módulo atual")
    completed_modules: List[str] = Field(default_factory=list, description="Módulos concluídos")
    completed_missions: List[str] = Field(default_factory=list, description="Missões concluídas")
    total_score: int = Field(default=0, description="Pontuação total")
    progress_percentage: float = Field(default=0.0, description="Percentual de progresso")

class LearningPathResponse(BaseModel):
    """Resposta da API com detalhes da trilha e progresso"""
    path: LearningPath
    progress: Optional[UserPathProgress] = None
    stats: dict = Field(default_factory=dict, description="Estatísticas da trilha")