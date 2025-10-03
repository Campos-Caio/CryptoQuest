from pydantic import BaseModel, Field 
from typing import List, Dict, Any, Optional 

class QuizOption(BaseModel): 
    text: str 

class QuizQuestion(BaseModel): 
    text: str
    options: List[QuizOption]
    correct_answer_index: int 

class Quiz(BaseModel): 
    id: str = Field(..., alias='_id')
    title: str 
    questions: List[QuizQuestion]

class Mission(BaseModel): 
    id: str = Field(...,alias='_id')
    title: str 
    description: str 
    type: str 
    reward_points: int 
    required_level: int 
    content_id: str 

class QuizSubmision(BaseModel): 
    """
    Representa o payload que o frontend envia ao submeter as respostas de um quiz.
    
    Attributes:
        answers (List[int]): Uma lista de inteiros, onde cada número é o 
                             índice da opção que o usuário selecionou para cada
                             pergunta, na ordem em que foram apresentadas.
    """
    answers: List[int]


class EnhancedQuizSubmission(BaseModel):
    """Submissão de quiz enriquecida com dados para IA"""
    answers: List[int] = Field(..., description="Respostas selecionadas")
    
    # 🆕 Dados comportamentais para IA
    time_per_question: List[float] = Field(default_factory=list, description="Tempo em segundos por pergunta")
    confidence_levels: List[float] = Field(default_factory=list, description="Nível de confiança (0-1) por pergunta")
    hints_used: List[int] = Field(default_factory=list, description="Dicas utilizadas por pergunta")
    attempts_per_question: List[int] = Field(default_factory=list, description="Tentativas por pergunta")
    session_metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadados da sessão")
    device_info: Optional[Dict[str, Any]] = Field(None, description="Informações do dispositivo") 