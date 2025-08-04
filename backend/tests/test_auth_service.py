import pytest
from datetime import datetime
from app.models.user import UserRegister, UserProfile
from app.services.auth_service import AuthService
from app.repositories.user_repository import UserRepository

# Marcador para indicar que os testes são assíncronos
pytestmark = pytest.mark.asyncio

async def test_auth_service_register_user(monkeypatch, mocker):
    """
    Testa o registro de um novo usuário no AuthService, simulando (mockando)
    as chamadas externas para o Firebase e para o nosso repositório.
    """
    # --- 1. ARRANGE (Preparação dos Mocks e Dados de Teste) ---

    # Mock 1: Simula a função `create_user` do Firebase Admin SDK
    def mock_firebase_create_user(email, password, display_name):
        # Retorna um objeto simples que se parece com o UserRecord do Firebase
        class MockUserRecord:
            def __init__(self, email_val, display_name_val):
                self.uid = "test_uid_123"
                self.email = email_val
                self.display_name = display_name_val
        return MockUserRecord(email_val=email, display_name_val=display_name)

    # Mock 2: Simula o método `create_user_profile` do nosso UserRepository
    async def mock_create_user_profile(self, uid, name, email):
        # Retorna um objeto UserProfile, assim como o método real faria
        return UserProfile(
            uid=uid,
            name=name,
            email=email,
            register_date=datetime.now(),
            level=1,
            has_completed_questionnaire=False
        )

    # Aplica os mocks usando monkeypatch
    # Substitui a função real do Firebase pela nossa simulação
    monkeypatch.setattr("firebase_admin.auth.create_user", mock_firebase_create_user)
    
    # Substitui o método real do UserRepository pela nossa simulação
    monkeypatch.setattr(
        "app.repositories.user_repository.UserRepository.create_user_profile",
        mock_create_user_profile
    )

    # Cria uma instância do UserRepository (pode ser 'None' pois seu método foi mockado)
    # e injeta no AuthService, como o construtor requer.
    mock_dbclient = mocker.MagicMock()
    mock_user_repo = UserRepository(mock_dbclient)
    auth_service = AuthService(user_repo=mock_user_repo)
    
    # Dados de entrada para o teste
    user_data = UserRegister(name="Test User", email="mock@test.com", password="password123")

    # --- 2. ACT (Ação) ---
    # Executa o método que queremos testar
    firebase_user, user_profile = await auth_service.register_user(user_data)

    # --- 3. ASSERT (Verificação) ---
    # Verifica se os resultados são os esperados
    assert firebase_user.uid == "test_uid_123"
    assert user_profile.name == "Test User"
    assert user_profile.email == "mock@test.com"
    assert user_profile.uid == "test_uid_123"