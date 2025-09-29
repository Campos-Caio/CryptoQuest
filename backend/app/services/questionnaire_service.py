from typing import Annotated
from fastapi import Depends
from app.models.questionnaire import * 
from app.repositories.user_repository import UserRepository, get_user_repository
class QuestionnaireService: 
    def __init__(self,user_repo: UserRepository): 
        self.user_repo = user_repo
        self.questions_map = {q.id: q for q in INITIAL_QUESTIONS.questions} 
    
    def get_initial_questionnaire(self) -> InitialQuestionnaire:
        """Retorna a estrutura do questionario inicial!"""
        return INITIAL_QUESTIONS 
    
    async def process_submission(self, uid: str, submission: QuestionnaireSubmission) -> KnowledgeProfile: 
        """Processa as respostas, calcula perfil e gera trilha"""
        total_score = 0 
        for answer in submission.answers: 
            question = self.questions_map.get(answer.question_id)
            if question: 
                for option in question.options: 
                    if option.id == answer.selected_option_id: 
                        total_score += option.score 
                        break 
        
        # Logica para definir o perfil, trilha e nível inicial baseado na pontuacao 
        if total_score <= 3: 
            profile_name = 'Explorador Curioso'
            learning_path_ids = ['fundamentos_dinheiro_bitcoin']
            initial_level = 1  # Nível inicial para iniciantes
        elif total_score <= 6: 
            profile_name = 'Iniciante Promissor'
            learning_path_ids = ['aprofundando_bitcoin_tecnologia']
            initial_level = 2  # Nível inicial para intermediários
        else: 
            profile_name = 'Entusiasta Preparado'
            learning_path_ids = ['bitcoin_ecossistema_financeiro']
            initial_level = 3  # Nível inicial para avançados

        knowledge_profile = KnowledgeProfile(
            profile_name=profile_name, 
            score = total_score, 
            learning_path_ids = learning_path_ids,
            initial_level = initial_level
        )

        # Dados a serem salvos no Firestore 
        update_data = {
            'knowledge_profile':  knowledge_profile.model_dump(), 
            'initial_answers':submission.model_dump(), 
            'has_completed_questionnaire':True,
            'level': initial_level  # Definir nível inicial baseado no questionário
        }

        # Atualiza o doc do User 
        self.user_repo.update_user_Profile(uid, update_data)

        return knowledge_profile 

def get_questionnaire_service(
        user_repo: Annotated[UserRepository, Depends(get_user_repository)]
) -> QuestionnaireService: 
    return QuestionnaireService(user_repo=user_repo)

INITIAL_QUESTIONS = InitialQuestionnaire(
    title="Questionário de Nivelamento - CryptoQuest",
    questions=[
        Question(
            id="q1",
            text="Qual seu nível de familiaridade com criptomoedas?",
            options=[
                QuestionOption(id="q1a", text="Nunca ouvi falar ou sei muito pouco.", score=1),
                QuestionOption(id="q1b", text="Já ouvi falar, mas não sei como funciona.", score=2),
                QuestionOption(id="q1c", text="Entendo os conceitos básicos (ex: Bitcoin).", score=3),
                QuestionOption(id="q1d", text="Já investi ou estudei a fundo.", score=4),
            ],
        ),
        Question(
            id="q2",
            text="O que você entende por 'Blockchain'?",
            options=[
                QuestionOption(id="q2a", text="Não sei o que é.", score=1),
                QuestionOption(id="q2b", text="É um tipo de moeda digital.", score=2),
                QuestionOption(id="q2c", text="É um 'livro-razão' digital, público e distribuído.", score=3),
                QuestionOption(id="q2d", text="É uma tecnologia para criar contratos inteligentes.", score=4),
            ],
        ),
        # Adicione mais perguntas aqui
    ],
)


            
    
                        
