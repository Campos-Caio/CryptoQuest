import pytest
from backend.app.models.user import UserRegister
from backend.app.services.auth_service import AuthService


@pytest.mark.asyncio
async def test_auth_service_register_user(monkeypatch):
    async def mock_create_user(email, password):
        return type("FirebaseUser", (), {"uid": "123", "email": email, "display_name": "Mock"})()

    async def mock_set_user_profile(user_profile):
        return True

    monkeypatch.setattr("backend.app.core.firebase.auth.create_user", mock_create_user)
    monkeypatch.setattr("backend.app.repositories.user_repository.UserRepository.set_user_profile", mock_set_user_profile)

    auth_service = AuthService()
    user_data = UserRegister(name="Teste", email="mock@test.com", password="senha123")

    firebase_user, user_profile = await auth_service.register_user(user_data)
    assert firebase_user.uid == "123"
    assert user_profile.email == "mock@test.com"
