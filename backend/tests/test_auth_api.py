from fastapi.testclient import TestClient
from app.main import app
import pytest


def test_register_user_api(monkeypatch):
    class MockFirebaseUser:
        def __init__(self, uid, email, name):
            self.uid = uid
            self.email = email
            self.name = name

    async def mock_register_user(self, user_data):
        mock_firebase_user = MockFirebaseUser(
            uid="mockuid", email=user_data.email, name=user_data.name
        )
        mock_user_profile = {
            "uid": "mockuid",
            "name": user_data.name,
            "email": user_data.email,
            "register_date": "2024-01-01T00:00:00",
            "level": 1,
        }
        return mock_firebase_user, mock_user_profile

    from app.services import auth_service
    monkeypatch.setattr(auth_service.AuthService, "register_user", mock_register_user)

    client = TestClient(app)
    response = client.post("/auth/register", json={
        "name": "Teste API",
        "email": "api@test.com",
        "password": "12345678"
    })

    print("STATUS:", response.status_code)
    print("BODY:", response.text)

    assert response.status_code == 201
