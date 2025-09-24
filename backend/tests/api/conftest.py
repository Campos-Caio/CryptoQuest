"""
Fixtures específicas para testes de API.
"""

import pytest
from app.models.user import UserProfile, FirebaseUser
from datetime import datetime, timezone


@pytest.fixture
def mock_user_profile():
    """Mock de perfil de usuário para testes"""
    return UserProfile(
        uid="test_uid_123",
        name="Test User",
        email="test@example.com",
        register_date=datetime.now(timezone.utc),
        level=1,
        points=0,
        xp=0,
        has_completed_questionnaire=False
    )


@pytest.fixture
def mock_user_profile_new():
    """Mock de perfil de usuário novo para testes"""
    return UserProfile(
        uid="test_uid_456",
        name="New User",
        email="new@example.com",
        register_date=datetime.now(timezone.utc),
        level=1,
        points=0,
        xp=0,
        has_completed_questionnaire=False
    )


@pytest.fixture
def mock_updated_user_profile():
    """Mock de perfil de usuário atualizado para testes"""
    return UserProfile(
        uid="test_uid_123",
        name="Novo nome",
        email="test@example.com",
        register_date=datetime.now(timezone.utc),
        level=1,
        points=0,
        xp=0,
        has_completed_questionnaire=True
    )


@pytest.fixture
def mock_firebase_user():
    """Mock de usuário Firebase para testes"""
    return FirebaseUser(
        uid="test_uid_123",
        email="test@example.com",
        name="Test User"
    )
