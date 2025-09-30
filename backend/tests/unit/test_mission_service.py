from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock
import pytest

from app.models.user import UserProfile
from app.services.mission_service import MissionService

pytestmark = pytest.mark.asyncio

# --- Dados de Teste (mantidos como estão) ---
mock_user = UserProfile(
    uid="test_user_1",
    name="Teste User",
    email="teste@test.com",
    register_date=datetime.now(),
    level=5,
    has_completed_questionnaire=True,
    points=500,
    completed_missions={
        "mission_easy_2": datetime.now(timezone.utc) - timedelta(days=1)
    },
)
mock_all_missions = [
    {"id": "mission_easy_1", "title": "Missão Fácil 1", "required_level": 1, "reward_points": 50},
    {"id": "mission_easy_2", "title": "Missão Fácil 2", "required_level": 2, "reward_points": 50},
    {"id": "mission_hard_1", "title": "Missão Difícil 1", "required_level": 10, "reward_points": 200},
]

# Helper que transforma a lista em um iterador assíncrono
async def async_iterator(data):
    for item in data:
        yield item

# --- Teste Corrigido ---
async def test_get_daily_missions_for_user():
    """
    Testa a lógica de seleção de missões diárias.
    """
    # Arrange (Preparação)

    # 1. Prepara os documentos falsos que nosso iterador irá fornecer
    mock_docs = [AsyncMock(to_dict=lambda m=m: m) for m in mock_all_missions]

    # 2. Cria um mock para o resultado do método .stream()
    #    Ele retorna nosso iterador assíncrono.
    mock_stream_result = async_iterator(mock_docs)

    # 3. Cria um mock para o objeto 'collection'
    #    O método .stream() deste objeto retornará o resultado que preparamos acima.
    from unittest.mock import MagicMock
    mock_collection = MagicMock()
    mock_collection.stream.return_value = mock_stream_result

    # 4. Cria um mock para o cliente do banco de dados (dbclient)
    #    O método .collection() dele retornará nosso mock_collection.
    mock_db_client = MagicMock()
    mock_db_client.collection.return_value = mock_collection

    # 5. Instancia o serviço, injetando nosso mock do dbclient
    service = MissionService(user_repo=None, dbclient=mock_db_client)

    # Act (Ação)
    daily_missions = await service.get_daily_missions_for_user(mock_user)

    # Assert (Verificação)
    # Apenas mission_easy_1 deve ser retornada pois:
    # - mission_easy_2 já foi completada
    # - mission_hard_1 requer nível 10 (usuário tem nível 5)
    assert len(daily_missions) == 1
    mission_ids = {m['id'] for m in daily_missions}
    assert "mission_hard_1" not in mission_ids
    assert "mission_easy_1" in mission_ids
    assert "mission_easy_2" not in mission_ids  # Já foi completada

