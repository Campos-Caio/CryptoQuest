"""
Fixtures compartilhadas para testes.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from app.core.firebase import get_firestore_db_async

<<<<<<< HEAD
@pytest.fixture
def firestore_db():
 """Mock do Firestore para testes"""
 mock_db = MagicMock()
 
 # Configurar mock para collection
 mock_collection = MagicMock()
 mock_db.collection.return_value = mock_collection
 
 # Configurar mock para document
 mock_doc = MagicMock()
 mock_doc_ref = AsyncMock()
 mock_doc_ref.get.return_value = mock_doc
 mock_doc_ref.set.return_value = None
 mock_doc_ref.update.return_value = None
 mock_doc_ref.delete.return_value = None
 mock_collection.document.return_value = mock_doc_ref
 
 # Configurar mock para query
 mock_query = MagicMock()
 mock_query.where.return_value = mock_query
 mock_query.limit.return_value = mock_query
 mock_query.stream.return_value = AsyncMock()
 mock_collection.where.return_value = mock_query
 
 return mock_db

@pytest.fixture
def mocker():
 """Mock do pytest-mock para compatibilidade"""
 from unittest.mock import MagicMock
 return MagicMock()

@pytest.fixture
def event_loop():
 """Event loop para testes assíncronos"""
 loop = asyncio.new_event_loop()
 yield loop
 loop.close()

@pytest.fixture
def mock_user_profile():
 """Mock de perfil de usuário para testes"""
 from app.models.user import UserProfile
 from datetime import datetime, timezone
 
 return UserProfile(
 uid="test_uid_",
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
 from app.models.user import UserProfile
 from datetime import datetime, timezone
 
 return UserProfile(
 uid="test_uid_",
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
 from app.models.user import UserProfile
 from datetime import datetime, timezone
 
 return UserProfile(
 uid="test_uid_",
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
 from app.models.user import FirebaseUser
 
 return FirebaseUser(
 uid="test_uid_",
 email="test@example.com",
 name="Test User"
 )
=======

@pytest.fixture
def firestore_db():
    """Mock do Firestore para testes"""
    mock_db = MagicMock()
    
    # Configurar mock para collection
    mock_collection = MagicMock()
    mock_db.collection.return_value = mock_collection
    
    # Configurar mock para document
    mock_doc = MagicMock()
    mock_doc_ref = AsyncMock()
    mock_doc_ref.get.return_value = mock_doc
    mock_doc_ref.set.return_value = None
    mock_doc_ref.update.return_value = None
    mock_doc_ref.delete.return_value = None
    mock_collection.document.return_value = mock_doc_ref
    
    # Configurar mock para query
    mock_query = MagicMock()
    mock_query.where.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.stream.return_value = AsyncMock()
    mock_collection.where.return_value = mock_query
    
    return mock_db


@pytest.fixture
def mocker():
    """Mock do pytest-mock para compatibilidade"""
    from unittest.mock import MagicMock
    return MagicMock()


@pytest.fixture
def event_loop():
    """Event loop para testes assíncronos"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_user_profile():
    """Mock de perfil de usuário para testes"""
    from app.models.user import UserProfile
    from datetime import datetime, timezone
    
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
    from app.models.user import UserProfile
    from datetime import datetime, timezone
    
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
    from app.models.user import UserProfile
    from datetime import datetime, timezone
    
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
    from app.models.user import FirebaseUser
    
    return FirebaseUser(
        uid="test_uid_123",
        email="test@example.com",
        name="Test User"
    )

>>>>>>> ceffef1 (feat: Implementacao final do sistema de recompensas)

@pytest.fixture
def override_get_current_user():
    """Override para get_current_user em testes"""
    from app.models.user import FirebaseUser
    
    async def _override():
        return FirebaseUser(
<<<<<<< HEAD
            uid="test_uid_",
=======
            uid="test_uid_123",
>>>>>>> ceffef1 (feat: Implementacao final do sistema de recompensas)
            email="test@example.com",
            name="Test User"
        )
    return _override

<<<<<<< HEAD
=======

>>>>>>> ceffef1 (feat: Implementacao final do sistema de recompensas)
@pytest.fixture
def override_get_current_user_new():
    """Override para get_current_user novo em testes"""
    from app.models.user import FirebaseUser
    
    async def _override():
        return FirebaseUser(
<<<<<<< HEAD
            uid="test_uid_",
=======
            uid="test_uid_456",
>>>>>>> ceffef1 (feat: Implementacao final do sistema de recompensas)
            email="new@example.com",
            name="New User"
        )
    return _override