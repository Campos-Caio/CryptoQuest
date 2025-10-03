"""
Testes unitários para serviços de IA.
"""
import pytest
import numpy as np
from datetime import datetime, UTC
from unittest.mock import Mock, patch

from app.ai.services.ml_engine import LearningStyleClassifier, DifficultyPredictor, MLEngine
from app.ai.services.recommendation_engine import BasicRecommendationEngine
from app.ai.data.behavioral_data_collector import BehavioralDataCollector
from app.ai.models.ai_models import EnhancedQuizSubmission, UserBehavioralData


class TestLearningStyleClassifier:
    """Testes para o classificador de estilo de aprendizado"""
    
    def test_init(self):
        """Testa inicialização do classificador"""
        classifier = LearningStyleClassifier()
        assert classifier.is_trained == False
        assert len(classifier.feature_names) == 6
    
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
    
    def test_predict_with_rules(self):
        """Testa predição baseada em regras"""
        classifier = LearningStyleClassifier()
        
        # Caso de aprendiz rápido
        user_data = {
            'avg_response_time': 10,
            'avg_confidence': 0.8,
            'hints_usage_rate': 0.1
        }
        
        prediction = classifier._predict_with_rules(user_data)
        assert prediction.value == "visual"
        assert prediction.confidence > 0.6
        
        # Caso de aprendiz metódico
        user_data = {
            'avg_response_time': 35,
            'avg_confidence': 0.6,
            'hints_usage_rate': 0.6
        }
        
        prediction = classifier._predict_with_rules(user_data)
        assert prediction.value == "methodical"
        assert prediction.confidence > 0.5


class TestDifficultyPredictor:
    """Testes para o preditor de dificuldade"""
    
    def test_init(self):
        """Testa inicialização do preditor"""
        predictor = DifficultyPredictor()
        assert predictor.is_trained == False
    
    def test_predict_with_rules(self):
        """Testa predição baseada em regras"""
        predictor = DifficultyPredictor()
        
        user_data = {
            'user_level': 2,
            'domain': 'bitcoin_basics'
        }
        
        prediction = predictor._predict_with_rules(user_data)
        assert 0.0 <= prediction.value <= 1.0
        assert prediction.confidence > 0.5


class TestBasicRecommendationEngine:
    """Testes para o engine de recomendação"""
    
    def test_init(self):
        """Testa inicialização do engine"""
        engine = BasicRecommendationEngine()
        assert len(engine.content_database) > 0
        assert "bitcoin_fundamentals_quiz" in engine.content_database
    
    def test_identify_knowledge_gaps(self):
        """Testa identificação de gaps de conhecimento"""
        engine = BasicRecommendationEngine()
        
        user_profile = {
            'domains': {
                'bitcoin_basics': 0.8,
                'defi': 0.2,
                'blockchain_technology': 0.6
            }
        }
        
        gaps = engine._identify_knowledge_gaps(user_profile)
        assert len(gaps) == 1  # Apenas DeFi tem gap
        assert gaps[0].domain == 'defi'
        assert gaps[0].gap_severity > 0.5
    
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


class TestBehavioralDataCollector:
    """Testes para o coletor de dados comportamentais"""
    
    def test_init(self):
        """Testa inicialização do coletor"""
        collector = BehavioralDataCollector()
        assert collector.data_storage == {}
        assert collector.session_tracking == {}
    
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
        assert metrics['avg_confidence'] == 0.77  # (0.8 + 0.6 + 0.9) / 3
        assert metrics['hints_usage_rate'] == 1/3  # 1 hint em 3 questões
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


class TestMLEngine:
    """Testes para o engine principal de ML"""
    
    def test_init(self):
        """Testa inicialização do engine"""
        engine = MLEngine()
        assert engine.learning_style_classifier is not None
        assert engine.difficulty_predictor is not None
    
    def test_identify_pattern_type(self):
        """Testa identificação de tipo de padrão"""
        engine = MLEngine()
        
        # Padrão de aprendiz rápido
        pattern_type, strength = engine._identify_pattern_type(
            avg_time=10, confidence_var=0.05, hints_rate=0.1, success_rate=0.9
        )
        assert pattern_type == "fast_learner"
        assert strength > 0.8
        
        # Padrão metódico
        pattern_type, strength = engine._identify_pattern_type(
            avg_time=30, confidence_var=0.2, hints_rate=0.5, success_rate=0.7
        )
        assert pattern_type == "methodical_learner"
        assert strength > 0.7
    
    def test_create_default_pattern(self):
        """Testa criação de padrão padrão"""
        engine = MLEngine()
        pattern = engine._create_default_pattern("test_user")
        
        assert pattern.pattern_type == "new_learner"
        assert pattern.strength == 0.3
        assert pattern.frequency == 0


@pytest.mark.asyncio
class TestAsyncFunctions:
    """Testes para funções assíncronas"""
    
    async def test_analyze_user_patterns(self):
        """Testa análise de padrões do usuário"""
        engine = MLEngine()
        
        quiz_data = [
            {'response_time': 15, 'confidence': 0.8, 'hints_used': 0, 'correct': True},
            {'response_time': 12, 'confidence': 0.9, 'hints_used': 0, 'correct': True},
            {'response_time': 18, 'confidence': 0.7, 'hints_used': 1, 'correct': True}
        ]
        
        pattern = await engine.analyze_user_patterns("test_user", quiz_data)
        
        assert pattern.pattern_type in ["fast_learner", "visual_learner", "mixed_learner"]
        assert pattern.strength > 0.0
        assert pattern.frequency == 3
    
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
                    'defi': 0.2
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
