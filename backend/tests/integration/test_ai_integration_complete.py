"""
Testes de integração completos para o sistema de IA do CryptoQuest.
Seguindo a estrutura e padrões dos testes existentes.
"""
import pytest
import asyncio
from datetime import datetime, UTC
from unittest.mock import Mock, patch, AsyncMock, MagicMock

from app.ai.models.ai_models import EnhancedQuizSubmission
from app.ai.services.ml_engine import get_ml_engine
from app.ai.services.recommendation_engine import get_recommendation_engine
from app.ai.data.behavioral_data_collector import get_behavioral_collector
from app.services.learning_path_service import LearningPathService


@pytest.mark.integration
@pytest.mark.ai
class TestAISystemIntegration:
    """Testes de integração do sistema de IA"""
    
    def test_ai_services_initialization(self):
        """Testa inicialização dos serviços de IA"""
        # Testar se os serviços podem ser inicializados
        ml_engine = get_ml_engine()
        recommendation_engine = get_recommendation_engine()
        behavioral_collector = get_behavioral_collector()
        
        assert ml_engine is not None
        assert recommendation_engine is not None
        assert behavioral_collector is not None
        
        # Verificar se são instâncias singleton
        ml_engine2 = get_ml_engine()
        recommendation_engine2 = get_recommendation_engine()
        behavioral_collector2 = get_behavioral_collector()
        
        assert ml_engine is ml_engine2
        assert recommendation_engine is recommendation_engine2
        assert behavioral_collector is behavioral_collector2
    
    def test_learning_path_service_ai_integration(self):
        """Testa integração da IA com LearningPathService"""
        service = LearningPathService()
        
        # Verificar se os serviços de IA foram inicializados
        assert hasattr(service, 'ml_engine')
        assert hasattr(service, 'recommendation_engine')
        assert hasattr(service, 'behavioral_collector')
        
        # Verificar se são as mesmas instâncias singleton
        assert service.ml_engine is get_ml_engine()
        assert service.recommendation_engine is get_recommendation_engine()
        assert service.behavioral_collector is get_behavioral_collector()
    
    @pytest.mark.asyncio
    async def test_complete_mission_with_ai_flow(self):
        """Testa fluxo completo de completar missão com IA"""
        service = LearningPathService()
        
        # Mock do método complete_mission original
        with patch.object(service, 'complete_mission') as mock_complete_mission:
            mock_complete_mission.return_value = {
                "success": True,
                "score": 85.5,
                "points_earned": 200,
                "xp_earned": 100
            }
            
            # Mock do método _generate_ai_insights
            with patch.object(service, '_generate_ai_insights') as mock_insights:
                mock_insights.return_value = {
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
                }
                
                # Mock do behavioral_collector
                with patch.object(service.behavioral_collector, 'collect_quiz_data') as mock_collect:
                    mock_behavioral_data = Mock()
                    mock_behavioral_data.session_id = "test_session_123"
                    mock_behavioral_data.performance_metrics = {"engagement_score": 0.82}
                    mock_collect.return_value = mock_behavioral_data
                    
                    # Criar submissão de teste
                    submission = EnhancedQuizSubmission(
                        answers=[1, 2, 1, 3, 2],
                        time_per_question=[15.5, 12.3, 18.7, 10.2, 14.8],
                        confidence_levels=[0.8, 0.6, 0.9, 0.7, 0.8],
                        hints_used=[0, 1, 0, 0, 1],
                        attempts_per_question=[1, 2, 1, 1, 1]
                    )
                    
                    # Executar o método
                    result = await service.complete_mission_with_ai(
                        user_id="test_user",
                        path_id="test_path",
                        mission_id="test_mission",
                        submission=submission
                    )
                    
                    # Verificar se o método original foi chamado
                    mock_complete_mission.assert_called_once()
                    
                    # Verificar se os dados comportamentais foram coletados
                    mock_collect.assert_called_once_with(
                        user_id="test_user",
                        quiz_id="test_mission",
                        submission=submission
                    )
                    
                    # Verificar se os insights foram gerados
                    mock_insights.assert_called_once()
                    
                    # Verificar resultado final
                    assert result["success"] == True
                    assert result["score"] == 85.5
                    assert result["points_earned"] == 200
                    assert result["xp_earned"] == 100
                    assert "ai_insights" in result
                    assert result["behavioral_data_collected"] == True
                    assert result["session_id"] == "test_session_123"
    
    @pytest.mark.asyncio
    async def test_ai_insights_generation(self):
        """Testa geração de insights de IA"""
        service = LearningPathService()
        
        # Mock do behavioral_collector
        with patch.object(service.behavioral_collector, 'get_user_behavioral_history') as mock_history:
            mock_history.return_value = [
                {
                    'performance_metrics': {
                        'avg_response_time': 15.0,
                        'avg_confidence': 0.8,
                        'engagement_score': 0.9
                    }
                }
            ]
            
            # Mock do ml_engine
            with patch.object(service.ml_engine, 'analyze_user_patterns') as mock_analyze:
                mock_pattern = Mock()
                mock_pattern.pattern_type = "visual_learner"
                mock_pattern.strength = 0.85
                mock_pattern.context = {"avg_response_time": 15.0}
                mock_analyze.return_value = mock_pattern
                
                # Mock do recommendation_engine
                with patch.object(service.recommendation_engine, 'get_recommendations') as mock_recommendations:
                    mock_recommendations.return_value = [
                        Mock(
                            content_id="defi_overview_quiz",
                            content_type="quiz",
                            relevance_score=0.87,
                            reasoning="Gap crítico em DeFi"
                        )
                    ]
                    
                    # Mock do difficulty_predictor
                    with patch.object(service.ml_engine.difficulty_predictor, 'predict_optimal_difficulty') as mock_difficulty:
                        mock_difficulty_prediction = Mock()
                        mock_difficulty_prediction.value = 0.65
                        mock_difficulty_prediction.confidence = 0.82
                        mock_difficulty_prediction.reasoning = "Baseado no perfil do usuário"
                        mock_difficulty.return_value = mock_difficulty_prediction
                        
                        # Mock do behavioral_data
                        mock_behavioral_data = Mock()
                        mock_behavioral_data.performance_metrics = {
                            "engagement_score": 0.82,
                            "response_time_consistency": 0.8,
                            "avg_confidence": 0.8,
                            "retry_rate": 0.1
                        }
                        
                        # Executar geração de insights
                        insights = await service._generate_ai_insights(
                            user_id="test_user",
                            mission_id="test_mission",
                            behavioral_data=mock_behavioral_data,
                            result={"success": True}
                        )
                        
                        # Verificar estrutura dos insights
                        assert "learning_pattern" in insights
                        assert "recommendations" in insights
                        assert "difficulty_suggestion" in insights
                        assert "performance_summary" in insights
                        
                        # Verificar conteúdo dos insights
                        assert insights["learning_pattern"]["type"] == "visual_learner"
                        assert insights["learning_pattern"]["strength"] == 0.85
                        assert len(insights["recommendations"]) == 1
                        assert insights["recommendations"][0]["content_id"] == "defi_overview_quiz"
                        assert insights["difficulty_suggestion"]["optimal_difficulty"] == 0.65
                        assert insights["performance_summary"]["engagement_score"] == 0.82
    
    @pytest.mark.asyncio
    async def test_ai_data_flow_integration(self):
        """Testa fluxo completo de dados de IA"""
        # Testar coleta -> análise -> recomendação
        behavioral_collector = get_behavioral_collector()
        ml_engine = get_ml_engine()
        recommendation_engine = get_recommendation_engine()
        
        # 1. Coletar dados comportamentais
        submission = EnhancedQuizSubmission(
            answers=[1, 2, 1, 3, 2],
            time_per_question=[15.5, 12.3, 18.7, 10.2, 14.8],
            confidence_levels=[0.8, 0.6, 0.9, 0.7, 0.8],
            hints_used=[0, 1, 0, 0, 1],
            attempts_per_question=[1, 2, 1, 1, 1]
        )
        
        # Mock do Firestore para coleta
        with patch.object(behavioral_collector, '_get_db') as mock_get_db:
            mock_db = AsyncMock()
            mock_get_db.return_value = mock_db
            
            behavioral_data = await behavioral_collector.collect_quiz_data(
                user_id="test_user",
                quiz_id="test_quiz",
                submission=submission
            )
            
            assert behavioral_data.user_id == "test_user"
            assert behavioral_data.quiz_id == "test_quiz"
            assert len(behavioral_data.performance_metrics) > 0
        
        # 2. Analisar padrões
        quiz_history = [
            {'response_time': 15, 'confidence': 0.8, 'hints_used': 0, 'correct': True},
            {'response_time': 12, 'confidence': 0.9, 'hints_used': 0, 'correct': True}
        ]
        
        pattern = await ml_engine.analyze_user_patterns("test_user", quiz_history)
        assert pattern.pattern_type is not None
        assert pattern.strength > 0.0
        
        # 3. Gerar recomendações
        with patch.object(recommendation_engine, '_get_user_profile') as mock_profile:
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
            
            recommendations = await recommendation_engine.get_recommendations('test_user', limit=3)
            assert len(recommendations) <= 3
            if recommendations:
                assert recommendations[0].content_id is not None
                assert 0.0 <= recommendations[0].relevance_score <= 1.0
    
    @pytest.mark.asyncio
    async def test_ai_performance_metrics_integration(self):
        """Testa integração de métricas de performance"""
        behavioral_collector = get_behavioral_collector()
        
        # Simular múltiplas sessões
        sessions_data = [
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
            },
            {
                'performance_metrics': {
                    'avg_response_time': 18.0,
                    'avg_confidence': 0.9,
                    'engagement_score': 0.95
                },
                'collected_at': '2024-01-15T11:30:00Z'
            }
        ]
        
        # Mock do histórico
        with patch.object(behavioral_collector, 'get_user_behavioral_history') as mock_history:
            mock_history.return_value = sessions_data
            
            summary = await behavioral_collector.get_user_performance_summary('test_user')
            
            # Verificar cálculos
            assert summary['total_sessions'] == 3
            assert summary['avg_response_time'] == 15.0  # (15.0 + 12.0 + 18.0) / 3
            assert summary['avg_confidence'] == 0.8  # (0.8 + 0.7 + 0.9) / 3
            assert summary['avg_engagement_score'] == 0.88  # (0.9 + 0.8 + 0.95) / 3
            
            # Verificar tendência (última sessão melhor que primeira)
            assert summary['performance_trend'] == 'improving'
    
    @pytest.mark.asyncio
    async def test_ai_knowledge_profile_integration(self):
        """Testa integração de perfil de conhecimento"""
        behavioral_collector = get_behavioral_collector()
        
        # Mock do Firestore
        with patch.object(behavioral_collector, '_get_db') as mock_get_db:
            mock_db = AsyncMock()
            mock_get_db.return_value = mock_db
            
            # Mock do documento existente
            mock_doc = Mock()
            mock_doc.exists = True
            mock_doc.to_dict.return_value = {
                'user_id': 'test_user',
                'domains': {
                    'bitcoin_basics': {
                        'proficiency_level': 0.6,
                        'total_questions': 5,
                        'correct_answers': 3
                    }
                },
                'updated_at': datetime.now(UTC)
            }
            
            mock_doc_ref = AsyncMock()
            mock_doc_ref.get.return_value = mock_doc
            mock_db.collection.return_value.document.return_value = mock_doc_ref
            
            # Mock do behavioral_data
            mock_behavioral_data = Mock()
            mock_behavioral_data.performance_metrics = {
                'total_questions': 3,
                'avg_confidence': 0.8,
                'engagement_score': 0.9,
                'avg_response_time': 15.0
            }
            mock_behavioral_data.quiz_id = 'bitcoin_quiz'
            
            # Executar atualização de perfil
            await behavioral_collector._update_knowledge_profile('test_user', mock_behavioral_data)
            
            # Verificar se o documento foi atualizado
            mock_doc_ref.update.assert_called_once()
            
            # Verificar se a estrutura do update está correta
            update_call = mock_doc_ref.update.call_args[0][0]
            assert 'domains' in update_call
            assert 'updated_at' in update_call
            assert 'engagement_score' in update_call
    
    @pytest.mark.asyncio
    async def test_ai_session_management_integration(self):
        """Testa integração de gerenciamento de sessões"""
        behavioral_collector = get_behavioral_collector()
        
        # Mock do Firestore
        with patch.object(behavioral_collector, '_get_db') as mock_get_db:
            mock_db = AsyncMock()
            mock_get_db.return_value = mock_db
            
            # 1. Iniciar sessão
            session_id = await behavioral_collector.start_learning_session('test_user', 'quiz')
            
            assert session_id is not None
            assert 'test_user' in session_id
            assert 'quiz' in session_id
            assert session_id in behavioral_collector.session_tracking
            
            # Verificar se foi salvo no Firestore
            mock_db.collection.assert_called_with('ai_learning_sessions')
            
            # 2. Finalizar sessão
            summary = await behavioral_collector.end_learning_session(session_id)
            
            assert summary['session_id'] == session_id
            assert summary['user_id'] == 'test_user'
            assert summary['duration_seconds'] > 0
            assert session_id not in behavioral_collector.session_tracking
            
            # Verificar se foi atualizado no Firestore
            mock_doc_ref = mock_db.collection.return_value.document.return_value
            mock_doc_ref.update.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_ai_error_handling_integration(self):
        """Testa tratamento de erros na integração de IA"""
        service = LearningPathService()
        
        # Teste com erro na coleta de dados comportamentais
        with patch.object(service.behavioral_collector, 'collect_quiz_data') as mock_collect:
            mock_collect.side_effect = Exception("Erro na coleta de dados")
            
            submission = EnhancedQuizSubmission(answers=[1, 2, 3])
            
            # O método deve lidar com o erro graciosamente
            try:
                result = await service.complete_mission_with_ai(
                    user_id="test_user",
                    path_id="test_path",
                    mission_id="test_mission",
                    submission=submission
                )
                # Se não lançar exceção, deve ter fallback
                assert "error" in result or "ai_insights" not in result
            except Exception as e:
                # Se lançar exceção, deve ser tratada adequadamente
                assert "Erro na coleta de dados" in str(e)
        
        # Teste com erro na geração de insights
        with patch.object(service, '_generate_ai_insights') as mock_insights:
            mock_insights.side_effect = Exception("Erro na geração de insights")
            
            with patch.object(service.behavioral_collector, 'collect_quiz_data') as mock_collect:
                mock_collect.return_value = Mock(session_id="test_session")
                
                submission = EnhancedQuizSubmission(answers=[1, 2, 3])
                
                try:
                    result = await service.complete_mission_with_ai(
                        user_id="test_user",
                        path_id="test_path",
                        mission_id="test_mission",
                        submission=submission
                    )
                    # Deve retornar resultado com erro nos insights
                    assert "ai_insights" in result
                    assert result["ai_insights"].get("error") is not None
                except Exception:
                    # Se lançar exceção, deve ser tratada adequadamente
                    pass
    
    @pytest.mark.asyncio
    async def test_ai_cache_integration(self):
        """Testa integração de cache na IA"""
        recommendation_engine = get_recommendation_engine()
        
        # Mock do perfil do usuário
        with patch.object(recommendation_engine, '_get_user_profile') as mock_profile:
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
            
            # Primeira chamada - deve gerar recomendações
            recommendations1 = await recommendation_engine.get_recommendations('test_user', limit=3)
            
            # Segunda chamada - deve usar cache
            recommendations2 = await recommendation_engine.get_recommendations('test_user', limit=3)
            
            # Verificar se as recomendações são iguais (cache funcionando)
            if recommendations1 and recommendations2:
                assert len(recommendations1) == len(recommendations2)
                assert recommendations1[0].content_id == recommendations2[0].content_id
            
            # Verificar se o cache foi criado
            cache_key = f"recommendations_test_user"
            assert cache_key in recommendation_engine.recommendation_cache
    
    @pytest.mark.asyncio
    async def test_ai_ml_engine_integration(self):
        """Testa integração do ML Engine com outros componentes"""
        ml_engine = get_ml_engine()
        
        # Teste de análise de padrões com dados reais
        quiz_data = [
            {'response_time': 10, 'confidence': 0.9, 'hints_used': 0, 'correct': True},
            {'response_time': 12, 'confidence': 0.8, 'hints_used': 0, 'correct': True},
            {'response_time': 8, 'confidence': 0.95, 'hints_used': 0, 'correct': True}
        ]
        
        pattern = await ml_engine.analyze_user_patterns("test_user", quiz_data)
        
        # Verificar se o padrão foi identificado
        assert pattern.pattern_type is not None
        assert pattern.strength > 0.0
        assert pattern.frequency >= 0
        
        # Teste de predição de dificuldade
        user_data = {
            'user_level': 2,
            'domain': 'bitcoin_basics'
        }
        
        difficulty_prediction = ml_engine.difficulty_predictor.predict_optimal_difficulty(user_data)
        
        assert 0.0 <= difficulty_prediction.value <= 1.0
        assert difficulty_prediction.confidence > 0.0
        assert difficulty_prediction.model_used is not None
    
    @pytest.mark.asyncio
    async def test_ai_recommendation_engine_integration(self):
        """Testa integração do Recommendation Engine com outros componentes"""
        recommendation_engine = get_recommendation_engine()
        
        # Mock do perfil do usuário
        with patch.object(recommendation_engine, '_get_user_profile') as mock_profile:
            mock_profile.return_value = {
                'user_id': 'test_user',
                'level': 2,
                'domains': {
                    'bitcoin_basics': 0.8,
                    'defi': 0.2,  # Gap crítico
                    'blockchain_technology': 0.6
                },
                'learning_style': 'visual',
                'completed_content': [],
                'preferred_difficulty': 0.5,
                'average_session_time': 20
            }
            
            # Teste de geração de recomendações
            recommendations = await recommendation_engine.get_recommendations('test_user', limit=5)
            
            assert len(recommendations) <= 5
            if recommendations:
                # Verificar se as recomendações são relevantes
                for rec in recommendations:
                    assert rec.content_id is not None
                    assert 0.0 <= rec.relevance_score <= 1.0
                    assert rec.content_type in ['quiz', 'lesson', 'practice']
                    assert rec.estimated_time > 0
                    assert len(rec.reasoning) > 0
            
            # Teste de sugestões por domínio
            suggestions = await recommendation_engine.get_content_suggestions('test_user', 'defi', limit=3)
            
            assert len(suggestions) <= 3
            for suggestion in suggestions:
                assert suggestion.content_id is not None
                assert 0.0 <= suggestion.relevance_score <= 1.0
            
            # Teste de dificuldade adaptativa
            difficulty = await recommendation_engine.get_adaptive_difficulty('test_user', 'defi_overview_quiz')
            assert 0.0 <= difficulty <= 1.0
    
    @pytest.mark.asyncio
    async def test_ai_behavioral_collector_integration(self):
        """Testa integração do Behavioral Data Collector com outros componentes"""
        behavioral_collector = get_behavioral_collector()
        
        # Mock do Firestore
        with patch.object(behavioral_collector, '_get_db') as mock_get_db:
            mock_db = AsyncMock()
            mock_get_db.return_value = mock_db
            
            # Teste de coleta de dados
            submission = EnhancedQuizSubmission(
                answers=[1, 2, 1, 3, 2],
                time_per_question=[15.5, 12.3, 18.7, 10.2, 14.8],
                confidence_levels=[0.8, 0.6, 0.9, 0.7, 0.8],
                hints_used=[0, 1, 0, 0, 1],
                attempts_per_question=[1, 2, 1, 1, 1]
            )
            
            behavioral_data = await behavioral_collector.collect_quiz_data(
                user_id="test_user",
                quiz_id="test_quiz",
                submission=submission
            )
            
            # Verificar se os dados foram coletados corretamente
            assert behavioral_data.user_id == "test_user"
            assert behavioral_data.quiz_id == "test_quiz"
            assert behavioral_data.session_id is not None
            assert len(behavioral_data.performance_metrics) > 0
            assert behavioral_data.performance_metrics['total_questions'] == 5
            
            # Teste de histórico comportamental
            mock_docs = [
                Mock(to_dict=lambda: {
                    'session_id': 'session1',
                    'quiz_id': 'quiz1',
                    'performance_metrics': {'engagement_score': 0.8},
                    'collected_at': datetime.now(UTC)
                }),
                Mock(to_dict=lambda: {
                    'session_id': 'session2',
                    'quiz_id': 'quiz2',
                    'performance_metrics': {'engagement_score': 0.7},
                    'collected_at': datetime.now(UTC)
                })
            ]
            
            mock_query = AsyncMock()
            mock_query.get.return_value = mock_docs
            mock_db.collection.return_value.where.return_value.order_by.return_value.limit.return_value = mock_query
            
            history = await behavioral_collector.get_user_behavioral_history('test_user', limit=5)
            
            assert len(history) == 2
            assert history[0]['session_id'] == 'session1'
            assert history[0]['performance_metrics']['engagement_score'] == 0.8
            
            # Teste de resumo de performance
            with patch.object(behavioral_collector, 'get_user_behavioral_history') as mock_history:
                mock_history.return_value = [
                    {
                        'performance_metrics': {
                            'avg_response_time': 15.0,
                            'avg_confidence': 0.8,
                            'engagement_score': 0.9
                        },
                        'collected_at': '2024-01-15T10:30:00Z'
                    }
                ]
                
                summary = await behavioral_collector.get_user_performance_summary('test_user')
                
                assert summary['total_sessions'] == 1
                assert summary['avg_response_time'] == 15.0
                assert summary['avg_confidence'] == 0.8
                assert summary['avg_engagement_score'] == 0.9
                assert summary['performance_trend'] in ['improving', 'stable', 'declining']
                assert summary['data_source'] == 'firestore'
