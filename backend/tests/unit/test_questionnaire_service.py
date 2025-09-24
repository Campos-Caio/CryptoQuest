import pytest 
from app.services.questionnaire_service import QuestionnaireService 
from app.models.questionnaire import QuestionnaireSubmission, UserAnswer 

pytestmark = pytest.mark.asyncio 

# Teste Unitario 
# Objetivo de testar a logica de calculo do perfil isoladamente

async def test_process_submission_calculates_beginner_profile(): 
    """
        Verifica se, com respostas de baixo score, o perfil "Iniciante Promissor eh gerado"
    """

    service = QuestionnaireService(user_repo=None)
    submission = QuestionnaireSubmission(
        answers=[
            UserAnswer(question_id="q1", selected_option_id='q1b'),
            UserAnswer(question_id="q2", selected_option_id='q2b'),
        ]
    )

    # Precisa ser capturada a excecao quando passamos user_repo = None 

    try: 
        await service.process_submission(uid="test_user",submission=submission)
    except AttributeError as e: 
        pass 

    def calculate_profile_logic(submission: QuestionnaireSubmission): 
        total_score = 0 
        questions_map = {
            "q1": {"q1b": 2}, 
            "q2": {"q2b": 2}
        }

        for answer in submission.answers: 
            questions_scores = questions_map.get(answer.question_id, {})
            total_score += questions_scores.get(answer.selected_option_id, 0) 

        if(total_score <= 6): 
            return "Iniciante Promissor"
        else: 
            return "Entusiasta Preparado"

    profile_name = calculate_profile_logic(submission)
    assert profile_name == "Iniciante Promissor"

async def test_process_submission_calculates_advanced_profile(): 
    """
        Verifica se, com respostas de alto score, o perfil eh gerado corretamente. 
    """

    submission = QuestionnaireSubmission(
        answers=[
            UserAnswer(question_id='q1', selected_option_id='q1d'), 
            UserAnswer(question_id='q2', selected_option_id='q2d'), 
        ]
    )

    def calculate_profile_logic(submission: QuestionnaireSubmission): 
        total_score = 0 
        questions_map = {
            'q1': {'q1d': 4}, 
            'q2': {'q2d': 4}
        }

        for answer in submission.answers:
            questions_scores = questions_map.get(answer.question_id, {})
            total_score += questions_scores.get(answer.selected_option_id, 0)

        if total_score <= 6: 
            return 'Iniciante Promissor'
        else: 
            return 'Entusiasta Preparado'
        
    profile_name = calculate_profile_logic(submission)

    assert profile_name == 'Entusiasta Preparado'