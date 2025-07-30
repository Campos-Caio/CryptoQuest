from pydantic import BaseModel, Field 
from typing import List 

# Model para uma unica opcao de resposta
class QuestionOption(BaseModel): 
    id: str
    text: str 
    score: int 

# Model para pergunta completa
class Question(BaseModel): 
    id: str 
    text: str 
    options: List[QuestionOption]

# Model para questionario completo que sera enviado ao Front 
class InitialQuestionnaire(BaseModel): 
    title: str 
    questions: List[Question]

# Model para resposta do usuario a uma unicao pergunta
class UserAnswer(BaseModel): 
    question_id: str 
    selected_option_id: str 

# Model para payload de submissao do questionario 
class QuestionnaireSubmission(BaseModel): 
    answers: List[UserAnswer]

# Model para o resultado que sera salvo no banco 
class KnowledgeProfile(BaseModel): 
    profile_name: str = Field(..., description="Ex: Iniciante, Entusiasta, MasterOfCrypto etc")
    score: int 
    learning_path_ids: List[str] = Field(..., description="Lista de IDs dos modulos da trilha inicial")