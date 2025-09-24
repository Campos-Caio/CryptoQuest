"""
Testes unitários para BadgeRepository.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.repositories.badge_repository import BadgeRepository
from app.models.reward import UserBadge, Badge


class TestBadgeRepository:
    """Testes para o BadgeRepository"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock do banco de dados"""
        mock_db = MagicMock()
        
        # Configurar mock para collection
        mock_collection = MagicMock()
        mock_db.collection.return_value = mock_collection
        
        return mock_db
    
    @pytest.fixture
    def badge_repo(self, mock_db):
        """Instância do BadgeRepository com mock"""
        return BadgeRepository(mock_db)

    @pytest.mark.asyncio
    async def test_has_badge_true(self, badge_repo, mock_db):
        """Testa verificação de badge existente"""
        # Mock do Firestore - configurar corretamente para async
        mock_doc = MagicMock()
        
        # Criar um async generator que retorna um documento
        async def mock_stream():
            yield mock_doc
        
        # Configurar a cadeia de mocks
        mock_collection = mock_db.collection.return_value
        mock_collection.where.return_value.where.return_value.limit.return_value.stream.return_value = mock_stream()
        
        # Testar
        result = await badge_repo.has_badge("user1", "badge1")
        
        assert result is True
        mock_db.collection.assert_called_with("user_badges")

    @pytest.mark.asyncio
    async def test_has_badge_false(self, badge_repo, mock_db):
        """Testa verificação de badge inexistente"""
        # Mock do Firestore - sem documentos
        async def mock_empty_stream():
            return
            yield  # Generator vazio
        
        # Configurar a cadeia de mocks
        mock_collection = mock_db.collection.return_value
        mock_collection.where.return_value.where.return_value.limit.return_value.stream.return_value = mock_empty_stream()
        
        # Testar
        result = await badge_repo.has_badge("user1", "badge1")
        
        assert result is False

    @pytest.mark.asyncio
    async def test_award_badge_success(self, badge_repo, mock_db):
        """Testa concessão de badge com sucesso"""
        # Mock - usuário não tem o badge (has_badge retorna False)
        async def mock_empty_stream():
            return
            yield  # Generator vazio
        
        # Configurar a cadeia de mocks para has_badge
        mock_collection = mock_db.collection.return_value
        mock_collection.where.return_value.where.return_value.limit.return_value.stream.return_value = mock_empty_stream()
        
        # Mock para salvar badge
        mock_doc_ref = AsyncMock()
        mock_collection.document.return_value = mock_doc_ref
        
        # Testar
        result = await badge_repo.award_badge("user1", "badge1", {"test": "context"})
        
        assert result is True
        mock_doc_ref.set.assert_called_once()

    @pytest.mark.asyncio
    async def test_award_badge_duplicate(self, badge_repo, mock_db):
        """Testa tentativa de conceder badge duplicado"""
        # Mock - usuário já tem o badge (has_badge retorna True)
        mock_doc = MagicMock()
        
        async def mock_stream_with_doc():
            yield mock_doc
        
        # Configurar a cadeia de mocks
        mock_collection = mock_db.collection.return_value
        mock_collection.where.return_value.where.return_value.limit.return_value.stream.return_value = mock_stream_with_doc()
        
        # Testar
        result = await badge_repo.award_badge("user1", "badge1", {"test": "context"})
        
        assert result is False  # Não deve conceder badge duplicado

    @pytest.mark.asyncio
    async def test_get_user_badges(self, badge_repo, mock_db):
        """Testa busca de badges do usuário"""
        # Mock de documentos
        mock_doc1 = MagicMock()
        mock_doc1.to_dict.return_value = {
            'user_id': 'user1',
            'badge_id': 'badge1',
            'earned_at': '2023-01-01T00:00:00Z',
            'context': {'test': 'context1'}
        }
        
        mock_doc2 = MagicMock()
        mock_doc2.to_dict.return_value = {
            'user_id': 'user1',
            'badge_id': 'badge2',
            'earned_at': '2023-01-02T00:00:00Z',
            'context': {'test': 'context2'}
        }
        
        async def mock_stream():
            yield mock_doc1
            yield mock_doc2
        
        # Configurar mock
        mock_collection = mock_db.collection.return_value
        mock_collection.where.return_value.stream.return_value = mock_stream()
        
        # Testar
        badges = await badge_repo.get_user_badges("user1")
        
        assert len(badges) == 2
        assert badges[0].badge_id == "badge1"
        assert badges[1].badge_id == "badge2"

    @pytest.mark.asyncio
    async def test_get_all_badges(self, badge_repo, mock_db):
        """Testa busca de todos os badges disponíveis"""
        # Mock de documentos
        mock_doc1 = MagicMock()
        mock_doc1.to_dict.return_value = {
            'id': 'badge1',
            'name': 'Badge 1',
            'description': 'Descrição 1',
            'icon': '🏆',
            'rarity': 'common',
            'color': '#FFD700',
            'requirements': {}
        }
        
        mock_doc2 = MagicMock()
        mock_doc2.to_dict.return_value = {
            'id': 'badge2',
            'name': 'Badge 2',
            'description': 'Descrição 2',
            'icon': '⭐',
            'rarity': 'rare',
            'color': '#FF6B6B',
            'requirements': {}
        }
        
        async def mock_stream():
            yield mock_doc1
            yield mock_doc2
        
        # Configurar mock
        mock_collection = mock_db.collection.return_value
        mock_collection.stream.return_value = mock_stream()
        
        # Testar
        badges = await badge_repo.get_all_badges()
        
        assert len(badges) == 2
        assert badges[0].id == "badge1"
        assert badges[1].id == "badge2"

    @pytest.mark.asyncio
    async def test_get_badge_by_id(self, badge_repo, mock_db):
        """Testa busca de badge por ID"""
        # Mock de documento
        mock_doc = MagicMock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {
            'id': 'badge1',
            'name': 'Badge 1',
            'description': 'Descrição 1',
            'icon': '🏆',
            'rarity': 'common',
            'color': '#FFD700',
            'requirements': {}
        }
        
        # Configurar mock
        mock_collection = mock_db.collection.return_value
        mock_doc_ref = AsyncMock()
        mock_doc_ref.get.return_value = mock_doc
        mock_collection.document.return_value = mock_doc_ref
        
        # Testar
        badge = await badge_repo.get_badge_by_id("badge1")
        
        assert badge is not None
        assert badge.id == "badge1"
        assert badge.name == "Badge 1"

    @pytest.mark.asyncio
    async def test_get_badge_by_id_not_found(self, badge_repo, mock_db):
        """Testa busca de badge inexistente por ID"""
        # Mock de documento inexistente
        mock_doc = MagicMock()
        mock_doc.exists = False
        
        # Configurar mock
        mock_collection = mock_db.collection.return_value
        mock_collection.document.return_value.get.return_value = mock_doc
        
        # Testar
        badge = await badge_repo.get_badge_by_id("nonexistent")
        
        assert badge is None

    @pytest.mark.asyncio
    async def test_get_user_badge_stats(self, badge_repo, mock_db):
        """Testa estatísticas de badges do usuário"""
        # Mock para get_user_badges
        mock_user_badge = MagicMock()
        mock_user_badge.badge_id = "badge1"
        
        async def mock_user_badges_stream():
            yield mock_user_badge
        
        # Mock para get_all_badges
        mock_badge = MagicMock()
        mock_badge.id = "badge1"
        mock_badge.rarity = "common"
        
        async def mock_all_badges_stream():
            yield mock_badge
        
        # Configurar mocks
        mock_collection = mock_db.collection.return_value
        mock_collection.where.return_value.stream.return_value = mock_user_badges_stream()
        mock_collection.stream.return_value = mock_all_badges_stream()
        
        # Testar
        stats = await badge_repo.get_user_badge_stats("user1")
        
        assert 'total_badges' in stats
        assert 'total_available' in stats
        assert 'completion_percentage' in stats
        assert 'rarity_counts' in stats
