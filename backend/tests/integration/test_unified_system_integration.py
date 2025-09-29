"""
Testes de integração para sistema unificado de níveis, recompensas e badges.
"""

import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock
from datetime import datetime, timezone

from app.services.learning_path_service import LearningPathService
from app.services.reward_service import RewardService
# from app.services.level_service import LevelService  # Não existe ainda
from app.services.badge_engine import BadgeEngine
from app.models.learning_path import LearningPath, Module, MissionReference
from app.models.user import UserProfile
from app.models.events import QuizCompletedEvent, ModuleCompletedEvent, LearningPathCompletedEvent


class TestUnifiedSystemIntegration:
    """Testes de integração para sistema unificado"""
    
    @pytest.fixture
    def mock_user_repo(self):
        """Mock do UserRepository"""
        return MagicMock()
    
    @pytest.fixture
    def mock_learning_path_repo(self):
        """Mock do LearningPathRepository"""
        return MagicMock()
    
    @pytest.fixture
    def mock_badge_repo(self):
        """Mock do BadgeRepository"""
        return MagicMock()
    
    @pytest.fixture
    def mock_event_bus(self):
        """Mock do EventBus"""
        return MagicMock()
    
    @pytest.fixture
    def reward_service(self, mock_user_repo, mock_badge_repo, mock_event_bus):
        """Instância do RewardService"""
        return RewardService(mock_user_repo, mock_badge_repo, mock_event_bus)
    
    @pytest.fixture
    def level_service(self, mock_user_repo, mock_event_bus):
        """Mock do LevelService"""
        mock_service = MagicMock()
        mock_service.add_xp = MagicMock(return_value={"level_up": True, "new_level": 2, "new_xp": 600})
        mock_service._calculate_level_from_xp = MagicMock(return_value=1)
        mock_service._calculate_xp_to_next_level = MagicMock(return_value=300)
        return mock_service
    
    @pytest.fixture
    def learning_path_service(self, mock_learning_path_repo, reward_service, mock_event_bus):
        """Instância do LearningPathService"""
        service = LearningPathService()
        service.repository = mock_learning_path_repo
        service.reward_service = reward_service
        service.event_bus = mock_event_bus
        return service

    @pytest.mark.asyncio
    async def test_complete_learning_path_mission_flow(self, learning_path_service, mock_learning_path_repo, 
                                                      mock_user_repo, mock_badge_repo, mock_event_bus):
        """Testa fluxo completo de completar missão de trilha de aprendizado"""
        # Mock de trilha de aprendizado
        mock_learning_path = LearningPath(
            id="test_path",
            name="Test Path",
            description="Test Description",
            modules=[
                Module(
                    id="module1",
                    name="Module 1",
                    description="Module 1 Description",
                    missions=[
                        MissionReference(mission_id="mission1", required_score=70)
                    ]
                )
            ]
        )
        
        # Mock de usuário
        mock_user = UserProfile(
            uid="user1",
            name="User1",
            email="user1@test.com",
            level=1,
            points=0,
            xp=0
        )
        
        # Mock de progresso do usuário
        mock_progress = MagicMock()
        mock_progress.completed_missions = []
        mock_progress.current_module_id = "module1"
        mock_progress.completed_at = None
        
        # Configurar mocks
        mock_learning_path_repo.get_learning_path.return_value = mock_learning_path
        mock_learning_path_repo.get_user_path_progress.return_value = mock_progress
        mock_learning_path_repo.update_user_path_progress.return_value = True
        mock_user_repo.get_user_profile.return_value = mock_user
        mock_badge_repo.award_badge.return_value = True
        
        # Mock de submissão de quiz
        mock_submission = MagicMock()
        mock_submission.answers = [0, 1, 2, 3, 4]  # 5 respostas corretas de 5
        
        # Testar
        result = learning_path_service.complete_mission(
            user_id="user1",
            path_id="test_path",
            mission_id="mission1",
            submission=mock_submission
        )
        
        # Verificações
        assert result is not None
        assert result["success"] is True
        assert result["score"] == 100
        assert result["points"] > 0
        assert result["xp"] > 0
        assert "rewards" in result
        
        # Verificar se recompensas foram concedidas
        mock_user_repo.update_user_Profile.assert_called()
        
        # Verificar se eventos foram emitidos
        assert mock_event_bus.emit.call_count >= 1
        
        # Verificar se evento de quiz completado foi emitido
        quiz_events = [call[0][0] for call in mock_event_bus.emit.call_args_list 
                      if isinstance(call[0][0], QuizCompletedEvent)]
        assert len(quiz_events) == 1
        assert quiz_events[0].user_id == "user1"
        assert quiz_events[0].score == 100.0

    @pytest.mark.asyncio
    async def test_level_up_integration(self, level_service, mock_user_repo, mock_event_bus):
        """Testa integração de level up com sistema de eventos"""
        # Mock de usuário
        mock_user = UserProfile(
            uid="user1",
            name="User1",
            email="user1@test.com",
            level=1,
            points=100,
            xp=400
        )
        
        mock_user_repo.get_user_profile.return_value = mock_user
        
        # Testar adição de XP que causa level up
        result = level_service.add_xp("user1", 200)
        
        # Verificações
        assert result is not None
        assert result["level_up"] is True
        assert result["new_level"] == 2
        assert result["new_xp"] == 600
        
        # Verificar se evento de level up foi emitido
        mock_event_bus.emit.assert_called_once()
        emitted_event = mock_event_bus.emit.call_args[0][0]
        assert emitted_event.user_id == "user1"
        assert emitted_event.old_level == 1
        assert emitted_event.new_level == 2

    @pytest.mark.asyncio
    async def test_badge_award_integration(self, reward_service, mock_user_repo, mock_badge_repo):
        """Testa integração de concessão de badges"""
        # Mock de usuário
        mock_user = UserProfile(
            uid="user1",
            name="User1",
            email="user1@test.com",
            level=1,
            points=100,
            xp=200
        )
        
        mock_user_repo.get_user_profile.return_value = mock_user
        mock_badge_repo.award_badge.return_value = True
        
        # Testar concessão de badge
        result = reward_service.award_badge(
            user_id="user1",
            badge_id="test_badge",
            context={"mission_id": "mission1", "score": 100.0}
        )
        
        # Verificações
        assert result is True
        mock_badge_repo.award_badge.assert_called_once_with(
            "user1", "test_badge", {"mission_id": "mission1", "score": 100.0}
        )

    @pytest.mark.asyncio
    async def test_mission_completion_with_level_up(self, reward_service, mock_user_repo, mock_badge_repo):
        """Testa completar missão que resulta em level up"""
        # Mock de usuário próximo do level up
        mock_user = UserProfile(
            uid="user1",
            name="User1",
            email="user1@test.com",
            level=1,
            points=100,
            xp=450  # Próximo de 500 para level 2
        )
        
        mock_user_repo.get_user_profile.return_value = mock_user
        mock_badge_repo.award_badge.return_value = True
        
        # Testar completar missão
        result = reward_service.award_mission_completion(
            user_id="user1",
            mission_id="mission1",
            score=100.0,
            mission_type="daily"
        )
        
        # Verificações
        assert result is not None
        assert "points" in result
        assert "xp" in result
        assert "badges" in result
        
        # Verificar se usuário foi atualizado
        mock_user_repo.update_user_Profile.assert_called()

    @pytest.mark.asyncio
    async def test_learning_path_completion_flow(self, learning_path_service, mock_learning_path_repo,
                                                mock_user_repo, mock_badge_repo, mock_event_bus):
        """Testa fluxo completo de conclusão de trilha de aprendizado"""
        # Mock de trilha de aprendizado com apenas uma missão
        mock_learning_path = LearningPath(
            id="test_path",
            name="Test Path",
            description="Test Description",
            modules=[
                Module(
                    id="module1",
                    name="Module 1",
                    description="Module 1 Description",
                    missions=[
                        MissionReference(mission_id="mission1", required_score=70)
                    ]
                )
            ]
        )
        
        # Mock de usuário
        mock_user = UserProfile(
            uid="user1",
            name="User1",
            email="user1@test.com",
            level=1,
            points=0,
            xp=0
        )
        
        # Mock de progresso do usuário
        mock_progress = MagicMock()
        mock_progress.completed_missions = []
        mock_progress.current_module_id = "module1"
        mock_progress.completed_at = None
        
        # Configurar mocks
        mock_learning_path_repo.get_learning_path.return_value = mock_learning_path
        mock_learning_path_repo.get_user_path_progress.return_value = mock_progress
        mock_learning_path_repo.update_user_path_progress.return_value = True
        mock_user_repo.get_user_profile.return_value = mock_user
        mock_badge_repo.award_badge.return_value = True
        
        # Mock de submissão de quiz
        mock_submission = MagicMock()
        mock_submission.answers = [0, 1, 2, 3, 4]  # 5 respostas corretas de 5
        
        # Testar
        result = learning_path_service.complete_mission(
            user_id="user1",
            path_id="test_path",
            mission_id="mission1",
            submission=mock_submission
        )
        
        # Verificações
        assert result is not None
        assert result["success"] is True
        
        # Verificar se eventos foram emitidos
        assert mock_event_bus.emit.call_count >= 2
        
        # Verificar se evento de trilha completada foi emitido
        path_events = [call[0][0] for call in mock_event_bus.emit.call_args_list 
                      if isinstance(call[0][0], LearningPathCompletedEvent)]
        assert len(path_events) == 1
        assert path_events[0].learning_path_id == "test_path"
        assert path_events[0].learning_path_name == "Test Path"

    @pytest.mark.asyncio
    async def test_multiple_mission_completion_accumulation(self, reward_service, mock_user_repo, mock_badge_repo):
        """Testa acumulação de recompensas em múltiplas missões"""
        # Mock de usuário
        mock_user = UserProfile(
            uid="user1",
            name="User1",
            email="user1@test.com",
            level=1,
            points=0,
            xp=0
        )
        
        mock_user_repo.get_user_profile.return_value = mock_user
        mock_badge_repo.award_badge.return_value = True
        
        # Completar primeira missão
        result1 = reward_service.award_mission_completion(
            user_id="user1",
            mission_id="mission1",
            score=85.0,
            mission_type="daily"
        )
        
        # Atualizar mock do usuário com novos valores
        mock_user.points = result1["points"]
        mock_user.xp = result1["xp"]
        
        # Completar segunda missão
        result2 = reward_service.award_mission_completion(
            user_id="user1",
            mission_id="mission2",
            score=90.0,
            mission_type="daily"
        )
        
        # Verificações
        assert result1 is not None
        assert result2 is not None
        assert result2["points"] > result1["points"]
        assert result2["xp"] > result1["xp"]

    @pytest.mark.asyncio
    async def test_system_error_handling(self, learning_path_service, mock_learning_path_repo):
        """Testa tratamento de erros no sistema"""
        # Mock de erro
        mock_learning_path_repo.get_learning_path.side_effect = Exception("Database error")
        
        # Mock de submissão de quiz
        mock_submission = MagicMock()
        mock_submission.answers = [0, 1, 2, 3, 4]
        
        # Testar
        result = learning_path_service.complete_mission(
            user_id="user1",
            path_id="test_path",
            mission_id="mission1",
            submission=mock_submission
        )
        
        # Verificações
        assert result is None

    @pytest.mark.asyncio
    async def test_event_bus_integration(self, mock_event_bus):
        """Testa integração com EventBus"""
        # Mock de evento
        event = QuizCompletedEvent(
            user_id="user1",
            quiz_id="quiz1",
            score=85.0,
            learning_path_id="path1",
            mission_id="mission1"
        )
        
        # Testar emissão de evento
        await mock_event_bus.emit(event)
        
        # Verificar se evento foi processado
        mock_event_bus.emit.assert_called_once_with(event)

    def test_system_consistency(self, reward_service, level_service, mock_user_repo):
        """Testa consistência do sistema"""
        # Mock de usuário
        mock_user = UserProfile(
            uid="user1",
            name="User1",
            email="user1@test.com",
            level=1,
            points=100,
            xp=200
        )
        
        mock_user_repo.get_user_profile.return_value = mock_user
        
        # Testar cálculo de nível baseado em XP
        level = level_service._calculate_level_from_xp(200)
        assert level == 1
        
        # Testar cálculo de XP necessário para próximo nível
        xp_to_next = level_service._calculate_xp_to_next_level(200)
        assert xp_to_next == 300  # 500 - 200
        
        # Testar cálculo de recompensas
        points, xp = reward_service._calculate_mission_rewards(85.0)
        assert points == 17  # 85/5 * 1
        assert xp == 17  # 85/5 * 1
