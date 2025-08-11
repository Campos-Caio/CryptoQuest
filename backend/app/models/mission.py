from pydantic import BaseModel, Field 
from typing import List, Dict 

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
    content_type: str 