from typing import Annotated
from fastapi import Depends
from app.models.questionnaire import * 
from app.repositories.user_repository import UserRepository, get_user_repository
from app.core.firebase import get_firestore_db_async
from google.cloud.firestore_v1 import SERVER_TIMESTAMP
import logging
from datetime import datetime, UTC

logger = logging.getLogger(__name__)
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
        
        # Logica para definir o perfil, trilha e nível inicial baseado na pontuacao (10-40)
        if total_score <= 15: 
            profile_name = 'Explorador Curioso'
            learning_path_ids = ['fundamentos_dinheiro_bitcoin']
            initial_level = 1  # Nível inicial para iniciantes
        elif total_score <= 22: 
            profile_name = 'Iniciante Promissor'
            learning_path_ids = ['fundamentos_dinheiro_bitcoin', 'aprofundando_bitcoin_tecnologia']
            initial_level = 2  # Nível inicial para intermediários
        elif total_score <= 28:
            profile_name = 'Estudante Dedicado'
            learning_path_ids = ['aprofundando_bitcoin_tecnologia', 'bitcoin_ecossistema_financeiro']
            initial_level = 3  # Conhecimento sólido
        elif total_score <= 34:
            profile_name = 'Entusiasta Avançado'
            learning_path_ids = ['bitcoin_ecossistema_financeiro', 'ethereum_developer_path']
            initial_level = 4  # Nível avançado
        else: 
            profile_name = 'Mestre Crypto'
            learning_path_ids = ['ethereum_developer_path', 'defi_master_path']
            initial_level = 5  # Nível expert

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
        self.user_repo.update_user_profile(uid, update_data)

        # ✅ FASE 1: Integração com IA - Criar perfil inicial de conhecimento
        await self._create_ai_knowledge_profile(uid, knowledge_profile, submission)

        return knowledge_profile 
    
    async def _create_ai_knowledge_profile(self, uid: str, knowledge_profile: KnowledgeProfile, submission: QuestionnaireSubmission):
        """Cria perfil inicial de conhecimento para o sistema de IA baseado no questionário"""
        try:
            db = await get_firestore_db_async()
            
            # Mapear score do questionário para domínios específicos
            domains = self._map_questionnaire_to_domains(knowledge_profile.score, submission)
            
            # Detectar estilo de aprendizado baseado nas respostas
            learning_style = self._detect_learning_style_from_questionnaire(submission)
            
            # Criar perfil de conhecimento inicial para IA
            ai_profile = {
                "user_id": uid,
                "domains": domains,
                "learning_style": learning_style,
                "engagement_score": 0.7,  # Score inicial baseado no questionário
                "total_questions": 0,  # Ainda não completou nenhuma questão
                "average_response_time": 0.0,
                "confidence_levels": [],
                "difficulty_preferences": self._map_difficulty_from_score(knowledge_profile.score),
                "recommended_paths": knowledge_profile.learning_path_ids,
                "initial_questionnaire_score": knowledge_profile.score,
                "initial_level": knowledge_profile.initial_level,
                "profile_name": knowledge_profile.profile_name,
                "questionnaire_answers": submission.model_dump(),  # Salvar respostas originais
                "created_at": SERVER_TIMESTAMP,
                "updated_at": SERVER_TIMESTAMP,
                "data_source": "initial_questionnaire"  # Identifica que vem do questionário
            }
            
            # Salvar no Firestore na coleção ai_knowledge_profiles
            profile_ref = db.collection("ai_knowledge_profiles").document(uid)
            await profile_ref.set(ai_profile)
            
            logger.info(f"✅ Perfil de IA criado para usuário {uid} baseado no questionário inicial")
            logger.info(f"   Score: {knowledge_profile.score}, Domínios: {list(domains.keys())}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar perfil de IA para usuário {uid}: {e}")
            # Não re-lançar a exceção para não quebrar o fluxo do questionário
    
    def _map_questionnaire_to_domains(self, score: int, submission: QuestionnaireSubmission) -> dict:
        """Mapeia respostas do questionário para domínios de conhecimento"""
        domains = {}
        
        # Calcular proficiência base baseada no score total
        if score <= 3:
            base_proficiency = 0.2  # Iniciante
        elif score <= 6:
            base_proficiency = 0.5  # Intermediário
        else:
            base_proficiency = 0.8  # Avançado
        
        # Analisar respostas específicas para mapear domínios
        for answer in submission.answers:
            question_id = answer.question_id
            question = self.questions_map.get(question_id)
            
            if question:
                # Encontrar a resposta selecionada para obter o score
                selected_score = 0
                for option in question.options:
                    if option.id == answer.selected_option_id:
                        selected_score = option.score
                        break
                
                # Mapear questões específicas para domínios baseado no ID da questão
                if question_id == "q1":  # Questão sobre familiaridade com criptomoedas
                    domains["bitcoin_basics"] = {
                        "proficiency_level": min(1.0, selected_score / 4.0),
                        "questions_answered": 1,
                        "confidence_score": selected_score / 4.0,
                        "last_activity": None,
                        "source": "questionnaire_q1"
                    }
                elif question_id == "q2":  # Questão sobre blockchain
                    domains["blockchain_technology"] = {
                        "proficiency_level": min(1.0, selected_score / 4.0),
                        "questions_answered": 1,
                        "confidence_score": selected_score / 4.0,
                        "last_activity": None,
                        "source": "questionnaire_q2"
                    }
                elif question_id == "q3":  # Questão sobre experiência em trading
                    domains["crypto_trading"] = {
                        "proficiency_level": min(1.0, selected_score / 4.0),
                        "questions_answered": 1,
                        "confidence_score": selected_score / 4.0,
                        "last_activity": None,
                        "source": "questionnaire_q3"
                    }
                elif question_id == "q4":  # Questão sobre segurança e carteiras
                    domains["wallet_security"] = {
                        "proficiency_level": min(1.0, selected_score / 4.0),
                        "questions_answered": 1,
                        "confidence_score": selected_score / 4.0,
                        "last_activity": None,
                        "source": "questionnaire_q4"
                    }
                elif question_id == "q5":  # Questão sobre DeFi
                    domains["defi_protocols"] = {
                        "proficiency_level": min(1.0, selected_score / 4.0),
                        "questions_answered": 1,
                        "confidence_score": selected_score / 4.0,
                        "last_activity": None,
                        "source": "questionnaire_q5"
                    }
                elif question_id == "q6":  # Questão sobre smart contracts
                    domains["smart_contracts"] = {
                        "proficiency_level": min(1.0, selected_score / 4.0),
                        "questions_answered": 1,
                        "confidence_score": selected_score / 4.0,
                        "last_activity": None,
                        "source": "questionnaire_q6"
                    }
                elif question_id == "q7":  # Questão sobre NFTs
                    domains["nfts_tokens"] = {
                        "proficiency_level": min(1.0, selected_score / 4.0),
                        "questions_answered": 1,
                        "confidence_score": selected_score / 4.0,
                        "last_activity": None,
                        "source": "questionnaire_q7"
                    }
        
        # Garantir que pelo menos o domínio bitcoin_basics existe (é fundamental)
        if "bitcoin_basics" not in domains:
            domains["bitcoin_basics"] = {
                "proficiency_level": base_proficiency,
                "questions_answered": 1,
                "confidence_score": 0.7,
                "last_activity": None,
                "source": "questionnaire_default"
            }
        
        # Se há conhecimento sobre blockchain, adicionar domínios relacionados
        if "blockchain_technology" in domains:
            if domains["blockchain_technology"]["proficiency_level"] >= 0.6:
                # Se tem bom conhecimento de blockchain, assumir interesse em cripto trading
                domains["crypto_trading"] = {
                    "proficiency_level": max(0.3, base_proficiency * 0.7),
                    "questions_answered": 0,
                    "confidence_score": 0.5,
                    "last_activity": None,
                    "source": "questionnaire_inferred"
                }
        
        return domains
    
    def _detect_learning_style_from_questionnaire(self, submission: QuestionnaireSubmission) -> str:
        """Detecta estilo de aprendizado baseado nas respostas do questionário"""
        # Extrair resposta específica da Q10 (estilo de aprendizado)
        q10_answer = None
        q8_answer = None  # Objetivo principal
        
        for answer in submission.answers:
            if answer.question_id == "q10":
                q10_answer = answer.selected_option_id
            elif answer.question_id == "q8":
                q8_answer = answer.selected_option_id
        
        # Se respondeu Q10, usar diretamente
        if q10_answer:
            if q10_answer == "q10a":
                return "analytical"  # Prefere ler textos
            elif q10_answer == "q10b":
                return "visual"  # Prefere vídeos
            elif q10_answer == "q10c":
                return "hands_on"  # Prefere praticar
            elif q10_answer == "q10d":
                return "mixed"  # Combina métodos
        
        # Fallback: usar objetivo (Q8) para inferir estilo
        if q8_answer:
            if q8_answer == "q8a":
                return "analytical"  # Quer entender conceito = teórico
            elif q8_answer == "q8b":
                return "visual"  # Investir = precisa ver gráficos/dados
            elif q8_answer == "q8c":
                return "hands_on"  # Desenvolver = precisa praticar
            elif q8_answer == "q8d":
                return "mixed"  # Profissional = balanceado
        
        # Fallback final: usar score geral
        actual_score = 0
        for answer in submission.answers:
            question = self.questions_map.get(answer.question_id)
            if question:
                for option in question.options:
                    if option.id == answer.selected_option_id:
                        actual_score += option.score
                        break
        
        confidence_percentage = actual_score / 40.0 if actual_score > 0 else 0.5
        
        if confidence_percentage >= 0.75:
            return "analytical"
        elif confidence_percentage >= 0.5:
            return "mixed"
        else:
            return "visual"
    
    def _map_difficulty_from_score(self, score: int) -> dict:
        """Mapeia pontuação para preferências de dificuldade (score range: 10-40)"""
        if score <= 15:
            return {
                "preferred_level": 1,
                "challenge_threshold": 0.6,
                "comfort_zone": "beginner"
            }
        elif score <= 22:
            return {
                "preferred_level": 2,
                "challenge_threshold": 0.7,
                "comfort_zone": "intermediate"
            }
        elif score <= 28:
            return {
                "preferred_level": 3,
                "challenge_threshold": 0.8,
                "comfort_zone": "intermediate-advanced"
            }
        elif score <= 34:
            return {
                "preferred_level": 4,
                "challenge_threshold": 0.9,
                "comfort_zone": "advanced"
            }
        else:
            return {
                "preferred_level": 5,
                "challenge_threshold": 1.0,
                "comfort_zone": "expert"
            }

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
                QuestionOption(id="q2b", text="É uma tecnologia, mas não sei como funciona.", score=2),
                QuestionOption(id="q2c", text="É um 'livro-razão' digital, público e distribuído.", score=3),
                QuestionOption(id="q2d", text="Entendo profundamente e sei como funciona tecnicamente.", score=4),
            ],
        ),
        Question(
            id="q3",
            text="Você já comprou, vendeu ou negociou criptomoedas?",
            options=[
                QuestionOption(id="q3a", text="Nunca fiz nenhuma transação.", score=1),
                QuestionOption(id="q3b", text="Já fiz algumas transações básicas.", score=2),
                QuestionOption(id="q3c", text="Faço transações regularmente.", score=3),
                QuestionOption(id="q3d", text="Negocio ativamente e uso estratégias.", score=4),
            ],
        ),
        Question(
            id="q4",
            text="Como você guardaria (ou guarda) suas criptomoedas com segurança?",
            options=[
                QuestionOption(id="q4a", text="Não sei como guardar de forma segura.", score=1),
                QuestionOption(id="q4b", text="Deixaria em uma exchange (corretora).", score=2),
                QuestionOption(id="q4c", text="Usaria uma carteira digital no celular.", score=3),
                QuestionOption(id="q4d", text="Hardware wallet ou cold storage.", score=4),
            ],
        ),
        Question(
            id="q5",
            text="O que você sabe sobre DeFi (Finanças Descentralizadas)?",
            options=[
                QuestionOption(id="q5a", text="Nunca ouvi falar.", score=1),
                QuestionOption(id="q5b", text="Já ouvi o termo, mas não sei o que é.", score=2),
                QuestionOption(id="q5c", text="Sei que são serviços financeiros sem bancos.", score=3),
                QuestionOption(id="q5d", text="Já usei protocolos DeFi (lending, DEX, etc).", score=4),
            ],
        ),
        Question(
            id="q6",
            text="O que são 'Smart Contracts' (Contratos Inteligentes)?",
            options=[
                QuestionOption(id="q6a", text="Não sei o que são.", score=1),
                QuestionOption(id="q6b", text="São contratos digitais comuns.", score=2),
                QuestionOption(id="q6c", text="Programas auto-executáveis na blockchain.", score=3),
                QuestionOption(id="q6d", text="Conheço e sei como são programados.", score=4),
            ],
        ),
        Question(
            id="q7",
            text="Qual sua familiaridade com NFTs (Tokens Não-Fungíveis)?",
            options=[
                QuestionOption(id="q7a", text="Não sei o que são NFTs.", score=1),
                QuestionOption(id="q7b", text="Já ouvi falar, mas não entendo.", score=2),
                QuestionOption(id="q7c", text="Sei o que são e como funcionam.", score=3),
                QuestionOption(id="q7d", text="Já comprei, vendi ou criei NFTs.", score=4),
            ],
        ),
        Question(
            id="q8",
            text="Qual é seu PRINCIPAL objetivo ao aprender sobre criptomoedas?",
            options=[
                QuestionOption(id="q8a", text="Entender o conceito e a tecnologia.", score=1),
                QuestionOption(id="q8b", text="Investir e ganhar dinheiro.", score=2),
                QuestionOption(id="q8c", text="Desenvolver aplicações blockchain.", score=3),
                QuestionOption(id="q8d", text="Uso profissional ou acadêmico.", score=4),
            ],
        ),
        Question(
            id="q9",
            text="Há quanto tempo você estuda ou acompanha o mercado de criptomoedas?",
            options=[
                QuestionOption(id="q9a", text="Estou começando agora.", score=1),
                QuestionOption(id="q9b", text="Alguns meses.", score=2),
                QuestionOption(id="q9c", text="1-2 anos.", score=3),
                QuestionOption(id="q9d", text="Mais de 2 anos.", score=4),
            ],
        ),
        Question(
            id="q10",
            text="Como você prefere aprender novos conceitos?",
            options=[
                QuestionOption(id="q10a", text="Lendo textos e artigos detalhados.", score=1),
                QuestionOption(id="q10b", text="Assistindo vídeos e tutoriais.", score=2),
                QuestionOption(id="q10c", text="Praticando e testando na prática.", score=3),
                QuestionOption(id="q10d", text="Combinando diferentes métodos.", score=4),
            ],
        ),
    ],
)


            
    
                        
