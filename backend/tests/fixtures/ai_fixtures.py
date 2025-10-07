"""
Fixtures específicas para testes de IA do CryptoQuest.
"""
import pytest
from datetime import datetime, UTC
from unittest.mock import Mock, AsyncMock
from typing import Dict, Any, List

from app.ai.models.ai_models import (
    EnhancedQuizSubmission, UserBehavioralData, LearningPattern,
    ContentRecommendation, AIPrediction, UserKnowledgeProfile,
    KnowledgeDomainProfile, LearningStyle, DifficultyLevel
)


@pytest.fixture
def sample_enhanced_submission():
    """Fixture para submissão de quiz enriquecida"""
    return EnhancedQuizSubmission(
        answers=[1, 2, 1, 3, 2],
        time_per_question=[15.5, 12.3, 18.7, 10.2, 14.8],
        confidence_levels=[0.8, 0.6, 0.9, 0.7, 0.8],
        hints_used=[0, 1, 0, 0, 1],
        attempts_per_question=[1, 2, 1, 1, 1],
        session_metadata={
            "device_type": "desktop",
            "browser": "chrome",
            "session_duration": 300
        },
        device_info={
            "os": "Windows",
            "version": "11",
            "screen_resolution": "1920x1080"
        }
    )


@pytest.fixture
def visual_learner_submission():
    """Fixture para submissão de aprendiz visual"""
    return EnhancedQuizSubmission(
        answers=[1, 2, 1, 3, 2],
        time_per_question=[8.5, 7.2, 9.1, 6.8, 8.3],  # Rápido
        confidence_levels=[0.9, 0.8, 0.95, 0.85, 0.9],  # Alta confiança
        hints_used=[0, 0, 0, 0, 0],  # Sem dicas
        attempts_per_question=[1, 1, 1, 1, 1]  # Uma tentativa
    )


@pytest.fixture
def methodical_learner_submission():
    """Fixture para submissão de aprendiz metódico"""
    return EnhancedQuizSubmission(
        answers=[1, 2, 1, 3, 2],
        time_per_question=[25.3, 28.7, 22.1, 30.2, 26.8],  # Lento
        confidence_levels=[0.6, 0.7, 0.5, 0.8, 0.65],  # Confiança variável
        hints_used=[1, 2, 1, 0, 1],  # Usa dicas
        attempts_per_question=[2, 3, 2, 1, 2]  # Múltiplas tentativas
    )


@pytest.fixture
def mixed_learner_submission():
    """Fixture para submissão de aprendiz misto"""
    return EnhancedQuizSubmission(
        answers=[1, 2, 1, 3, 2],
        time_per_question=[15.2, 18.7, 12.3, 20.1, 16.8],  # Médio
        confidence_levels=[0.7, 0.8, 0.6, 0.9, 0.75],  # Confiança média
        hints_used=[0, 1, 0, 0, 1],
        attempts_per_question=[1, 2, 1, 1, 2]
    )


@pytest.fixture
def sample_behavioral_data(sample_enhanced_submission):
    """Fixture para dados comportamentais"""
    return UserBehavioralData(
        user_id="test_user_123",
        session_id="test_session_456",
        quiz_id="bitcoin_fundamentals_quiz",
        submission_data=sample_enhanced_submission,
        performance_metrics={
            "total_questions": 5,
            "avg_response_time": 14.3,
            "avg_confidence": 0.76,
            "response_time_consistency": 0.8,
            "confidence_variance": 0.1,
            "hints_usage_rate": 0.4,
            "retry_rate": 0.2,
            "engagement_score": 0.82,
            "total_hints_used": 2,
            "total_attempts": 6
        },
        collected_at=datetime.now(UTC)
    )


@pytest.fixture
def sample_learning_pattern():
    """Fixture para padrão de aprendizado"""
    return LearningPattern(
        pattern_type="visual_learner",
        strength=0.85,
        frequency=8,
        last_observed=datetime.now(UTC),
        context={
            "avg_response_time": 12.3,
            "confidence_variance": 0.05,
            "hints_usage_rate": 0.1,
            "success_rate": 0.9
        }
    )


@pytest.fixture
def sample_content_recommendation():
    """Fixture para recomendação de conteúdo"""
    return ContentRecommendation(
        content_id="defi_overview_quiz",
        content_type="quiz",
        relevance_score=0.87,
        difficulty_level=DifficultyLevel.BEGINNER,
        estimated_time=20,
        reasoning="Identificado gap crítico em DeFi (severidade: 0.8)",
        learning_objectives=[
            "Entender conceitos de DeFi",
            "Conhecer principais protocolos"
        ]
    )


@pytest.fixture
def sample_ai_prediction():
    """Fixture para predição de IA"""
    return AIPrediction(
        prediction_type="learning_style",
        value="visual",
        confidence=0.85,
        reasoning="Respostas rápidas e alta confiança indicam estilo visual",
        model_used="learning_style_classifier",
        timestamp=datetime.now(UTC)
    )


@pytest.fixture
def sample_knowledge_domain_profile():
    """Fixture para perfil de domínio de conhecimento"""
    return KnowledgeDomainProfile(
        domain="bitcoin_basics",
        proficiency_level=0.75,
        confidence=0.8,
        last_updated=datetime.now(UTC),
        evidence_sources=["quiz1", "quiz2", "quiz3"],
        total_questions=15,
        correct_answers=12,
        average_response_time=14.2,
        difficulty_preference=0.6
    )


@pytest.fixture
def sample_user_knowledge_profile(sample_knowledge_domain_profile):
    """Fixture para perfil completo de conhecimento do usuário"""
    return UserKnowledgeProfile(
        user_id="test_user_123",
        domains={
            "bitcoin_basics": sample_knowledge_domain_profile,
            "defi": KnowledgeDomainProfile(
                domain="defi",
                proficiency_level=0.2,
                confidence=0.6,
                last_updated=datetime.now(UTC),
                evidence_sources=["quiz1"],
                total_questions=3,
                correct_answers=1,
                average_response_time=25.0,
                difficulty_preference=0.3
            )
        },
        learning_style=LearningStyle.VISUAL,
        pace_preference="fast",
        difficulty_preference=0.6,
        engagement_score=0.8,
        retention_rate=0.75,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC)
    )


@pytest.fixture
def mock_firestore_db():
    """Fixture para mock do Firestore"""
    mock_db = Mock()
    
    # Mock para collection
    mock_collection = Mock()
    mock_db.collection.return_value = mock_collection
    
    # Mock para document
    mock_doc_ref = AsyncMock()
    mock_doc = Mock()
    mock_doc.exists = True
    mock_doc.to_dict.return_value = {
        "user_id": "test_user_123",
        "session_id": "test_session_456",
        "quiz_id": "bitcoin_fundamentals_quiz",
        "performance_metrics": {
            "engagement_score": 0.82,
            "avg_response_time": 14.3
        },
        "collected_at": datetime.now(UTC)
    }
    mock_doc_ref.get.return_value = mock_doc
    mock_doc_ref.set.return_value = None
    mock_doc_ref.update.return_value = None
    mock_collection.document.return_value = mock_doc_ref
    
    # Mock para query
    mock_query = Mock()
    mock_query.where.return_value = mock_query
    mock_query.order_by.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.get.return_value = [mock_doc]
    mock_collection.where.return_value = mock_query
    
    return mock_db


@pytest.fixture
def mock_ml_engine():
    """Fixture para mock do ML Engine"""
    mock_engine = Mock()
    
    # Mock do learning_style_classifier
    mock_engine.learning_style_classifier = Mock()
    mock_engine.learning_style_classifier.is_trained = False
    mock_engine.learning_style_classifier.predict = Mock(return_value=Mock(
        value="visual",
        confidence=0.85,
        reasoning="Respostas rápidas e alta confiança",
        model_used="rule_based"
    ))
    
    # Mock do difficulty_predictor
    mock_engine.difficulty_predictor = Mock()
    mock_engine.difficulty_predictor.is_trained = False
    mock_engine.difficulty_predictor.predict_optimal_difficulty = Mock(return_value=Mock(
        value=0.65,
        confidence=0.82,
        reasoning="Baseado no perfil do usuário",
        model_used="rule_based"
    ))
    
    # Mock do analyze_user_patterns
    mock_engine.analyze_user_patterns = AsyncMock(return_value=Mock(
        pattern_type="visual_learner",
        strength=0.85,
        frequency=5,
        context={"avg_response_time": 12.3}
    ))
    
    # Mock do get_model_metrics
    mock_engine.get_model_metrics = Mock(return_value={
        "learning_style": Mock(
            accuracy=0.85,
            precision=0.83,
            recall=0.82,
            f1_score=0.82,
            training_samples=1000,
            last_trained=datetime.now(UTC),
            version="1.0"
        )
    })
    
    return mock_engine


@pytest.fixture
def mock_recommendation_engine():
    """Fixture para mock do Recommendation Engine"""
    mock_engine = Mock()
    
    # Mock do content_database
    mock_engine.content_database = {
        "bitcoin_fundamentals_quiz": {
            "id": "bitcoin_fundamentals_quiz",
            "type": "quiz",
            "domain": "bitcoin_basics",
            "difficulty": 0.3,
            "estimated_time": 15,
            "prerequisites": [],
            "learning_objectives": ["Entender Bitcoin", "Conhecer conceitos básicos"]
        },
        "defi_overview_quiz": {
            "id": "defi_overview_quiz",
            "type": "quiz",
            "domain": "defi",
            "difficulty": 0.6,
            "estimated_time": 20,
            "prerequisites": ["bitcoin_fundamentals_quiz"],
            "learning_objectives": ["Entender DeFi", "Conhecer protocolos"]
        }
    }
    
    # Mock do recommendation_cache
    mock_engine.recommendation_cache = {}
    
    # Mock do _get_user_profile
    mock_engine._get_user_profile = AsyncMock(return_value={
        "user_id": "test_user_123",
        "level": 2,
        "domains": {
            "bitcoin_basics": 0.8,
            "defi": 0.2
        },
        "learning_style": "visual",
        "completed_content": [],
        "preferred_difficulty": 0.5,
        "average_session_time": 20
    })
    
    # Mock do get_recommendations
    mock_engine.get_recommendations = AsyncMock(return_value=[
        Mock(
            content_id="defi_overview_quiz",
            content_type="quiz",
            relevance_score=0.87,
            difficulty_level=Mock(value="beginner"),
            estimated_time=20,
            reasoning="Gap crítico em DeFi",
            learning_objectives=["Entender DeFi", "Conhecer protocolos"]
        )
    ])
    
    # Mock do get_content_suggestions
    mock_engine.get_content_suggestions = AsyncMock(return_value=[
        Mock(
            content_id="bitcoin_fundamentals_quiz",
            content_type="quiz",
            relevance_score=0.75,
            difficulty_level=Mock(value="beginner"),
            estimated_time=15,
            reasoning="Sugestão para domínio bitcoin_basics",
            learning_objectives=["Entender Bitcoin"]
        )
    ])
    
    # Mock do get_adaptive_difficulty
    mock_engine.get_adaptive_difficulty = AsyncMock(return_value=0.65)
    
    return mock_engine


@pytest.fixture
def mock_behavioral_collector():
    """Fixture para mock do Behavioral Data Collector"""
    mock_collector = Mock()
    
    # Mock do data_storage
    mock_collector.data_storage = {}
    
    # Mock do session_tracking
    mock_collector.session_tracking = {}
    
    # Mock do collect_quiz_data
    mock_collector.collect_quiz_data = AsyncMock(return_value=Mock(
        user_id="test_user_123",
        session_id="test_session_456",
        quiz_id="bitcoin_fundamentals_quiz",
        performance_metrics={
            "engagement_score": 0.82,
            "avg_response_time": 14.3
        }
    ))
    
    # Mock do get_user_behavioral_history
    mock_collector.get_user_behavioral_history = AsyncMock(return_value=[
        {
            "session_id": "session1",
            "quiz_id": "quiz1",
            "performance_metrics": {"engagement_score": 0.8},
            "collected_at": "2024-01-15T10:30:00Z"
        }
    ])
    
    # Mock do get_user_performance_summary
    mock_collector.get_user_performance_summary = AsyncMock(return_value={
        "total_sessions": 5,
        "avg_response_time": 14.2,
        "avg_confidence": 0.78,
        "avg_engagement_score": 0.82,
        "performance_trend": "improving",
        "data_source": "firestore"
    })
    
    # Mock do start_learning_session
    mock_collector.start_learning_session = AsyncMock(return_value="test_session_789")
    
    # Mock do end_learning_session
    mock_collector.end_learning_session = AsyncMock(return_value={
        "session_id": "test_session_789",
        "user_id": "test_user_123",
        "duration_seconds": 300,
        "quizzes_completed": 1,
        "average_confidence": 0.8
    })
    
    return mock_collector


@pytest.fixture
def mock_learning_path_service(mock_ml_engine, mock_recommendation_engine, mock_behavioral_collector):
    """Fixture para mock do LearningPathService com IA"""
    mock_service = Mock()
    
    # Mock dos serviços de IA
    mock_service.ml_engine = mock_ml_engine
    mock_service.recommendation_engine = mock_recommendation_engine
    mock_service.behavioral_collector = mock_behavioral_collector
    
    # Mock do complete_mission_with_ai
    mock_service.complete_mission_with_ai = AsyncMock(return_value={
        "success": True,
        "score": 85.5,
        "points_earned": 200,
        "xp_earned": 100,
        "ai_insights": {
            "learning_pattern": {
                "type": "visual_learner",
                "strength": 0.85
            },
            "recommendations": [
                {
                    "content_id": "defi_overview_quiz",
                    "relevance_score": 0.87
                }
            ],
            "difficulty_suggestion": {
                "optimal_difficulty": 0.65,
                "confidence": 0.82
            },
            "performance_summary": {
                "engagement_score": 0.82
            }
        },
        "behavioral_data_collected": True,
        "session_id": "test_session_456"
    })
    
    # Mock do _generate_ai_insights
    mock_service._generate_ai_insights = AsyncMock(return_value={
        "learning_pattern": {
            "type": "visual_learner",
            "strength": 0.85,
            "context": {"avg_response_time": 12.3}
        },
        "recommendations": [
            {
                "content_id": "defi_overview_quiz",
                "type": "quiz",
                "relevance_score": 0.87,
                "reasoning": "Gap crítico em DeFi"
            }
        ],
        "difficulty_suggestion": {
            "optimal_difficulty": 0.65,
            "confidence": 0.82,
            "reasoning": "Baseado no perfil do usuário"
        },
        "performance_summary": {
            "engagement_score": 0.82,
            "response_consistency": 0.8,
            "learning_efficiency": 0.75
        }
    })
    
    return mock_service


@pytest.fixture
def ai_test_data():
    """Fixture com dados de teste para IA"""
    return {
        "user_profiles": {
            "visual_learner": {
                "user_id": "visual_user_123",
                "domains": {
                    "bitcoin_basics": 0.8,
                    "blockchain_technology": 0.7,
                    "defi": 0.3
                },
                "learning_style": "visual",
                "preferred_difficulty": 0.6
            },
            "methodical_learner": {
                "user_id": "methodical_user_456",
                "domains": {
                    "bitcoin_basics": 0.6,
                    "blockchain_technology": 0.5,
                    "defi": 0.2
                },
                "learning_style": "methodical",
                "preferred_difficulty": 0.4
            }
        },
        "quiz_data": {
            "bitcoin_fundamentals_quiz": {
                "domain": "bitcoin_basics",
                "difficulty": 0.3,
                "estimated_time": 15
            },
            "defi_overview_quiz": {
                "domain": "defi",
                "difficulty": 0.6,
                "estimated_time": 20
            }
        },
        "expected_patterns": {
            "visual_learner": {
                "pattern_type": "visual_learner",
                "strength": 0.85,
                "context": {
                    "avg_response_time": 12.3,
                    "confidence_variance": 0.05
                }
            },
            "methodical_learner": {
                "pattern_type": "methodical_learner",
                "strength": 0.8,
                "context": {
                    "avg_response_time": 28.5,
                    "confidence_variance": 0.2
                }
            }
        }
    }
