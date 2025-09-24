from fastapi import HTTPException, status
import pytest
from httpx import AsyncClient, ASGITransport
from datetime import datetime

from app.main import app
from app.dependencies.auth import get_current_user
from app.models.user import FirebaseUser, UserProfile
from app.repositories.user_repository import get_user_repository

# Simula o perfil do usuario ANTES da atualizacao 

mock_initial_user_profile = UserProfile(
    uid="test_uid_123",
    name = 'Test User Original', 
    email = "test@exemple.com", 
    register_date= datetime.now(), 
    level=1,
    has_completed_questionnaire=True,
)

# Simula como o perfil deve ficar DEPOIS da atualizacao 
mock_updated_user_profile = UserProfile(
    uid="test_uid_123",
    name = 'Novo nome', 
    email = "test@exemple.com", 
    register_date= mock_initial_user_profile.register_date, 
    level=1,
    has_completed_questionnaire=True,
)

async def override_get_current_user():
    return FirebaseUser(uid="test_uid_123",
    email = "test@exemple.com",
    name = 'Test User Original'
)

# -- Tests -- 

pytestmark = pytest.mark.asyncio 

async def test_update_user_profile_sucess(mocker, mock_updated_user_profile): 
    """
        Teste se o usuario autenticado consegue atualizar seu perfil com sucesso

        Returns: 
            (200 OK)
    """

    class MockUserRepository:
        async def update_user_Profile(self, uid: str, new_data:dict):
            assert uid == 'test_uid_123'
            assert new_data.get("name") == 'Novo Nome'
            pass

        async def get_user_profile(self,uid:str):
            return mock_updated_user_profile

    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_user_repository] = lambda: MockUserRepository()

    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client: 
        response = await client.put(
            "/users/me",
            headers={"Authorization": "Bearer fake-token"},
            json={"name": "Novo Nome", "bio": "Nova bio do usuário"}
        )
    
    assert response.status_code == 200 
    response_data = response.json() 
    assert response_data['name'] == 'Novo nome'
    
    app.dependency_overrides = {}

async def test_update_profile_unauthorized(): 
    """
        Testa se um usuario nao autenticado recebe um erro 401 ao tentar utilizar o perfil. 
    """    

    async def override_get_current_user_unauthorized(): 
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")

    app.dependency_overrides[get_current_user] = override_get_current_user_unauthorized

    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client: 
        response = await client.put(
            "/users/me",
            headers={"Authorization": "Bearer invalid-token"},
            json={"name": "Qualquer Nome"}
        )
    
    assert response.status_code == 401 
    app.dependency_overrides = {}