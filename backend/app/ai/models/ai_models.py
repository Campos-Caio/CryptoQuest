"""
Modelos de dados para o sistema de IA do CryptoQuest.
"""
from datetime import datetime, UTC
from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field
from enum import Enum


class LearningStyle(str, Enum):
    """Estilos de aprendizado identificados pela IA"""
    VISUAL = "visual"
    AUDITORY = "auditory"
    KINESTHETIC = "kinesthetic"
    READING_WRITING = "reading_writing"
    MIXED = "mixed"


class DifficultyLevel(str, Enum):
    """Níveis de dificuldade"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class KnowledgeDomain(str, Enum):
    """Domínios de conhecimento em criptomoedas"""
    BITCOIN_BASICS = "bitcoin_basics"
    BLOCKCHAIN_TECHNOLOGY = "blockchain_technology"
    CRYPTO_TRADING = "crypto_trading"
    DEFI = "defi"
    NFT = "nft"
    SMART_CONTRACTS = "smart_contracts"
    CRYPTO_SECURITY = "crypto_security"
    REGULATION = "regulation"


class EnhancedQuizSubmission(BaseModel):
    """Submissão de quiz enriquecida com dados para IA"""
    answers: List[int] = Field(..., description="Respostas selecionadas")
    time_per_question: List[float] = Field(default_factory=list, description="Tempo em segundos por pergunta")
    confidence_levels: List[float] = Field(default_factory=list, description="Nível de confiança (0-1) por pergunta")
    hints_used: List[int] = Field(default_factory=list, description="Dicas utilizadas por pergunta")
    attempts_per_question: List[int] = Field(default_factory=list, description="Tentativas por pergunta")
    session_metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadados da sessão")
    device_info: Optional[Dict[str, Any]] = Field(None, description="Informações do dispositivo")


class KnowledgeDomainProfile(BaseModel):
    """Domínio específico de conhecimento do usuário"""
    domain: str = Field(..., description="Domínio de conhecimento")
    proficiency_level: float = Field(..., description="Nível de proficiência (0-1)")
    confidence: float = Field(..., description="Confiança na avaliação (0-1)")
    last_updated: datetime = Field(default_factory=lambda: datetime.now(UTC))
    evidence_sources: List[str] = Field(default_factory=list, description="IDs das missões/quizzes")
    total_questions: int = Field(default=0, description="Total de questões respondidas")
    correct_answers: int = Field(default=0, description="Respostas corretas")
    average_response_time: float = Field(default=0.0, description="Tempo médio de resposta")
    difficulty_preference: float = Field(default=0.5, description="Preferência de dificuldade (0-1)")


class UserKnowledgeProfile(BaseModel):
    """Perfil de conhecimento completo do usuário"""
    user_id: str = Field(..., description="ID do usuário")
    domains: Dict[str, KnowledgeDomainProfile] = Field(default_factory=dict)
    learning_style: LearningStyle = Field(default=LearningStyle.MIXED)
    pace_preference: str = Field(default="medium", description="slow, medium, fast")
    difficulty_preference: float = Field(default=0.5, description="Preferência geral de dificuldade")
    engagement_score: float = Field(default=0.0, description="Score de engajamento (0-1)")
    retention_rate: float = Field(default=0.0, description="Taxa de retenção de conhecimento")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class LearningPattern(BaseModel):
    """Padrão de aprendizado identificado pela IA"""
    pattern_type: str = Field(..., description="Tipo do padrão")
    strength: float = Field(..., description="Força do padrão (0-1)")
    frequency: int = Field(..., description="Frequência de ocorrência")
    last_observed: datetime = Field(default_factory=lambda: datetime.now(UTC))
    context: Dict[str, Any] = Field(default_factory=dict, description="Contexto do padrão")


class KnowledgeGap(BaseModel):
    """Gap de conhecimento identificado pela IA"""
    domain: str = Field(..., description="Domínio com gap")
    gap_severity: float = Field(..., description="Severidade do gap (0-1)")
    recommended_content: List[str] = Field(default_factory=list, description="Conteúdo recomendado")
    priority: int = Field(default=1, description="Prioridade (1-5)")
    identified_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ContentRecommendation(BaseModel):
    """Recomendação de conteúdo gerada pela IA"""
    content_id: str = Field(..., description="ID do conteúdo")
    content_type: str = Field(..., description="Tipo: quiz, lesson, practice")
    relevance_score: float = Field(..., description="Score de relevância (0-1)")
    difficulty_level: DifficultyLevel = Field(..., description="Nível de dificuldade")
    estimated_time: int = Field(..., description="Tempo estimado em minutos")
    reasoning: str = Field(..., description="Justificativa da recomendação")
    learning_objectives: List[str] = Field(default_factory=list, description="Objetivos de aprendizado")
    title: Optional[str] = Field(None, description="Título amigável do conteúdo")


class AdaptiveLearningPlan(BaseModel):
    """Plano de aprendizado adaptativo gerado pela IA"""
    user_id: str = Field(..., description="ID do usuário")
    current_level: int = Field(..., description="Nível atual")
    target_level: int = Field(..., description="Nível alvo")
    learning_path: List[str] = Field(default_factory=list, description="Caminho de aprendizado")
    estimated_completion_time: int = Field(..., description="Tempo estimado em dias")
    confidence_score: float = Field(..., description="Confiança no plano (0-1)")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class MLModelMetrics(BaseModel):
    """Métricas de performance dos modelos de ML"""
    model_name: str = Field(..., description="Nome do modelo")
    accuracy: float = Field(..., description="Precisão do modelo")
    precision: float = Field(..., description="Precisão")
    recall: float = Field(..., description="Recall")
    f1_score: float = Field(..., description="F1 Score")
    training_samples: int = Field(..., description="Amostras de treino")
    last_trained: datetime = Field(default_factory=lambda: datetime.now(UTC))
    version: str = Field(default="1.0", description="Versão do modelo")


class AIPrediction(BaseModel):
    """Predição gerada pela IA"""
    prediction_type: str = Field(..., description="Tipo da predição")
    value: Union[float, int, str, bool] = Field(..., description="Valor predito")
    confidence: float = Field(..., description="Confiança na predição (0-1)")
    reasoning: str = Field(..., description="Justificativa da predição")
    model_used: str = Field(..., description="Modelo utilizado")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class UserBehavioralData(BaseModel):
    """Dados comportamentais coletados do usuário"""
    user_id: str = Field(..., description="ID do usuário")
    session_id: str = Field(..., description="ID da sessão")
    quiz_id: str = Field(..., description="ID do quiz")
    submission_data: Dict[str, Any] = Field(..., description="Dados da submissão")
    performance_metrics: Dict[str, Any] = Field(default_factory=dict, description="Métricas de performance")
    collected_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class AIInsight(BaseModel):
    """Insight gerado pela IA sobre o usuário"""
    user_id: str = Field(..., description="ID do usuário")
    insight_type: str = Field(..., description="Tipo do insight")
    title: str = Field(..., description="Título do insight")
    description: str = Field(..., description="Descrição detalhada")
    confidence: float = Field(..., description="Confiança no insight (0-1)")
    actionable: bool = Field(default=True, description="Se o insight é acionável")
    recommendations: List[str] = Field(default_factory=list, description="Recomendações baseadas no insight")
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    expires_at: Optional[datetime] = Field(None, description="Data de expiração do insight")


class LearningSession(BaseModel):
    """Dados de uma sessão de aprendizado"""
    session_id: str = Field(..., description="ID da sessão")
    user_id: str = Field(..., description="ID do usuário")
    start_time: datetime = Field(..., description="Início da sessão")
    end_time: Optional[datetime] = Field(None, description="Fim da sessão")
    quizzes_completed: List[str] = Field(default_factory=list, description="IDs dos quizzes completados")
    total_time_spent: float = Field(default=0.0, description="Tempo total em segundos")
    average_confidence: float = Field(default=0.0, description="Confiança média")
    learning_style_detected: Optional[LearningStyle] = Field(None, description="Estilo detectado")
    difficulty_adaptations: List[Dict[str, Any]] = Field(default_factory=list, description="Adaptações de dificuldade")
