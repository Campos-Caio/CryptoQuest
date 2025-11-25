"""
Testes unitários completos para o sistema de IA do CryptoQuest.
"""
import pytest
import asyncio
from datetime import datetime, UTC, timedelta
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from typing import Dict, Any, List

from app.ai.models.ai_models import (
    EnhancedQuizSubmission, UserBehavioralData, LearningPattern,
    ContentRecommendation, AIPrediction, UserKnowledgeProfile
)
from app.ai.services.ml_engine import MLEngine, LearningStyleClassifier, DifficultyPredictor
from app.ai.services.recommendation_engine import BasicRecommendationEngine
from app.ai.data.behavioral_data_collector import BehavioralDataCollector
from app.ai.config import ai_config


@pytest.mark.unit
@pytest.mark.ai
class TestAIConfig:
    """Testes para configurações de IA"""
    
    def test_ai_config_loaded(self):
        """Testa se as configurações de IA foram carregadas"""
        assert ai_config.ai_enabled == True
        assert ai_config.ai_version == "1.0.0"
        assert len(ai_config.knowledge_domains) == 8
        assert len(ai_config.learning_styles) == 5
        assert "bitcoin_basics" in ai_config.knowledge_domains
        assert "visual" in ai_config.learning_styles
    
    def test_domain_difficulty_mapping(self):
        """Testa mapeamento de dificuldade por domínio"""
        from app.ai.config import DOMAIN_DIFFICULTY_MAP
        
        assert "bitcoin_basics" in DOMAIN_DIFFICULTY_MAP
        assert "defi" in DOMAIN_DIFFICULTY_MAP
        assert 0.0 <= DOMAIN_DIFFICULTY_MAP["bitcoin_basics"] <= 1.0
        assert 0.0 <= DOMAIN_DIFFICULTY_MAP["defi"] <= 1.0
    
    def test_domain_content_mapping(self):
        """Testa mapeamento de conteúdo por domínio"""
        from app.ai.config import DOMAIN_CONTENT_MAP
        
        assert "bitcoin_basics" in DOMAIN_CONTENT_MAP
        assert len(DOMAIN_CONTENT_MAP["bitcoin_basics"]) > 0
        assert "bitcoin_fundamentals_quiz" in DOMAIN_CONTENT_MAP["bitcoin_basics"]


@pytest.mark.unit
@pytest.mark.ai
class TestEnhancedQuizSubmission:
    """Testes para o modelo EnhancedQuizSubmission"""
    
    def test_create_enhanced_submission(self):
        """Testa criação de submissão enriquecida"""
        submission = EnhancedQuizSubmission(
            answers=[1, 2, 1, 3, 2],
            time_per_question=[15.5, 12.3, 18.7, 10.2, 14.8],
            confidence_levels=[0.8, 0.6, 0.9, 0.7, 0.8],
            hints_used=[0, 1, 0, 0, 1],
            attempts_per_question=[1, 2, 1, 1, 1],
            session_metadata={"device": "mobile", "browser": "chrome"},
            device_info={"os": "Android", "version": "12"}
        )
        
        assert len(submission.answers) == 5
        assert len(submission.time_per_question) == 5
        assert len(submission.confidence_levels) == 5
        assert len(submission.hints_used) == 5
        assert len(submission.attempts_per_question) == 5
        assert submission.session_metadata["device"] == "mobile"
        assert submission.device_info["os"] == "Android"
    
    def test_enhanced_submission_validation(self):
        """Testa validação de dados da submissão"""
        # Teste com dados válidos
        submission = EnhancedQuizSubmission(
            answers=[1, 2, 3],
            time_per_question=[10.0, 15.0, 12.0],
            confidence_levels=[0.8, 0.7, 0.9]
        )
        
        assert submission.answers == [1, 2, 3]
        assert submission.time_per_question == [10.0, 15.0, 12.0]
        assert submission.confidence_levels == [0.8, 0.7, 0.9]
        
        # Teste com listas vazias (valores padrão)
        submission_empty = EnhancedQuizSubmission(answers=[1, 2])
        assert submission_empty.time_per_question == []
        assert submission_empty.confidence_levels == []
        assert submission_empty.hints_used == []
        assert submission_empty.attempts_per_question == []


@pytest.mark.unit
@pytest.mark.ai
class TestBehavioralDataCollector:
    """Testes para o coletor de dados comportamentais"""
    
    def test_init(self):
        """Testa inicialização do coletor"""
        collector = BehavioralDataCollector()
        assert collector.data_storage == {}
        assert collector.session_tracking == {}
        assert collector.db is None
    
    def test_calculate_performance_metrics(self):
        """Testa cálculo de métricas de performance"""
        collector = BehavioralDataCollector()
        
        submission = EnhancedQuizSubmission(
            answers=[0, 1, 2],
            time_per_question=[15.0, 20.0, 10.0],
            confidence_levels=[0.8, 0.6, 0.9],
            hints_used=[0, 1, 0],
            attempts_per_question=[1, 2, 1]
        )
        
        metrics = collector._calculate_performance_metrics(submission)
        
        assert metrics['total_questions'] == 3
        assert metrics['avg_response_time'] == 15.0
        assert abs(metrics['avg_confidence'] - 0.77) < 0.01  # (0.8 + 0.6 + 0.9) / 3
        assert metrics['hints_usage_rate'] == 1/3  # 1 hint em 3 questões
        assert metrics['total_hints_used'] == 1
        assert metrics['total_attempts'] == 4  # 1 + 2 + 1
        assert 0.0 <= metrics['engagement_score'] <= 1.0
    
    def test_calculate_consistency(self):
        """Testa cálculo de consistência"""
        collector = BehavioralDataCollector()
        
        # Valores consistentes
        consistent_values = [10.0, 10.5, 9.8, 10.2]
        consistency = collector._calculate_consistency(consistent_values)
        assert consistency > 0.8
        
        # Valores inconsistentes
        inconsistent_values = [5.0, 25.0, 10.0, 30.0]
        consistency = collector._calculate_consistency(inconsistent_values)
        assert consistency < 0.5
        
        # Lista vazia
        consistency = collector._calculate_consistency([])
        assert consistency == 1.0
    
    def test_calculate_variance(self):
        """Testa cálculo de variância"""
        collector = BehavioralDataCollector()
        
        # Valores com baixa variância
        low_variance = [0.8, 0.8, 0.8, 0.8]
        variance = collector._calculate_variance(low_variance)
        assert variance < 0.01
        
        # Valores com alta variância
        high_variance = [0.2, 0.8, 0.3, 0.9]
        variance = collector._calculate_variance(high_variance)
        assert variance > 0.09  # Ajustado para valor real calculado (0.0925)
    
    def test_calculate_engagement_score(self):
        """Testa cálculo de score de engajamento"""
        collector = BehavioralDataCollector()
        
        # Alto engajamento
        high_engagement = collector._calculate_engagement_score(
            avg_confidence=0.8,
            hints_usage_rate=0.2,
            retry_rate=0.1
        )
        assert high_engagement > 0.7
        
        # Baixo engajamento
        low_engagement = collector._calculate_engagement_score(
            avg_confidence=0.3,
            hints_usage_rate=0.8,
            retry_rate=0.7
        )
        assert low_engagement < 0.5
        
        # Engajamento médio
        medium_engagement = collector._calculate_engagement_score(
            avg_confidence=0.6,
            hints_usage_rate=0.4,
            retry_rate=0.3
        )
        assert 0.4 <= medium_engagement <= 0.7
    
    def test_determine_domain_from_quiz(self):
        """Testa determinação de domínio baseado no quiz"""
        collector = BehavioralDataCollector()
        
        assert collector._determine_domain_from_quiz("bitcoin_fundamentals_quiz") == "bitcoin_basics"
        assert collector._determine_domain_from_quiz("blockchain_101_quiz") == "blockchain_technology"
        assert collector._determine_domain_from_quiz("defi_overview_quiz") == "defi"
        assert collector._determine_domain_from_quiz("trading_basics_quiz") == "crypto_trading"
        assert collector._determine_domain_from_quiz("unknown_quiz") == "bitcoin_basics"  # padrão
    
    def test_calculate_domain_proficiency(self):
        """Testa cálculo de proficiência no domínio"""
        collector = BehavioralDataCollector()
        
        # Métricas de alta performance
        high_metrics = {
            'engagement_score': 0.9,
            'avg_confidence': 0.8,
            'retry_rate': 0.1
        }
        proficiency = collector._calculate_domain_proficiency(high_metrics)
        assert proficiency > 0.7
        
        # Métricas de baixa performance
        low_metrics = {
            'engagement_score': 0.3,
            'avg_confidence': 0.4,
            'retry_rate': 0.8
        }
        proficiency = collector._calculate_domain_proficiency(low_metrics)
        assert proficiency < 0.5


@pytest.mark.unit
@pytest.mark.ai
class TestLearningStyleClassifier:
    """Testes para o classificador de estilo de aprendizado"""
    
    def test_init(self):
        """Testa inicialização do classificador"""
        classifier = LearningStyleClassifier()
        assert classifier.is_trained == False
        assert len(classifier.feature_names) == 6
        assert 'avg_response_time' in classifier.feature_names
        assert 'confidence_variance' in classifier.feature_names
    
    def test_extract_features(self):
        """Testa extração de features"""
        classifier = LearningStyleClassifier()
        user_data = [
            {
                'avg_response_time': 15.0,
                'confidence_variance': 0.1,
                'hints_usage_rate': 0.2,
                'time_consistency': 0.8,
                'difficulty_preference': 0.5,
                'retry_rate': 0.1
            }
        ]
        
        features = classifier._extract_features(user_data)
        assert features.shape == (1, 6)
        assert features[0][0] == 15.0
        assert features[0][1] == 0.1
    
    def test_predict_with_rules_visual_learner(self):
        """Testa predição de aprendiz visual"""
        classifier = LearningStyleClassifier()
        
        user_data = {
            'avg_response_time': 10,
            'avg_confidence': 0.8,
            'hints_usage_rate': 0.1
        }
        
        prediction = classifier._predict_with_rules(user_data)
        assert prediction.value == "visual"
        assert prediction.confidence > 0.6
        assert prediction.model_used == "rule_based"
    
    def test_predict_with_rules_methodical_learner(self):
        """Testa predição de aprendiz metódico"""
        classifier = LearningStyleClassifier()
        
        user_data = {
            'avg_response_time': 35,
            'avg_confidence': 0.6,
            'hints_usage_rate': 0.6
        }
        
        prediction = classifier._predict_with_rules(user_data)
        assert prediction.value == "methodical"
        assert prediction.confidence > 0.5
        assert prediction.model_used == "rule_based"
    
    def test_predict_with_rules_mixed_learner(self):
        """Testa predição de aprendiz misto"""
        classifier = LearningStyleClassifier()
        
        user_data = {
            'avg_response_time': 20,
            'avg_confidence': 0.6,
            'hints_usage_rate': 0.3
        }
        
        prediction = classifier._predict_with_rules(user_data)
        assert prediction.value == "mixed"
        assert prediction.confidence == 0.5
        assert prediction.model_used == "rule_based"
    
    def test_create_default_metrics(self):
        """Testa criação de métricas padrão"""
        classifier = LearningStyleClassifier()
        metrics = classifier._create_default_metrics()
        
        assert metrics.model_name == "learning_style_classifier"
        assert metrics.accuracy == 0.0
        assert metrics.training_samples == 0


@pytest.mark.unit
@pytest.mark.ai
class TestDifficultyPredictor:
    """Testes para o preditor de dificuldade"""
    
    def test_init(self):
        """Testa inicialização do preditor"""
        predictor = DifficultyPredictor()
        assert predictor.is_trained == False
    
    def test_predict_with_rules(self):
        """Testa predição baseada em regras"""
        predictor = DifficultyPredictor()
        
        # Usuário iniciante
        user_data = {
            'user_level': 1,
            'domain': 'bitcoin_basics'
        }
        
        prediction = predictor._predict_with_rules(user_data)
        assert 0.0 <= prediction.value <= 1.0
        assert prediction.confidence > 0.5
        assert prediction.model_used == "rule_based"
        
        # Usuário avançado
        user_data = {
            'user_level': 5,
            'domain': 'defi'
        }
        
        prediction = predictor._predict_with_rules(user_data)
        assert 0.0 <= prediction.value <= 1.0
        assert prediction.value > 0.5  # Dificuldade maior para usuário avançado
    
    def test_create_default_metrics(self):
        """Testa criação de métricas padrão"""
        predictor = DifficultyPredictor()
        metrics = predictor._create_default_metrics()
        
        assert metrics.model_name == "difficulty_predictor"
        assert metrics.accuracy == 0.0
        assert metrics.training_samples == 0


@pytest.mark.unit
@pytest.mark.ai
class TestMLEngine:
    """Testes para o engine principal de ML"""
    
    def test_init(self):
        """Testa inicialização do engine"""
        engine = MLEngine()
        assert engine.learning_style_classifier is not None
        assert engine.difficulty_predictor is not None
    
    def test_identify_pattern_type_fast_learner(self):
        """Testa identificação de padrão de aprendiz rápido"""
        engine = MLEngine()
        
        pattern_type, strength = engine._identify_pattern_type(
            avg_time=10, confidence_var=0.05, hints_rate=0.1, success_rate=0.9
        )
        assert pattern_type == "fast_learner"
        assert strength > 0.8
    
    def test_identify_pattern_type_methodical_learner(self):
        """Testa identificação de padrão de aprendiz metódico"""
        engine = MLEngine()
        
        pattern_type, strength = engine._identify_pattern_type(
            avg_time=30, confidence_var=0.2, hints_rate=0.5, success_rate=0.7
        )
        assert pattern_type == "methodical_learner"
        assert strength > 0.7
    
    def test_identify_pattern_type_visual_learner(self):
        """Testa identificação de padrão de aprendiz visual"""
        engine = MLEngine()
        
        pattern_type, strength = engine._identify_pattern_type(
            avg_time=15, confidence_var=0.1, hints_rate=0.2, success_rate=0.8
        )
        assert pattern_type == "visual_learner"
        assert strength > 0.6
    
    def test_identify_pattern_type_auditory_learner(self):
        """Testa identificação de padrão de aprendiz auditório"""
        engine = MLEngine()
        
        pattern_type, strength = engine._identify_pattern_type(
            avg_time=25, confidence_var=0.4, hints_rate=0.3, success_rate=0.7
        )
        assert pattern_type == "auditory_learner"
        assert strength > 0.5
    
    def test_identify_pattern_type_mixed_learner(self):
        """Testa identificação de padrão de aprendiz misto"""
        engine = MLEngine()
        
        pattern_type, strength = engine._identify_pattern_type(
            avg_time=20, confidence_var=0.3, hints_rate=0.4, success_rate=0.6
        )
        assert pattern_type == "mixed_learner"
        assert strength == 0.5
    
    def test_create_default_pattern(self):
        """Testa criação de padrão padrão"""
        engine = MLEngine()
        pattern = engine._create_default_pattern("test_user")
        
        assert pattern.pattern_type == "new_learner"
        assert pattern.strength == 0.3
        assert pattern.frequency == 0
        assert pattern.context["status"] == "insufficient_data"
    
    def test_get_model_metrics(self):
        """Testa obtenção de métricas dos modelos"""
        engine = MLEngine()
        metrics = engine.get_model_metrics()
        
        # Deve retornar um dicionário
        assert isinstance(metrics, dict)
        
        # Se os modelos estiverem treinados, deve ter métricas
        if engine.learning_style_classifier.is_trained:
            assert "learning_style" in metrics
        if engine.difficulty_predictor.is_trained:
            assert "difficulty" in metrics


@pytest.mark.unit
@pytest.mark.ai
class TestBasicRecommendationEngine:
    """Testes para o engine de recomendação"""
    
    def test_init(self):
        """Testa inicialização do engine"""
        engine = BasicRecommendationEngine()
        assert len(engine.content_database) > 0
        # Verificar IDs que realmente existem no content_database
        assert "btc_quiz_01" in engine.content_database or "bitcoin_caracteristicas_questionnaire" in engine.content_database
        # Verificar que há conteúdo de blockchain (pode estar na chave ou no domain)
        has_blockchain = any(
            "blockchain" in key.lower() or 
            content.get("domain", "").lower() == "blockchain_technology"
            for key, content in engine.content_database.items()
        )
        assert has_blockchain
        # Verificar que há conteúdo de DeFi (pode estar na chave ou no domain)
        has_defi = any(
            "defi" in key.lower() or 
            content.get("domain", "").lower() == "defi"
            for key, content in engine.content_database.items()
        )
        assert has_defi
    
    def test_initialize_content_database(self):
        """Testa inicialização do banco de conteúdo"""
        engine = BasicRecommendationEngine()
        content_db = engine._initialize_content_database()
        
        # Verificar estrutura dos itens de conteúdo
        for content_id, content_data in content_db.items():
            assert "id" in content_data
            assert "type" in content_data
            assert "domain" in content_data
            assert "difficulty" in content_data
            assert "estimated_time" in content_data
            assert "learning_objectives" in content_data
            assert content_data["id"] == content_id
    
    def test_identify_knowledge_gaps(self):
        """Testa identificação de gaps de conhecimento"""
        engine = BasicRecommendationEngine()
        
        # Perfil com gaps
        user_profile = {
            'domains': {
                'bitcoin_basics': 0.8,      # Bom
                'defi': 0.2,                # Gap crítico
                'blockchain_technology': 0.6,  # Médio
                'crypto_trading': 0.4       # Gap médio
            }
        }
        
        gaps = engine._identify_knowledge_gaps(user_profile)
        
        # Deve identificar 2 gaps (defi e crypto_trading)
        assert len(gaps) == 2
        
        # Verificar se DeFi tem maior severidade (menor proficiência)
        defi_gap = next(gap for gap in gaps if gap.domain == 'defi')
        trading_gap = next(gap for gap in gaps if gap.domain == 'crypto_trading')
        assert defi_gap.gap_severity > trading_gap.gap_severity
        
        # Verificar prioridades
        assert defi_gap.priority >= trading_gap.priority
    
    def test_calculate_gap_priority(self):
        """Testa cálculo de prioridade de gaps"""
        engine = BasicRecommendationEngine()
        
        # Gap crítico
        priority = engine._calculate_gap_priority("defi", 0.1)
        assert priority == 5
        
        # Gap alto
        priority = engine._calculate_gap_priority("trading", 0.4)
        assert priority == 4
        
        # Gap médio
        priority = engine._calculate_gap_priority("blockchain", 0.6)
        assert priority == 3
        
        # Gap baixo
        priority = engine._calculate_gap_priority("bitcoin", 0.8)
        assert priority == 2
    
    def test_find_content_for_gap(self):
        """Testa busca de conteúdo para gaps"""
        engine = BasicRecommendationEngine()
        
        # Gap crítico - deve retornar conteúdo básico
        critical_gap = Mock()
        critical_gap.domain = "defi"
        critical_gap.gap_severity = 0.8
        
        content = engine._find_content_for_gap(critical_gap)
        for item in content:
            assert item['domain'] == "defi"
            assert item['difficulty'] <= 0.4  # Conteúdo básico
        
        # Gap médio - pode retornar qualquer conteúdo do domínio
        medium_gap = Mock()
        medium_gap.domain = "bitcoin_basics"
        medium_gap.gap_severity = 0.4
        
        content = engine._find_content_for_gap(medium_gap)
        for item in content:
            assert item['domain'] == "bitcoin_basics"
    
    def test_calculate_relevance_score(self):
        """Testa cálculo de score de relevância"""
        engine = BasicRecommendationEngine()
        
        content_item = {
            'id': 'test_quiz',
            'type': 'quiz',
            'difficulty': 0.5,
            'estimated_time': 20,
            'learning_objectives': ['Test objective']
        }
        
        gap = Mock()
        gap.gap_severity = 0.8
        gap.domain = 'bitcoin_basics'
        
        user_profile = {
            'level': 2,
            'preferred_difficulty': 0.5,
            'average_session_time': 25,
            'learning_style': 'visual'
        }
        
        score = engine._calculate_relevance_score(content_item, gap, user_profile)
        
        assert 0.0 <= score <= 1.0
        assert score > 0.5  # Deve ser relevante
        
        # Teste com perfil que não combina
        user_profile['learning_style'] = 'auditory'
        user_profile['preferred_difficulty'] = 0.9  # Muito diferente da dificuldade do conteúdo
        
        score = engine._calculate_relevance_score(content_item, gap, user_profile)
        assert score < 0.8  # Deve ser menos relevante
    
    def test_map_difficulty(self):
        """Testa mapeamento de dificuldade"""
        engine = BasicRecommendationEngine()
        
        assert engine._map_difficulty(0.2).value == "beginner"
        assert engine._map_difficulty(0.5).value == "intermediate"
        assert engine._map_difficulty(0.7).value == "advanced"
        assert engine._map_difficulty(0.9).value == "expert"


@pytest.mark.unit
@pytest.mark.ai
@pytest.mark.asyncio
class TestAsyncAIFunctions:
    """Testes para funções assíncronas de IA"""
    
    async def test_analyze_user_patterns(self):
        """Testa análise de padrões do usuário"""
        engine = MLEngine()
        
        # Dados de quiz para aprendiz visual
        quiz_data = [
            {'response_time': 15, 'confidence': 0.8, 'hints_used': 0, 'correct': True},
            {'response_time': 12, 'confidence': 0.9, 'hints_used': 0, 'correct': True},
            {'response_time': 18, 'confidence': 0.7, 'hints_used': 1, 'correct': True}
        ]
        
        pattern = await engine.analyze_user_patterns("test_user", quiz_data)
        
        assert pattern.pattern_type in ["fast_learner", "visual_learner", "mixed_learner"]
        assert pattern.strength > 0.0
        assert pattern.frequency == 3
        assert "avg_response_time" in pattern.context
        assert "confidence_variance" in pattern.context
    
    async def test_analyze_user_patterns_empty_data(self):
        """Testa análise com dados vazios"""
        engine = MLEngine()
        
        pattern = await engine.analyze_user_patterns("test_user", [])
        
        assert pattern.pattern_type == "new_learner"
        assert pattern.strength == 0.3
        assert pattern.frequency == 0
    
    async def test_get_recommendations(self):
        """Testa geração de recomendações"""
        engine = BasicRecommendationEngine()
        
        # Mock do perfil do usuário
        with patch.object(engine, '_get_user_profile') as mock_profile:
            mock_profile.return_value = {
                'user_id': 'test_user',
                'level': 2,
                'domains': {
                    'bitcoin_basics': 0.8,
                    'defi': 0.2  # Gap crítico
                },
                'learning_style': 'visual',
                'completed_content': [],
                'preferred_difficulty': 0.5,
                'average_session_time': 20
            }
            
            recommendations = await engine.get_recommendations('test_user', limit=3)
            
            assert len(recommendations) <= 3
            if recommendations:
                assert recommendations[0].content_id is not None
                assert 0.0 <= recommendations[0].relevance_score <= 1.0
                assert recommendations[0].content_type in ['quiz', 'lesson', 'practice']
                assert recommendations[0].difficulty_level is not None
                assert recommendations[0].estimated_time > 0
                assert len(recommendations[0].reasoning) > 0
    
    async def test_get_content_suggestions(self):
        """Testa geração de sugestões de conteúdo por domínio"""
        engine = BasicRecommendationEngine()
        
        with patch.object(engine, '_get_user_profile') as mock_profile:
            mock_profile.return_value = {
                'user_id': 'test_user',
                'domains': {
                    'bitcoin_basics': 0.6
                },
                'completed_content': []
            }
            
            suggestions = await engine.get_content_suggestions('test_user', 'bitcoin_basics', limit=2)
            
            assert len(suggestions) <= 2
            for suggestion in suggestions:
                assert suggestion.content_id is not None
                assert suggestion.content_type in ['quiz', 'lesson', 'practice']
                assert 0.0 <= suggestion.relevance_score <= 1.0
    
    async def test_get_adaptive_difficulty(self):
        """Testa cálculo de dificuldade adaptativa"""
        engine = BasicRecommendationEngine()
        
        with patch.object(engine, '_get_user_profile') as mock_profile:
            mock_profile.return_value = {
                'user_id': 'test_user',
                'domains': {
                    'bitcoin_basics': 0.7
                }
            }
            
            difficulty = await engine.get_adaptive_difficulty('test_user', 'bitcoin_fundamentals_quiz')
            
            assert 0.0 <= difficulty <= 1.0
            
            # Teste com conteúdo inexistente
            difficulty = await engine.get_adaptive_difficulty('test_user', 'nonexistent_quiz')
            assert difficulty == 0.5  # Dificuldade padrão
    
    async def test_collect_quiz_data(self):
        """Testa coleta de dados de quiz"""
        collector = BehavioralDataCollector()
        
        submission = EnhancedQuizSubmission(
            answers=[1, 2, 1, 3, 2],
            time_per_question=[15.5, 12.3, 18.7, 10.2, 14.8],
            confidence_levels=[0.8, 0.6, 0.9, 0.7, 0.8],
            hints_used=[0, 1, 0, 0, 1],
            attempts_per_question=[1, 2, 1, 1, 1]
        )
        
        # Mock do Firestore
        with patch.object(collector, '_get_db') as mock_get_db:
            mock_db = AsyncMock()
            mock_get_db.return_value = mock_db
            
            # Mock do documento
            mock_doc_ref = AsyncMock()
            mock_db.collection.return_value.document.return_value = mock_doc_ref
            
            behavioral_data = await collector.collect_quiz_data(
                user_id="test_user",
                quiz_id="test_quiz",
                submission=submission
            )
            
            assert behavioral_data.user_id == "test_user"
            assert behavioral_data.quiz_id == "test_quiz"
            assert behavioral_data.session_id is not None
            assert len(behavioral_data.performance_metrics) > 0
            assert behavioral_data.performance_metrics['total_questions'] == 5
    
    async def test_get_user_behavioral_history(self):
        """Testa busca de histórico comportamental"""
        collector = BehavioralDataCollector()
        
        # Usar o fallback para cache local quando o Firestore falhar
        # Preencher o cache local diretamente
        test_data = [
            {
                "session_id": 'session1',
                "quiz_id": 'quiz1',
                "performance_metrics": {'engagement_score': 0.8},
                "collected_at": datetime.now(UTC).isoformat()
            },
            {
                "session_id": 'session2',
                "quiz_id": 'quiz2',
                "performance_metrics": {'engagement_score': 0.7},
                "collected_at": datetime.now(UTC).isoformat()
            }
        ]
        collector.data_storage['test_user'] = test_data
        
        # Mock do Firestore para forçar o fallback
        with patch.object(collector, '_get_db') as mock_get_db:
            # Fazer o mock lançar uma exceção para usar o fallback
            mock_get_db.side_effect = Exception("Firestore error")
            
            history = await collector.get_user_behavioral_history('test_user', limit=5)
            
            assert len(history) == 2
            assert history[0]['session_id'] == 'session1'
            assert history[0]['performance_metrics']['engagement_score'] == 0.8
    
    async def test_get_user_performance_summary(self):
        """Testa resumo de performance do usuário"""
        collector = BehavioralDataCollector()
        
        # Mock do histórico
        with patch.object(collector, 'get_user_behavioral_history') as mock_history, \
             patch.object(collector, '_get_user_knowledge_profile') as mock_profile:
            
            mock_history.return_value = [
                {
                    'performance_metrics': {
                        'avg_response_time': 15.0,
                        'avg_confidence': 0.8,
                        'engagement_score': 0.9
                    },
                    'collected_at': '2024-01-15T10:30:00Z'
                },
                {
                    'performance_metrics': {
                        'avg_response_time': 12.0,
                        'avg_confidence': 0.7,
                        'engagement_score': 0.8
                    },
                    'collected_at': '2024-01-15T09:30:00Z'
                }
            ]
            
            # Mock do perfil de conhecimento (retorna vazio para simplificar)
            mock_profile.return_value = {}
            
            summary = await collector.get_user_performance_summary('test_user')
            
            assert summary['total_sessions'] == 2
            assert summary['avg_response_time'] == 13.5  # (15.0 + 12.0) / 2
            assert summary['avg_confidence'] == 0.75  # (0.8 + 0.7) / 2
            # O código retorna 'engagement_score', não 'avg_engagement_score'
            assert summary['engagement_score'] == 0.85  # (0.9 + 0.8) / 2
            assert summary['performance_trend'] in ['improving', 'stable', 'declining']
            assert summary['data_source'] == 'firestore'
    
    async def test_start_learning_session(self):
        """Testa início de sessão de aprendizado"""
        collector = BehavioralDataCollector()
        
        # Mock do Firestore - corrigindo a estrutura do mock
        with patch.object(collector, '_get_db') as mock_get_db:
            mock_db = Mock()
            mock_collection = Mock()
            mock_doc_ref = Mock()
            
            # Configurar a cadeia de mocks corretamente
            mock_db.collection.return_value = mock_collection
            mock_collection.document.return_value = mock_doc_ref
            mock_doc_ref.set = AsyncMock()  # set é async
            
            # Fazer o mock retornar o db corretamente
            async def mock_get_db_func():
                return mock_db
            
            mock_get_db.side_effect = mock_get_db_func
            
            session_id = await collector.start_learning_session('test_user', 'quiz')
            
            assert session_id is not None
            assert 'test_user' in session_id
            assert 'quiz' in session_id
            assert session_id in collector.session_tracking
    
    async def test_end_learning_session(self):
        """Testa finalização de sessão de aprendizado"""
        collector = BehavioralDataCollector()
        
        # Criar sessão manualmente no tracking para o teste
        # Usar um start_time no passado para garantir que haja duração
        session_id = f"test_user_quiz_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}"
        from app.ai.models.ai_models import LearningSession
        start_time = datetime.now(UTC) - timedelta(seconds=10)  # 10 segundos no passado
        session = LearningSession(
            session_id=session_id,
            user_id='test_user',
            start_time=start_time
        )
        collector.session_tracking[session_id] = session
        
        # Mock do Firestore
        with patch.object(collector, '_get_db') as mock_get_db:
            mock_db = Mock()
            mock_collection = Mock()
            mock_doc_ref = Mock()
            
            # Configurar a cadeia de mocks corretamente
            mock_db.collection.return_value = mock_collection
            mock_collection.document.return_value = mock_doc_ref
            mock_doc_ref.update = AsyncMock()  # update é async
            
            # Fazer o mock retornar o db corretamente
            async def mock_get_db_func():
                return mock_db
            
            mock_get_db.side_effect = mock_get_db_func
            
            summary = await collector.end_learning_session(session_id)
            
            assert summary['session_id'] == session_id
            assert summary['user_id'] == 'test_user'
            # A duração deve ser pelo menos 9 segundos (10 segundos menos 1 segundo de processamento)
            assert summary['duration_seconds'] >= 9
            assert session_id not in collector.session_tracking  # Removido da tracking


@pytest.mark.unit
@pytest.mark.ai
class TestAIModels:
    """Testes para modelos de dados de IA"""
    
    def test_learning_pattern(self):
        """Testa modelo LearningPattern"""
        pattern = LearningPattern(
            pattern_type="visual_learner",
            strength=0.85,
            frequency=5,
            context={"avg_response_time": 12.3, "confidence_variance": 0.05}
        )
        
        assert pattern.pattern_type == "visual_learner"
        assert pattern.strength == 0.85
        assert pattern.frequency == 5
        assert pattern.context["avg_response_time"] == 12.3
    
    def test_content_recommendation(self):
        """Testa modelo ContentRecommendation"""
        from app.ai.models.ai_models import DifficultyLevel
        
        recommendation = ContentRecommendation(
            content_id="defi_overview_quiz",
            content_type="quiz",
            relevance_score=0.87,
            difficulty_level=DifficultyLevel.BEGINNER,
            estimated_time=20,
            reasoning="Gap crítico em DeFi",
            learning_objectives=["Entender DeFi", "Conhecer protocolos"]
        )
        
        assert recommendation.content_id == "defi_overview_quiz"
        assert recommendation.content_type == "quiz"
        assert recommendation.relevance_score == 0.87
        assert recommendation.difficulty_level == DifficultyLevel.BEGINNER
        assert recommendation.estimated_time == 20
        assert len(recommendation.learning_objectives) == 2
    
    def test_ai_prediction(self):
        """Testa modelo AIPrediction"""
        prediction = AIPrediction(
            prediction_type="learning_style",
            value="visual",
            confidence=0.85,
            reasoning="Respostas rápidas e alta confiança",
            model_used="learning_style_classifier"
        )
        
        assert prediction.prediction_type == "learning_style"
        assert prediction.value == "visual"
        assert prediction.confidence == 0.85
        assert prediction.reasoning == "Respostas rápidas e alta confiança"
        assert prediction.model_used == "learning_style_classifier"
    
    def test_user_knowledge_profile(self):
        """Testa modelo UserKnowledgeProfile"""
        from app.ai.models.ai_models import LearningStyle, KnowledgeDomainProfile
        
        domain_profile = KnowledgeDomainProfile(
            domain="bitcoin_basics",
            proficiency_level=0.75,
            confidence=0.8,
            evidence_sources=["quiz1", "quiz2"],
            total_questions=10,
            correct_answers=8,
            average_response_time=15.2
        )
        
        profile = UserKnowledgeProfile(
            user_id="test_user",
            domains={"bitcoin_basics": domain_profile},
            learning_style=LearningStyle.VISUAL,
            pace_preference="fast",
            difficulty_preference=0.6,
            engagement_score=0.8
        )
        
        assert profile.user_id == "test_user"
        assert profile.learning_style == LearningStyle.VISUAL
        assert profile.pace_preference == "fast"
        assert profile.difficulty_preference == 0.6
        assert profile.engagement_score == 0.8
        assert "bitcoin_basics" in profile.domains
        assert profile.domains["bitcoin_basics"].proficiency_level == 0.75
