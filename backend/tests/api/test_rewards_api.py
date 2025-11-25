"""
Testes para a API de recompensas.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.repositories.badge_repository import get_badge_repository
from app.repositories.reward_repository import get_reward_repository
from app.services.reward_service import get_reward_service
from app.dependencies.auth import get_current_user
from app.models.user import FirebaseUser


class TestRewardsAPI:
    """Testes para endpoints de recompensas"""
    
    @pytest.fixture
    def mock_badge_repo(self):
        """Mock do BadgeRepository"""
        mock_repo = AsyncMock()
        mock_repo.get_user_badges.return_value = []
        mock_repo.get_all_badges.return_value = []
        mock_repo.get_user_badge_stats.return_value = {
            'total_badges': 0,
            'total_available': 10,
            'completion_percentage': 0.0,
            'rarity_counts': {}
        }
        mock_repo.get_badge_by_id.return_value = None
        return mock_repo
    
    @pytest.fixture
    def mock_reward_repo(self):
        """Mock do RewardRepository"""
        mock_repo = AsyncMock()
        mock_repo.get_user_rewards.return_value = []
        return mock_repo
    
    @pytest.fixture
    def mock_reward_service(self, mock_badge_repo, mock_reward_repo):
        """Mock do RewardService"""
        mock_service = AsyncMock()
        mock_service.award_mission_completion.return_value = {
            'points_earned': 100,
            'xp_earned': 50,
            'badges_earned': []
        }
        return mock_service
    
    @pytest.fixture
    def mock_current_user(self):
        """Mock do usuário atual"""
        return FirebaseUser(
            uid="test_user",
            email="test@example.com",
            name="Test User"
        )

    @pytest.mark.asyncio
    async def test_get_user_badges(self, mock_badge_repo, mock_current_user):
        """Testa endpoint GET /rewards/user/{user_id}/badges"""
        # Mock das dependências
        app.dependency_overrides[get_badge_repository] = lambda: mock_badge_repo
        app.dependency_overrides[get_current_user] = lambda: mock_current_user
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/rewards/user/test_user/badges")
        
        assert response.status_code == 200
        assert response.json() == []
        
        # Limpar override
        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_all_badges(self, mock_badge_repo, mock_current_user):
        """Testa endpoint GET /rewards/badges"""
        # Mock das dependências
        app.dependency_overrides[get_badge_repository] = lambda: mock_badge_repo
        app.dependency_overrides[get_current_user] = lambda: mock_current_user
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/rewards/badges")
        
        assert response.status_code == 200
        assert response.json() == []
        
        # Limpar override
        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_user_badge_stats(self, mock_badge_repo, mock_current_user):
        """Testa endpoint GET /rewards/user/{user_id}/badge-stats"""
        # Mock das dependências
        app.dependency_overrides[get_badge_repository] = lambda: mock_badge_repo
        app.dependency_overrides[get_current_user] = lambda: mock_current_user
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/rewards/user/test_user/badge-stats")
        
        assert response.status_code == 200
        data = response.json()
        assert 'total_badges' in data
        assert 'total_available' in data
        assert 'completion_percentage' in data
        
        # Limpar override
        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_badge_by_id(self, mock_badge_repo, mock_current_user):
        """Testa endpoint GET /rewards/badges/{badge_id}"""
        # Mock das dependências
        app.dependency_overrides[get_badge_repository] = lambda: mock_badge_repo
        app.dependency_overrides[get_current_user] = lambda: mock_current_user
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/rewards/badges/test_badge")
        
        assert response.status_code == 404  # Badge não encontrado
        assert response.json()["detail"] == "Badge não encontrado"
        
        # Limpar override
        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_award_mission_completion(self, mock_reward_service, mock_current_user):
        """Testa endpoint POST /rewards/award/mission"""
        # Mock das dependências
        app.dependency_overrides[get_reward_service] = lambda: mock_reward_service
        app.dependency_overrides[get_current_user] = lambda: mock_current_user
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/rewards/award/mission?user_id=test_user&mission_id=test_mission&score=85.0&mission_type=daily")
        
        assert response.status_code == 200
        data = response.json()
        assert 'points_earned' in data
        assert 'xp_earned' in data
        assert 'badges_earned' in data
        
        # Limpar override
        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_user_rewards(self, mock_reward_repo, mock_current_user):
        """Testa endpoint GET /rewards/user/{user_id}/rewards"""
        # Mock das dependências
        app.dependency_overrides[get_reward_repository] = lambda: mock_reward_repo
        app.dependency_overrides[get_current_user] = lambda: mock_current_user
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/rewards/user/test_user/history")
        
        assert response.status_code == 200
        assert response.json() == []
        
        # Limpar override
        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_invalid_user_id(self, mock_current_user):
        """Testa comportamento com user_id inválido"""
        app.dependency_overrides[get_current_user] = lambda: mock_current_user
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/rewards/user//badges")
        
        assert response.status_code == 404
        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_invalid_badge_id(self, mock_badge_repo, mock_current_user):
        """Testa comportamento com badge_id inválido"""
        # Mock das dependências
        app.dependency_overrides[get_badge_repository] = lambda: mock_badge_repo
        app.dependency_overrides[get_current_user] = lambda: mock_current_user
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/rewards/badges/")
        
        assert response.status_code == 307  # Redirect (trailing slash)
        
        # Limpar override
        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_award_mission_completion_invalid_payload(self, mock_current_user):
        """Testa award mission completion com payload inválido"""
        from unittest.mock import MagicMock
        from app.repositories.badge_repository import BadgeRepository
        from app.services.reward_service import RewardService
        
        # Mock dos repositórios para evitar problemas de coroutine
        mock_badge_repo = MagicMock()
        mock_reward_repo = MagicMock()
        mock_reward_service = MagicMock()
        
        app.dependency_overrides[get_current_user] = lambda: mock_current_user
        app.dependency_overrides[get_badge_repository] = lambda: mock_badge_repo
        app.dependency_overrides[get_reward_repository] = lambda: mock_reward_repo
        app.dependency_overrides[get_reward_service] = lambda: mock_reward_service
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/rewards/award/mission?user_id=test_user&mission_id=test_mission&score=invalid&mission_type=daily")
        
        assert response.status_code == 422  # Validation error
        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_award_mission_completion_service_error(self, mock_reward_service, mock_current_user):
        """Testa comportamento quando serviço retorna erro"""
        # Mock para retornar erro
        mock_reward_service.award_mission_completion.side_effect = Exception("Service error")
        
        # Mock das dependências
        app.dependency_overrides[get_reward_service] = lambda: mock_reward_service
        app.dependency_overrides[get_current_user] = lambda: mock_current_user
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/rewards/award/mission?user_id=test_user&mission_id=test_mission&score=85.0&mission_type=daily")
        
        assert response.status_code == 500
        
        # Limpar override
        app.dependency_overrides.clear()
