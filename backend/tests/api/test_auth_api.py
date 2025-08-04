import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.services.auth_service import AuthService
from app.dependencies.auth import get_current_user
from app.models.user import FirebaseUser, UserProfile
from datetime import datetime
from app.services.auth_service import get_auth_service

# UserProfile falso que sera usado nos Mocks

mock_user_profile = UserProfile(
    uid="test_uid_123",
    name="Test User",
    email="test@example.com",
    register_date=datetime.now(),
    level=1,
    has_completed_questionnaire=False,
)


# Mock para dependencia get_current_user
async def override_get_current_user():
    return FirebaseUser(uid="test_uid_123", name="Test User", email="test@exemple.com")


# -- Testes --
async def test_register_user_sucess(mocker):
    """
    Testa o endpoint de registro de usuario com sucesso (201 Created)
    Passado o usuario de teste
    """
    class MockAuthService:
        async def register_user(self, user_data):
            return (
                FirebaseUser(uid='test_uid_123', email='test@example.com', name='Test User'), 
                mock_user_profile
            )

    app.dependency_overrides[get_auth_service] = lambda:  MockAuthService()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Act: Fazemos a chamada de API
        response = await client.post(
            "/auth/register",
            json={
                "name": "Test User",
                "email": "test@example.com",
                "password": "password123",
            },
        )

    assert response.status_code == 201
    data = response.json()
    assert data["message"] == "Usuario registrado com sucesso!"
    assert data["uid"] == "test_uid_123"
    assert data["user_profile"]["name"] == "Test User"

    app.dependency_overrides = {}


async def test_get_me_sucess(mocker):
    """
    Testa o endpoint /me com um usuario autenticado
    """

    mock_get_profile = mocker.AsyncMock(return_value=mock_user_profile)
    app.dependency_overrides[get_current_user] = override_get_current_user

    from app.repositories.user_repository import get_user_repository

    class MockUserRepository:
        async def get_user_profile(self, uid: str):
            return mock_user_profile

    app.dependency_overrides[get_user_repository] = lambda: MockUserRepository()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(
            "/auth/me", headers={"Authorization": "Bearer fake-token"}
        )

    assert response.status_code == 200
    data = response.json()
    assert data["uid"] == "test_uid_123"
    assert data["name"] == "Test User"

    app.dependency_overrides = {}
