import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.dependencies.auth import get_current_user
from app.models.user import FirebaseUser, UserProfile
from app.repositories.user_repository import get_user_repository
from datetime import datetime

# --- Mocks e Dados de Teste ---
mock_user_profile_new = UserProfile(
    uid="new_user_uid", name="New User", email="new@test.com",
    register_date=datetime.now(), level=1, has_completed_questionnaire=False
)
mock_user_profile_existing = UserProfile(
    uid="existing_user_uid", name="Existing User", email="existing@test.com",
    register_date=datetime.now(), level=1, has_completed_questionnaire=True
)

async def override_get_current_user_new():
    return FirebaseUser(uid="new_user_uid", name="New User", email="new@test.com")

async def override_get_current_user_existing():
    return FirebaseUser(uid="existing_user_uid", name="Existing User", email="existing@test.com")

pytestmark = pytest.mark.asyncio

async def test_submit_questionnaire_success_for_new_user(mocker, mock_user_profile_new):
    # Arrange
    class MockUserRepository:
        def get_user_profile(self, uid: str):
            return mock_user_profile_new
        def update_user_Profile(self, uid: str, new_data: dict):
            pass

    app.dependency_overrides[get_current_user] = override_get_current_user_new
    app.dependency_overrides[get_user_repository] = lambda: MockUserRepository()
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Act
        response = await client.post(
            "/questionnaire/initial/submit",
            headers={"Authorization": "Bearer fake-token"},
            json={"answers": [{"question_id": "q", "selected_option_id": "qa"}]}
        )

        # Assert
        assert response.status_code == 201
        assert response.json()["profile_name"] == "Explorador Curioso"
    app.dependency_overrides = {}

async def test_submit_questionnaire_fails_if_already_completed():
    # Arrange
    class MockUserRepository:
        def get_user_profile(self, uid: str):
            return mock_user_profile_existing

    app.dependency_overrides[get_current_user] = override_get_current_user_existing
    app.dependency_overrides[get_user_repository] = lambda: MockUserRepository()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Act
        response = await client.post(
            "/questionnaire/initial/submit",
            headers={"Authorization": "Bearer fake-token"},
            json={"answers": []}
        )

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "O usuario ja respondeu o questionario inicial!"
    app.dependency_overrides = {}