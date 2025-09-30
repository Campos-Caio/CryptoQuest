"""
Testes de API para endpoints de ranking.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock
from fastapi.testclient import TestClient
from datetime import datetime, timezone

from app.main import app
from app.models.ranking import Ranking, RankingEntry, RankingType


class TestRankingAPI:
    """Testes para endpoints de ranking"""
    
    @pytest.fixture
    def client(self):
        """Cliente de teste FastAPI"""
        return TestClient(app)
    
    @pytest.fixture
    def mock_ranking_service(self):
        """Mock do RankingService"""
        return MagicMock()
    
    @pytest.fixture
    def sample_ranking(self):
        """Ranking de exemplo para testes"""
        return Ranking(
            type=RankingType.GLOBAL,
            period="2024-01",
            entries=[
                RankingEntry(
                    user_id="user1",
                    username="User1",
                    points=1000,
                    level=5,
                    xp=2500,
                    position=1
                ),
                RankingEntry(
                    user_id="user2",
                    username="User2",
                    points=800,
                    level=4,
                    xp=2000,
                    position=2
                )
            ],
            generated_at=datetime.now(timezone.utc)
        )

    def test_get_global_ranking(self, client, mock_ranking_service, sample_ranking):
        """Testa busca de ranking global"""
        # Mock do serviço
        mock_ranking_service.get_latest_ranking.return_value = sample_ranking
        
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
            assert data["entries"][0]["position"] == 1
            assert data["entries"][1]["position"] == 2
            
        finally:
            # Limpar override
            app.dependency_overrides.clear()

    def test_get_weekly_ranking(self, client, mock_ranking_service, sample_ranking):
        """Testa busca de ranking semanal"""
        # Modificar ranking para semanal
        sample_ranking.type = RankingType.WEEKLY
        sample_ranking.period = "2024-W01"
        
        mock_ranking_service.get_latest_ranking.return_value = sample_ranking
        
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
        
        mock_ranking_service.get_latest_ranking.return_value = sample_ranking
        
        # Substituir dependência
        app.dependency_overrides[get_ranking_service] = lambda: mock_ranking_service
        
        try:
            # Testar
            response = client.get("/ranking/monthly")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["type"] == "monthly"
            assert data["period"] == "2024-01"
            
        finally:
            # Limpar override
            app.dependency_overrides.clear()

    def test_get_ranking_by_period(self, client, mock_ranking_service, sample_ranking):
        """Testa busca de ranking por período específico"""
        mock_ranking_service.get_ranking_by_period.return_value = sample_ranking
        
        # Substituir dependência
        app.dependency_overrides[get_ranking_service] = lambda: mock_ranking_service
        
        try:
            # Testar
            response = client.get("/ranking/global/2024-01")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["type"] == "global"
            assert data["period"] == "2024-01"
            
        finally:
            # Limpar override
            app.dependency_overrides.clear()

    def test_get_ranking_not_found(self, client, mock_ranking_service):
        """Testa busca de ranking inexistente"""
        mock_ranking_service.get_latest_ranking.return_value = None
        
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
        """Testa geração de ranking"""
        mock_ranking_service.generate_global_ranking.return_value = True
        
        # Substituir dependência
        app.dependency_overrides[get_ranking_service] = lambda: mock_ranking_service
        
        try:
            # Testar
            response = client.post("/ranking/generate/global")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "generated" in data["message"].lower()
            
        finally:
            # Limpar override
            app.dependency_overrides.clear()

    def test_generate_ranking_error(self, client, mock_ranking_service):
        """Testa erro na geração de ranking"""
        mock_ranking_service.generate_global_ranking.return_value = False
        
        # Substituir dependência
        app.dependency_overrides[get_ranking_service] = lambda: mock_ranking_service
        
        try:
            # Testar
            response = client.post("/ranking/generate/global")
            
            assert response.status_code == 500
            data = response.json()
            assert "error" in data["detail"].lower()
            
        finally:
            # Limpar override
            app.dependency_overrides.clear()

    def test_invalid_ranking_type(self, client):
        """Testa tipo de ranking inválido"""
        # Testar
        response = client.get("/ranking/invalid")
        
        assert response.status_code == 422  # Validation error

    def test_ranking_entry_structure(self, client, mock_ranking_service, sample_ranking):
        """Testa estrutura das entradas de ranking"""
        mock_ranking_service.get_latest_ranking.return_value = sample_ranking
        
        # Substituir dependência
        app.dependency_overrides[get_ranking_service] = lambda: mock_ranking_service
        
        try:
            # Testar
            response = client.get("/ranking/global")
            
            assert response.status_code == 200
            data = response.json()
            
            # Verificar estrutura da primeira entrada
            entry = data["entries"][0]
            required_fields = ["user_id", "username", "points", "level", "xp", "position"]
            
            for field in required_fields:
                assert field in entry
            
            # Verificar tipos de dados
            assert isinstance(entry["user_id"], str)
            assert isinstance(entry["username"], str)
            assert isinstance(entry["points"], int)
            assert isinstance(entry["level"], int)
            assert isinstance(entry["xp"], int)
            assert isinstance(entry["position"], int)
            
        finally:
            # Limpar override
            app.dependency_overrides.clear()

    def test_ranking_metadata(self, client, mock_ranking_service, sample_ranking):
        """Testa metadados do ranking"""
        mock_ranking_service.get_latest_ranking.return_value = sample_ranking
        
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
            assert "total_entries" in data
            
            assert data["total_entries"] == 2
            
        finally:
            # Limpar override
            app.dependency_overrides.clear()


# Função auxiliar para importar dependência
def get_ranking_service():
    """Função auxiliar para importar dependência"""
    pass
