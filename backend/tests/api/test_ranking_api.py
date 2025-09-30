"""
Testes de API para endpoints de ranking.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock
from fastapi.testclient import TestClient
from datetime import datetime, timezone

from app.main import app
from app.models.ranking import Ranking, RankingEntry, RankingType
from app.services.ranking_service import get_ranking_service


class TestRankingAPI:
    """Testes para endpoints de ranking"""
    
    @pytest.fixture
    def client(self):
        """Cliente de teste FastAPI"""
        return TestClient(app)
    
    @pytest.fixture
    def mock_ranking_service(self):
        """Mock do RankingService"""
        mock = AsyncMock()
        return mock
    
    @pytest.fixture
    def sample_ranking(self):
        """Ranking de exemplo para testes"""
        return Ranking(
            type=RankingType.GLOBAL,
            period="2024-01",
            total_users=2,
            entries=[
                RankingEntry(
                    user_id="user1",
                    name="User1",
                    email="user1@test.com",
                    points=1000,
                    level=5,
                    xp=2500,
                    rank=1,
                    last_activity=datetime.now(timezone.utc)
                ),
                RankingEntry(
                    user_id="user2",
                    name="User2",
                    email="user2@test.com",
                    points=800,
                    level=4,
                    xp=2000,
                    rank=2,
                    last_activity=datetime.now(timezone.utc)
                )
            ],
            generated_at=datetime.now(timezone.utc)
        )

    def test_get_global_ranking(self, client, mock_ranking_service, sample_ranking):
        """Testa busca de ranking global"""
        # Mock do serviço
        mock_ranking_service.generate_global_ranking.return_value = sample_ranking
        
        # Substituir dependência
        app.dependency_overrides[get_ranking_service] = lambda: mock_ranking_service
        
        try:
            # Testar
            response = client.get("/ranking/global")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["type"] == "global"
            assert data["period"] == "2024-01"
            assert len(data["entries"]) == 2
            assert data["entries"][0]["rank"] == 1
            assert data["entries"][1]["rank"] == 2
            
        finally:
            # Limpar override
            app.dependency_overrides.clear()

    def test_get_weekly_ranking(self, client, mock_ranking_service, sample_ranking):
        """Testa busca de ranking semanal"""
        # Modificar ranking para semanal
        sample_ranking.type = RankingType.WEEKLY
        sample_ranking.period = "2024-W01"
        
        mock_ranking_service.generate_weekly_ranking.return_value = sample_ranking
        
        # Substituir dependência
        app.dependency_overrides[get_ranking_service] = lambda: mock_ranking_service
        
        try:
            # Testar
            response = client.get("/ranking/weekly")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["type"] == "weekly"
            assert data["period"] == "2024-W01"
            
        finally:
            # Limpar override
            app.dependency_overrides.clear()

    def test_get_monthly_ranking(self, client, mock_ranking_service, sample_ranking):
        """Testa busca de ranking mensal"""
        # Modificar ranking para mensal
        sample_ranking.type = RankingType.MONTHLY
        sample_ranking.period = "2024-01"
        
        mock_ranking_service.generate_global_ranking.return_value = sample_ranking
        
        # Substituir dependência
        app.dependency_overrides[get_ranking_service] = lambda: mock_ranking_service
        
        try:
            # Testar - endpoint /monthly não existe na API
            response = client.get("/ranking/monthly")
            
            # Deve retornar 404 pois o endpoint não existe
            assert response.status_code == 404
            
        finally:
            # Limpar override
            app.dependency_overrides.clear()

    def test_get_ranking_by_period(self, client, mock_ranking_service, sample_ranking):
        """Testa busca de ranking por período - endpoint não existe"""
        # Substituir dependência
        app.dependency_overrides[get_ranking_service] = lambda: mock_ranking_service
        
        try:
            # Testar - endpoint /ranking/global/2024-01 não existe na API
            response = client.get("/ranking/global/2024-01")
            
            # Deve retornar 404 pois o endpoint não existe
            assert response.status_code == 404
            
        finally:
            # Limpar override
            app.dependency_overrides.clear()

    def test_get_ranking_not_found(self, client, mock_ranking_service):
        """Testa busca de ranking inexistente"""
        from fastapi import HTTPException
        mock_ranking_service.generate_global_ranking.side_effect = HTTPException(status_code=404, detail="Ranking not found")
        
        # Substituir dependência
        app.dependency_overrides[get_ranking_service] = lambda: mock_ranking_service
        
        try:
            # Testar
            response = client.get("/ranking/global")
            
            assert response.status_code == 404
            data = response.json()
            assert "not found" in data["detail"].lower()
            
        finally:
            # Limpar override
            app.dependency_overrides.clear()

    def test_generate_ranking(self, client, mock_ranking_service):
        """Testa geração de ranking - endpoint não existe"""
        # Substituir dependência
        app.dependency_overrides[get_ranking_service] = lambda: mock_ranking_service
        
        try:
            # Testar - endpoint /ranking/generate/global não existe na API
            response = client.post("/ranking/generate/global")
            
            # Deve retornar 404 pois o endpoint não existe
            assert response.status_code == 404
            
        finally:
            # Limpar override
            app.dependency_overrides.clear()

    def test_generate_ranking_error(self, client, mock_ranking_service):
        """Testa erro na geração de ranking - endpoint não existe"""
        # Substituir dependência
        app.dependency_overrides[get_ranking_service] = lambda: mock_ranking_service
        
        try:
            # Testar - endpoint /ranking/generate/global não existe na API
            response = client.post("/ranking/generate/global")
            
            # Deve retornar 404 pois o endpoint não existe
            assert response.status_code == 404
            
        finally:
            # Limpar override
            app.dependency_overrides.clear()

    def test_invalid_ranking_type(self, client):
        """Testa tipo de ranking inválido - endpoint não existe"""
        # Testar - endpoint /ranking/invalid não existe na API
        response = client.get("/ranking/invalid")
        
        # Deve retornar 404 pois o endpoint não existe
        assert response.status_code == 404

    def test_ranking_entry_structure(self, client, mock_ranking_service, sample_ranking):
        """Testa estrutura das entradas de ranking"""
        mock_ranking_service.generate_global_ranking.return_value = sample_ranking
        
        # Substituir dependência
        app.dependency_overrides[get_ranking_service] = lambda: mock_ranking_service
        
        try:
            # Testar
            response = client.get("/ranking/global")
            
            assert response.status_code == 200
            data = response.json()
            
            # Verificar estrutura da primeira entrada
            entry = data["entries"][0]
            required_fields = ["user_id", "name", "email", "points", "level", "xp", "rank", "last_activity"]
            
            for field in required_fields:
                assert field in entry
            
            # Verificar tipos de dados
            assert isinstance(entry["user_id"], str)
            assert isinstance(entry["name"], str)
            assert isinstance(entry["email"], str)
            assert isinstance(entry["points"], int)
            assert isinstance(entry["level"], int)
            assert isinstance(entry["xp"], int)
            assert isinstance(entry["rank"], int)
            
        finally:
            # Limpar override
            app.dependency_overrides.clear()

    def test_ranking_metadata(self, client, mock_ranking_service, sample_ranking):
        """Testa metadados do ranking"""
        mock_ranking_service.generate_global_ranking.return_value = sample_ranking
        
        # Substituir dependência
        app.dependency_overrides[get_ranking_service] = lambda: mock_ranking_service
        
        try:
            # Testar
            response = client.get("/ranking/global")
            
            assert response.status_code == 200
            data = response.json()
            
            # Verificar metadados
            assert "type" in data
            assert "period" in data
            assert "generated_at" in data
            assert "total_users" in data
            
            assert data["total_users"] == 2
            
        finally:
            # Limpar override
            app.dependency_overrides.clear()


