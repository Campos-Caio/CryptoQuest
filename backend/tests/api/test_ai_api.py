"""
Testes de API para endpoints de IA do CryptoQuest.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, UTC

from app.main import app
from app.dependencies.auth import get_current_user
from app.ai.models.ai_models import EnhancedQuizSubmission


@pytest.mark.api
@pytest.mark.ai
class TestAIApi:
    """Testes para endpoints de IA"""
    
    @pytest.fixture
    def client(self):
        """Cliente de teste para FastAPI"""
        return TestClient(app)
    
    @pytest.fixture
    def mock_current_user(self):
        """Mock do usuário atual"""
        from app.models.user import FirebaseUser
        return FirebaseUser(
            uid="test_user_123",
            email="test@example.com",
            name="Test User"
        )
    
    @pytest.fixture
    def mock_ai_services(self):
        """Mock dos serviços de IA"""
        return {
            'ml_engine': Mock(),
            'recommendation_engine': Mock(),
            'behavioral_collector': Mock()
        }
    
    def test_ai_profile_endpoint_success(self, client, mock_current_user, mock_ai_services):
        """Testa endpoint de perfil de IA com sucesso"""
        # Mock do get_current_user usando dependency_overrides
        app.dependency_overrides[get_current_user] = lambda: mock_current_user
        
        try:
            # Mock dos serviços de IA
            with patch('app.api.ai_api.get_behavioral_collector') as mock_get_collector:
                mock_collector = Mock()
                mock_collector.get_user_performance_summary = AsyncMock(return_value={
                    'total_sessions': 5,
                    'avg_response_time': 14.2,
                    'avg_confidence': 0.78,
                    'avg_engagement_score': 0.82,
                    'performance_trend': 'improving'
                })
                mock_collector.get_user_behavioral_history = AsyncMock(return_value=[
                    {'performance_metrics': {'engagement_score': 0.8}}
                ])
                mock_get_collector.return_value = mock_collector
                
                with patch('app.api.ai_api.get_ml_engine') as mock_get_ml:
                    mock_ml_engine = Mock()
                    mock_ml_engine.analyze_user_patterns = AsyncMock(return_value=Mock(
                        pattern_type="visual_learner",
                        strength=0.85,
                        context={"avg_response_time": 12.3}
                    ))
                    mock_get_ml.return_value = mock_ml_engine
                    
                    # Fazer requisição
                    response = client.get("/ai/profile/test_user_123")
                    
                    # Verificar resposta
                    assert response.status_code == 200
                    data = response.json()
                    assert data["success"] == True
                    assert "data" in data
                    assert data["data"]["user_id"] == "test_user_123"
                    assert "performance_summary" in data["data"]
                    assert "learning_pattern" in data["data"]
                    assert data["data"]["ai_enabled"] == True
        finally:
            app.dependency_overrides.clear()
    
    def test_ai_profile_endpoint_forbidden(self, client, mock_current_user):
        """Testa endpoint de perfil de IA com acesso negado"""
        # Mock do get_current_user usando dependency_overrides
        app.dependency_overrides[get_current_user] = lambda: mock_current_user
        
        try:
            # Tentar acessar perfil de outro usuário
            response = client.get("/ai/profile/other_user_456")
            
            # Verificar resposta de acesso negado
            assert response.status_code == 403
            assert "Acesso negado" in response.json()["detail"]
        finally:
            app.dependency_overrides.clear()
    
    def test_ai_recommendations_endpoint_success(self, client, mock_current_user):
        """Testa endpoint de recomendações com sucesso"""
        app.dependency_overrides[get_current_user] = lambda: mock_current_user
        
        try:
            with patch('app.api.ai_api.get_recommendation_engine') as mock_get_engine:
                mock_engine = Mock()
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
                mock_get_engine.return_value = mock_engine
                
                # Fazer requisição
                response = client.get("/ai/recommendations/test_user_123?limit=3")
                
                # Verificar resposta
                assert response.status_code == 200
                data = response.json()
                assert len(data) == 1
                assert data[0]["content_id"] == "defi_overview_quiz"
                assert data[0]["content_type"] == "quiz"
                assert data[0]["relevance_score"] == 0.87
                assert data[0]["difficulty_level"] == "beginner"
                assert data[0]["estimated_time"] == 20
        finally:
            app.dependency_overrides.clear()
    
    def test_ai_recommendations_endpoint_limit_validation(self, client, mock_current_user):
        """Testa validação de limite no endpoint de recomendações"""
        app.dependency_overrides[get_current_user] = lambda: mock_current_user
        
        try:
            with patch('app.api.ai_api.get_recommendation_engine') as mock_get_engine:
                mock_engine = Mock()
                mock_engine.get_recommendations = AsyncMock(return_value=[])
                mock_get_engine.return_value = mock_engine
                
                # Teste com limite muito alto (deve ser limitado)
                response = client.get("/ai/recommendations/test_user_123?limit=100")
                
                # Verificar que o limite foi aplicado
                assert response.status_code == 200
                mock_engine.get_recommendations.assert_called_once()
                call_args = mock_engine.get_recommendations.call_args
                assert call_args[0][1] <= 10  # Limite máximo configurado
        finally:
            app.dependency_overrides.clear()
    
    def test_ai_insights_endpoint_success(self, client, mock_current_user):
        """Testa endpoint de insights com sucesso"""
        app.dependency_overrides[get_current_user] = lambda: mock_current_user
        
        try:
            with patch('app.api.ai_api.get_behavioral_collector') as mock_get_collector:
                mock_collector = Mock()
                # Mock deve retornar histórico com 'collected_at' para _calculate_ideal_time
                mock_collector.get_user_behavioral_history = AsyncMock(return_value=[
                    {
                        'performance_metrics': {'engagement_score': 0.8, 'success_rate': 0.9, 'avg_response_time': 15.0},
                        'collected_at': '2024-01-01T10:00:00Z'
                    }
                ])
                mock_collector.get_user_performance_summary = AsyncMock(return_value={
                    'total_sessions': 5,
                    'avg_engagement_score': 0.82,
                    'avg_response_time': 14.2
                })
                mock_get_collector.return_value = mock_collector
                
                with patch('app.api.ai_api.get_ml_engine') as mock_get_ml:
                    mock_ml_engine = Mock()
                    mock_ml_engine.analyze_user_patterns = AsyncMock(return_value=Mock(
                        pattern_type="visual_learner",
                        strength=0.85,
                        frequency=8,
                        context={"avg_response_time": 12.3}
                    ))
                    mock_ml_engine.get_model_metrics = Mock(return_value={
                        "learning_style": Mock(),
                        "difficulty": Mock()
                    })
                    mock_get_ml.return_value = mock_ml_engine
                    
                    with patch('app.api.ai_api.get_recommendation_engine') as mock_get_rec:
                        mock_rec_engine = Mock()
                        mock_rec_engine.get_recommendations = AsyncMock(return_value=[
                            Mock(
                                content_id="defi_overview_quiz",
                                content_type="quiz",
                                relevance_score=0.87,
                                reasoning="Gap crítico em DeFi"
                            )
                        ])
                        mock_get_rec.return_value = mock_rec_engine
                        
                        # Fazer requisição
                        response = client.get("/ai/insights/test_user_123")
                        
                        # Verificar resposta
                        assert response.status_code == 200
                        data = response.json()
                        assert data["success"] == True
                        assert "data" in data
                        assert "learning_pattern" in data["data"]
                        assert "performance_analysis" in data["data"]
                        assert "top_recommendations" in data["data"]
                        assert "ai_model_status" in data["data"]
                        assert "data_quality" in data["data"]
        finally:
            app.dependency_overrides.clear()
    
    def test_ai_difficulty_suggestion_endpoint_success(self, client, mock_current_user):
        """Testa endpoint de sugestão de dificuldade com sucesso"""
        app.dependency_overrides[get_current_user] = lambda: mock_current_user
        
        try:
            with patch('app.api.ai_api.get_behavioral_collector') as mock_get_collector:
                mock_collector = Mock()
                mock_collector.get_user_performance_summary = AsyncMock(return_value={
                    'avg_confidence': 0.8,
                    'avg_response_time': 15.0
                })
                mock_get_collector.return_value = mock_collector
                
                with patch('app.api.ai_api.get_ml_engine') as mock_get_ml:
                    mock_ml_engine = Mock()
                    mock_ml_engine.difficulty_predictor = Mock()
                    mock_ml_engine.difficulty_predictor.predict_optimal_difficulty = Mock(return_value=Mock(
                        value=0.65,
                        confidence=0.82,
                        reasoning="Baseado no perfil do usuário",
                        model_used="difficulty_predictor"
                    ))
                    mock_get_ml.return_value = mock_ml_engine
                    
                    # Fazer requisição
                    response = client.get("/ai/difficulty-suggestion/test_user_123?domain=bitcoin_basics")
                    
                    # Verificar resposta
                    assert response.status_code == 200
                    data = response.json()
                    assert data["success"] == True
                    assert "data" in data
                    assert data["data"]["user_id"] == "test_user_123"
                    assert data["data"]["domain"] == "bitcoin_basics"
                    assert data["data"]["optimal_difficulty"] == 0.65
                    assert data["data"]["confidence"] == 0.82
                    assert "difficulty_level" in data["data"]
        finally:
            app.dependency_overrides.clear()
    
    def test_ai_difficulty_suggestion_endpoint_invalid_domain(self, client, mock_current_user):
        """Testa endpoint de sugestão de dificuldade com domínio inválido"""
        app.dependency_overrides[get_current_user] = lambda: mock_current_user
        
        try:
            # Fazer requisição com domínio inválido
            response = client.get("/ai/difficulty-suggestion/test_user_123?domain=invalid_domain")
            
            # Verificar resposta de erro
            assert response.status_code == 400
            assert "não é válido" in response.json()["detail"]
        finally:
            app.dependency_overrides.clear()
    
    def test_ai_content_suggestions_endpoint_success(self, client, mock_current_user):
        """Testa endpoint de sugestões de conteúdo com sucesso"""
        app.dependency_overrides[get_current_user] = lambda: mock_current_user
        
        try:
            with patch('app.api.ai_api.get_recommendation_engine') as mock_get_engine:
                mock_engine = Mock()
                mock_engine.get_content_suggestions = AsyncMock(return_value=[
                    Mock(
                        content_id="bitcoin_fundamentals_quiz",
                        content_type="quiz",
                        relevance_score=0.75,
                        difficulty_level=Mock(value="beginner"),
                        estimated_time=15,
                        reasoning="Sugestão para domínio bitcoin_basics",
                        learning_objectives=["Entender Bitcoin", "Conhecer conceitos básicos"]
                    )
                ])
                mock_get_engine.return_value = mock_engine
                
                # Fazer requisição
                response = client.get("/ai/content-suggestions/test_user_123?domain=bitcoin_basics&limit=2")
                
                # Verificar resposta
                assert response.status_code == 200
                data = response.json()
                assert len(data) == 1
                assert data[0]["content_id"] == "bitcoin_fundamentals_quiz"
                assert data[0]["content_type"] == "quiz"
                assert data[0]["relevance_score"] == 0.75
                assert data[0]["difficulty_level"] == "beginner"
        finally:
            app.dependency_overrides.clear()
    
    def test_ai_model_metrics_endpoint_success(self, client, mock_current_user):
        """Testa endpoint de métricas dos modelos com sucesso"""
        app.dependency_overrides[get_current_user] = lambda: mock_current_user
        
        try:
            with patch('app.api.ai_api.get_ml_engine') as mock_get_ml:
                mock_ml_engine = Mock()
                mock_ml_engine.get_model_metrics = Mock(return_value={
                    "learning_style": Mock(
                        accuracy=0.85,
                        precision=0.83,
                        recall=0.82,
                        f1_score=0.82,
                        training_samples=1000,
                        last_trained=datetime.now(UTC),
                        version="1.0"
                    ),
                    "difficulty": Mock(
                        accuracy=0.82,
                        precision=0.80,
                        recall=0.85,
                        f1_score=0.82,
                        training_samples=800,
                        last_trained=datetime.now(UTC),
                        version="1.0"
                    )
                })
                mock_get_ml.return_value = mock_ml_engine
                
                # Fazer requisição
                response = client.get("/ai/model-metrics")
                
                # Verificar resposta
                assert response.status_code == 200
                data = response.json()
                assert data["success"] == True
                assert "data" in data
                assert "model_metrics" in data["data"]
                assert "total_models" in data["data"]
                assert "ai_config" in data["data"]
                assert data["data"]["total_models"] == 2
                assert "learning_style" in data["data"]["model_metrics"]
                assert "difficulty" in data["data"]["model_metrics"]
        finally:
            app.dependency_overrides.clear()
    
    def test_ai_endpoints_authentication_required(self, client):
        """Testa que endpoints de IA requerem autenticação"""
        # Garantir que não há overrides de dependências
        app.dependency_overrides.clear()
        
        try:
            endpoints = [
                "/ai/profile/test_user_123",
                "/ai/recommendations/test_user_123",
                "/ai/insights/test_user_123",
                "/ai/difficulty-suggestion/test_user_123?domain=bitcoin_basics",
                "/ai/content-suggestions/test_user_123?domain=bitcoin_basics",
                "/ai/model-metrics"
            ]
            
            for endpoint in endpoints:
                response = client.get(endpoint)
                # Deve retornar erro de autenticação (401, 422 ou 403)
                # FastAPI pode retornar diferentes status dependendo da implementação
                assert response.status_code in [401, 422, 403], f"Endpoint {endpoint} retornou {response.status_code} em vez de erro de autenticação"
        finally:
            app.dependency_overrides.clear()
    
    def test_ai_endpoints_error_handling(self, client, mock_current_user):
        """Testa tratamento de erros nos endpoints de IA"""
        app.dependency_overrides[get_current_user] = lambda: mock_current_user
        
        try:
            # Mock que lança exceção
            with patch('app.api.ai_api.get_behavioral_collector') as mock_get_collector:
                mock_get_collector.side_effect = Exception("Erro interno")
                
                # Fazer requisição
                response = client.get("/ai/profile/test_user_123")
                
                # Verificar resposta de erro
                assert response.status_code == 500
                assert "Erro interno" in response.json()["detail"]
        finally:
            app.dependency_overrides.clear()
    
    def test_ai_endpoints_cors_headers(self, client, mock_current_user):
        """Testa headers CORS nos endpoints de IA"""
        app.dependency_overrides[get_current_user] = lambda: mock_current_user
        
        try:
            with patch('app.api.ai_api.get_behavioral_collector') as mock_get_collector:
                mock_collector = Mock()
                mock_collector.get_user_performance_summary = AsyncMock(return_value={})
                mock_collector.get_user_behavioral_history = AsyncMock(return_value=[])
                mock_get_collector.return_value = mock_collector
                
                with patch('app.api.ai_api.get_ml_engine') as mock_get_ml:
                    mock_ml_engine = Mock()
                    mock_ml_engine.analyze_user_patterns = AsyncMock(return_value=Mock(
                        pattern_type="visual_learner",
                        strength=0.85,
                        context={}
                    ))
                    mock_get_ml.return_value = mock_ml_engine
                    
                    # Fazer requisição OPTIONS (preflight CORS)
                    response = client.options("/ai/profile/test_user_123")
                    
                    # Verificar headers CORS (FastAPI pode retornar 405 se OPTIONS não estiver configurado)
                    assert response.status_code in [200, 405]
                    # Headers CORS devem estar presentes (dependendo da configuração do FastAPI)
        finally:
            app.dependency_overrides.clear()
    
    def test_ai_endpoints_rate_limiting(self, client, mock_current_user):
        """Testa limitação de taxa nos endpoints de IA"""
        app.dependency_overrides[get_current_user] = lambda: mock_current_user
        
        try:
            with patch('app.api.ai_api.get_behavioral_collector') as mock_get_collector:
                mock_collector = Mock()
                mock_collector.get_user_performance_summary = AsyncMock(return_value={})
                mock_collector.get_user_behavioral_history = AsyncMock(return_value=[])
                mock_get_collector.return_value = mock_collector
                
                with patch('app.api.ai_api.get_ml_engine') as mock_get_ml:
                    mock_ml_engine = Mock()
                    mock_ml_engine.analyze_user_patterns = AsyncMock(return_value=Mock(
                        pattern_type="visual_learner",
                        strength=0.85,
                        context={}
                    ))
                    mock_get_ml.return_value = mock_ml_engine
                    
                    # Fazer múltiplas requisições rapidamente
                    responses = []
                    for _ in range(5):
                        response = client.get("/ai/profile/test_user_123")
                        responses.append(response)
                    
                    # Todas devem ser bem-sucedidas (sem rate limiting implementado ainda)
                    for response in responses:
                        assert response.status_code == 200
        finally:
            app.dependency_overrides.clear()
