"""
Utilitários e helpers para testes.
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from unittest.mock import AsyncMock, MagicMock

# Adicionar o diretório backend ao path
backend_path = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(backend_path))

from app.core.firebase import get_firestore_db_async
from app.models.user import UserProfile
from app.models.events import MissionCompletedEvent, LevelUpEvent, PointsEarnedEvent


<<<<<<< HEAD
class DataManager:
=======
class TestDataManager:
>>>>>>> ceffef1 (feat: Implementacao final do sistema de recompensas)
    """Gerenciador de dados de teste"""
    
    def __init__(self):
        self.test_users = []
        self.test_badges = []
        self.cleanup_tasks = []
    
    async def create_test_user(self, user_id: str, **kwargs) -> UserProfile:
        """Cria um usuário de teste"""
        default_data = {
            'uid': user_id,
            'name': f'Test User {user_id}',
            'email': f'{user_id}@test.com',
            'register_date': datetime.now(timezone.utc),
            'level': 1,
            'points': 0,
            'completed_missions': {},
            'daily_missions': [],
            'has_completed_questionnaire': False
        }
        
        user_data = {**default_data, **kwargs}
        user = UserProfile(**user_data)
        self.test_users.append(user_id)
        return user
<<<<<<< HEAD
 
=======
    
>>>>>>> ceffef1 (feat: Implementacao final do sistema de recompensas)
    async def cleanup_test_user(self, db, user_id: str):
        """Limpa dados de teste de um usuário"""
        try:
            # Remover badges do usuário
            badges_query = db.collection("user_badges").where("user_id", "==", user_id)
            badges_docs = badges_query.stream()
            async for doc in badges_docs:
                await doc.reference.delete()
            
            # Remover usuário
            user_doc = db.collection("users").document(user_id)
            await user_doc.delete()
            
        except Exception as e:
            print(f"⚠️ Erro ao limpar usuário {user_id}: {e}")
    
    async def cleanup_all(self, db):
        """Limpa todos os dados de teste"""
        for user_id in self.test_users:
            await self.cleanup_test_user(db, user_id)
        self.test_users.clear()


class EventTestHelper:
    """Helper para criar eventos de teste"""
    
    @staticmethod
    def create_mission_event(user_id: str, **kwargs) -> MissionCompletedEvent:
        """Cria evento de missão completada para teste"""
        default_data = {
            'user_id': user_id,
            'mission_id': f'test_mission_{user_id}',
<<<<<<< HEAD
            'score': 100.0,
=======
            'score': 85.0,
>>>>>>> ceffef1 (feat: Implementacao final do sistema de recompensas)
            'mission_type': 'daily',
            'points_earned': 100,
            'xp_earned': 50
        }
        
        event_data = {**default_data, **kwargs}
        return MissionCompletedEvent(**event_data)
    
    @staticmethod
    def create_level_up_event(user_id: str, **kwargs) -> LevelUpEvent:
        """Cria evento de level up para teste"""
        default_data = {
            'user_id': user_id,
            'old_level': 1,
            'new_level': 2,
<<<<<<< HEAD
            'points_required': 100,
            'points_earned': 100
=======
            'points_required': 500,
            'points_earned': 200
>>>>>>> ceffef1 (feat: Implementacao final do sistema de recompensas)
        }
        
        event_data = {**default_data, **kwargs}
        return LevelUpEvent(**event_data)
    
    @staticmethod
    def create_points_event(user_id: str, **kwargs) -> PointsEarnedEvent:
        """Cria evento de pontos ganhos para teste"""
        default_data = {
            'user_id': user_id,
<<<<<<< HEAD
            'points_amount': 100,
            'xp_amount': 50,
            'source': 'mission',
            'points_earned': 100,
            'total_points': 100
=======
            'points_amount': 1000,
            'xp_amount': 500,
            'source': 'mission',
            'points_earned': 1000,
            'total_points': 1000
>>>>>>> ceffef1 (feat: Implementacao final do sistema de recompensas)
        }
        
        event_data = {**default_data, **kwargs}
        return PointsEarnedEvent(**event_data)


class MockHelper:
    """Helper para criar mocks"""
    
    @staticmethod
    def create_firestore_mock():
        """Cria mock do Firestore"""
        mock_db = MagicMock()
        
        # Configurar collection mock
        mock_collection = MagicMock()
        mock_db.collection.return_value = mock_collection
        
        return mock_db
    
    @staticmethod
    def create_user_repo_mock():
        """Cria mock do UserRepository"""
        mock_repo = AsyncMock()
        mock_repo.get_user_profile.return_value = None
        mock_repo.create_user_profile.return_value = None
        return mock_repo
    
    @staticmethod
    def create_badge_repo_mock():
        """Cria mock do BadgeRepository"""
        mock_repo = AsyncMock()
        mock_repo.has_badge.return_value = False
        mock_repo.award_badge.return_value = True
        mock_repo.get_user_badges.return_value = []
        mock_repo.get_all_badges.return_value = []
        return mock_repo


class TestConfig:
    """Configurações para testes"""
    
    # URLs de teste
<<<<<<< HEAD
    BASE_URL = "http://localhost:8000"
    
    # Timeouts
    DEFAULT_TIMEOUT = 30
    EVENT_PROCESSING_DELAY = 0.1
=======
    BASE_URL = "http://localhost:8001"
    
    # Timeouts
    DEFAULT_TIMEOUT = 30
    EVENT_PROCESSING_DELAY = 1
>>>>>>> ceffef1 (feat: Implementacao final do sistema de recompensas)
    
    # Dados de teste
    TEST_USER_PREFIX = "test_user_"
    TEST_MISSION_PREFIX = "test_mission_"
    TEST_BADGE_PREFIX = "test_badge_"
    
    # Configurações do Firebase
    FIREBASE_PROJECT_ID = "cryptoquest-test"
<<<<<<< HEAD
 
=======
    
>>>>>>> ceffef1 (feat: Implementacao final do sistema de recompensas)
    @classmethod
    def get_test_user_id(cls, suffix: str = "") -> str:
        """Gera ID de usuário de teste"""
        timestamp = int(datetime.now().timestamp())
        return f"{cls.TEST_USER_PREFIX}{timestamp}{suffix}"
    
    @classmethod
    def get_test_mission_id(cls, suffix: str = "") -> str:
        """Gera ID de missão de teste"""
        timestamp = int(datetime.now().timestamp())
        return f"{cls.TEST_MISSION_PREFIX}{timestamp}{suffix}"


async def wait_for_event_processing(delay: float = None):
    """Aguarda processamento de eventos"""
    if delay is None:
        delay = TestConfig.EVENT_PROCESSING_DELAY
    await asyncio.sleep(delay)


def assert_event_emitted(event_bus, event_type: str, user_id: str = None):
    """Verifica se um evento foi emitido"""
    events = event_bus.get_event_log()
    
    if user_id:
        events = [e for e in events if e.user_id == user_id]
    
    event_types = [e.event_type for e in events]
    assert event_type in event_types, f"Evento {event_type} não foi emitido. Eventos: {event_types}"


def assert_badge_awarded(badges, badge_id: str):
    """Verifica se um badge foi concedido"""
    badge_ids = [b.badge_id for b in badges]
    assert badge_id in badge_ids, f"Badge {badge_id} não foi concedido. Badges: {badge_ids}"


def assert_no_duplicates(badges):
    """Verifica se não há badges duplicados"""
    badge_ids = [b.badge_id for b in badges]
    unique_ids = set(badge_ids)
    assert len(badge_ids) == len(unique_ids), f"Badges duplicados encontrados: {badge_ids}"

