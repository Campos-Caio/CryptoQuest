"""
Testes unitários para RankingRepository.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock
from datetime import datetime, timezone

from app.repositories.ranking_repository import RankingRepository
from app.models.ranking import Ranking, RankingEntry, RankingType


class TestRankingRepository:
    """Testes para o RankingRepository"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock do banco de dados"""
        mock_db = MagicMock()
        
        # Configurar mock para collection
        mock_collection = MagicMock()
        mock_db.collection.return_value = mock_collection
        
        return mock_db
    
    @pytest.fixture
    def ranking_repo(self, mock_db):
        """Instância do RankingRepository com mock"""
        return RankingRepository(mock_db)

    def test_save_ranking(self, ranking_repo, mock_db):
        """Testa salvamento de ranking"""
        # Mock de documento
        mock_doc_ref = MagicMock()
        mock_collection = mock_db.collection.return_value
        mock_collection.document.return_value = mock_doc_ref
        
        # Criar ranking de teste
        ranking = Ranking(
            type=RankingType.GLOBAL,
            period="2024-01",
            entries=[
                RankingEntry(
                    user_id="user1",
                    name="User1",
                    email="user1@test.com",
                    points=1000,
                    level=5,
                    xp=2500,
                    rank=1,
                    last_activity=datetime.now(timezone.utc)
                )
            ],
            total_users=1,
            generated_at=datetime.now(timezone.utc)
        )
        
        # Testar
        result = ranking_repo.save_ranking(ranking)
        
        # O método save_ranking não retorna nada (None)
        assert result is None
        mock_doc_ref.set.assert_called_once()

    def test_get_latest_ranking(self, ranking_repo, mock_db):
        """Testa busca do ranking mais recente"""
        # Mock de documento
        mock_doc = MagicMock()
        mock_doc.to_dict.return_value = {
            'type': 'global',
            'period': '2024-01',
            'entries': [
                {
                    'user_id': 'user1',
                    'name': 'User1',
                    'email': 'user1@test.com',
                    'points': 1000,
                    'level': 5,
                    'xp': 2500,
                    'rank': 1,
                    'last_activity': datetime.now(timezone.utc).isoformat()
                }
            ],
            'total_users': 1,
            'generated_at': datetime.now(timezone.utc).isoformat()
        }
        
        # Configurar mock para query.stream()
        mock_collection = mock_db.collection.return_value
        mock_query = MagicMock()
        mock_order_by = MagicMock()
        mock_limit = MagicMock()
        mock_limit.stream.return_value = [mock_doc]
        mock_order_by.limit.return_value = mock_limit
        mock_query.order_by.return_value = mock_order_by
        mock_collection.where.return_value = mock_query
        
        # Testar
        ranking = ranking_repo.get_latest_ranking(RankingType.GLOBAL)
        
        assert ranking is not None
        assert ranking.type == RankingType.GLOBAL
        assert len(ranking.entries) == 1

    def test_get_ranking_by_period(self, ranking_repo, mock_db):
        """Testa busca de ranking por período"""
        # Mock de documento
        mock_doc = MagicMock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {
            'type': 'weekly',
            'period': '2024-W01',
            'entries': [
                {
                    'user_id': 'user1',
                    'name': 'User1',
                    'email': 'user1@test.com',
                    'points': 500,
                    'level': 3,
                    'xp': 1200,
                    'rank': 1,
                    'last_activity': datetime.now(timezone.utc).isoformat()
                }
            ],
            'total_users': 1,
            'generated_at': datetime.now(timezone.utc).isoformat()
        }
        
        # Configurar mock
        mock_collection = mock_db.collection.return_value
        mock_doc_ref = MagicMock()
        mock_doc_ref.get.return_value = mock_doc
        mock_collection.document.return_value = mock_doc_ref
        
        # Testar
        ranking = ranking_repo.get_ranking_by_period(RankingType.WEEKLY, "2024-W01")
        
        assert ranking is not None
        assert ranking.type == RankingType.WEEKLY
        assert ranking.period == "2024-W01"

    def test_get_ranking_not_found(self, ranking_repo, mock_db):
        """Testa busca de ranking inexistente"""
        # Mock de documento inexistente
        mock_doc = MagicMock()
        mock_doc.exists = False
        
        # Configurar mock
        mock_collection = mock_db.collection.return_value
        mock_doc_ref = MagicMock()
        mock_doc_ref.get.return_value = mock_doc
        mock_collection.document.return_value = mock_doc_ref
        
        # Testar
        ranking = ranking_repo.get_latest_ranking(RankingType.MONTHLY)
        
        assert ranking is None

    def test_ranking_entry_creation(self, ranking_repo):
        """Testa criação de entrada de ranking"""
        entry = RankingEntry(
            user_id="user123",
            name="TestUser",
            email="testuser@test.com",
            points=1500,
            level=7,
            xp=3500,
            rank=3,
            last_activity=datetime.now(timezone.utc)
        )
        
        assert entry.user_id == "user123"
        assert entry.name == "TestUser"
        assert entry.points == 1500
        assert entry.level == 7
        assert entry.xp == 3500
        assert entry.rank == 3

    def test_ranking_creation(self, ranking_repo):
        """Testa criação de ranking"""
        entries = [
            RankingEntry(
                user_id="user1",
                name="User1",
                email="user1@test.com",
                points=1000,
                level=5,
                xp=2500,
                rank=1,
                last_activity=datetime.now(timezone.utc)
            ),
            RankingEntry(
                user_id="user2",
                name="User2",
                email="user2@test.com",
                points=800,
                level=4,
                xp=2000,
                rank=2,
                last_activity=datetime.now(timezone.utc)
            )
        ]
        
        ranking = Ranking(
            type=RankingType.GLOBAL,
            period="2024-01",
            entries=entries,
            total_users=2,
            generated_at=datetime.now(timezone.utc)
        )
        
        assert ranking.type == RankingType.GLOBAL
        assert ranking.period == "2024-01"
        assert len(ranking.entries) == 2
        assert ranking.entries[0].rank == 1
        assert ranking.entries[1].rank == 2
