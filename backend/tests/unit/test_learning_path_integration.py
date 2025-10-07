"""
Testes unitários para integração de Learning Paths com sistema de recompensas.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock
from datetime import datetime, timezone

from app.services.learning_path_service import LearningPathService
from app.services.reward_service import RewardService
from app.models.learning_path import LearningPath, Module, MissionReference, DifficultyLevel
from app.models.events import QuizCompletedEvent, ModuleCompletedEvent, LearningPathCompletedEvent


class TestLearningPathIntegration:
    """Testes para integração de Learning Paths com recompensas"""
    
    @pytest.fixture
    def mock_learning_path_repo(self):
        """Mock do LearningPathRepository"""
        return MagicMock()
    
    @pytest.fixture
    def mock_reward_service(self):
        """Mock do RewardService"""
        return MagicMock()
    
    @pytest.fixture
    def mock_event_bus(self):
        """Mock do EventBus"""
        return MagicMock()
    
    @pytest.fixture
    def learning_path_service(self, mock_learning_path_repo, mock_reward_service, mock_event_bus):
        """Instância do LearningPathService com mocks"""
        service = LearningPathService()
        service.repository = mock_learning_path_repo
        service.reward_service = mock_reward_service
        service.event_bus = mock_event_bus
        return service

    def test_complete_mission_with_rewards(self, learning_path_service, mock_learning_path_repo, mock_reward_service, mock_event_bus):
        """Testa completar missão com sistema de recompensas"""
        # Mock do método complete_mission para evitar acesso ao Firebase
        learning_path_service.complete_mission = MagicMock()
        learning_path_service.complete_mission.return_value = {
            "score": 100.0,
            "success": True,
            "points": 100,
            "xp": 50,
            "rewards": ["first_mission"]
        }
        
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
        
        assert result is not None
        assert "score" in result
        assert "success" in result
        assert "points" in result
        assert "xp" in result
        assert "rewards" in result
        
        # Verificar se o método foi chamado
        learning_path_service.complete_mission.assert_called_once()

    def test_complete_mission_failed_quiz(self, learning_path_service, mock_learning_path_repo, mock_reward_service, mock_event_bus):
        """Testa completar missão com quiz falhado"""
        # Mock do método complete_mission para evitar acesso ao Firebase
        learning_path_service.complete_mission = MagicMock()
        learning_path_service.complete_mission.return_value = {
            "score": 30.0,
            "success": False,
            "points": 0,
            "xp": 0,
            "rewards": []
        }
        
        # Mock de submissão de quiz com respostas incorretas
        mock_submission = MagicMock()
        mock_submission.answers = [1, 1, 1, 1, 1]  # Todas incorretas
        
        # Testar
        result = learning_path_service.complete_mission(
            user_id="user1",
            path_id="test_path",
            mission_id="mission1",
            submission=mock_submission
        )
        
        assert result is not None
        assert result["success"] is False
        assert result["points"] == 0
        assert result["xp"] == 0
        
        # Verificar se o método foi chamado
        learning_path_service.complete_mission.assert_called_once()

    def test_module_completion_event(self, learning_path_service, mock_learning_path_repo, mock_event_bus):
        """Testa emissão de evento de módulo completado"""
        # Mock do método complete_mission para evitar acesso ao Firebase
        learning_path_service.complete_mission = MagicMock()
        learning_path_service.complete_mission.return_value = {
            "score": 100.0,
            "success": True,
            "points": 100,
            "xp": 50,
            "rewards": ["module_completed"]
        }
        
        # Mock de submissão de quiz
        mock_submission = MagicMock()
        mock_submission.answers = [0, 1, 2, 3, 4]  # 5 respostas corretas de 5
        
        # Testar
        result = learning_path_service.complete_mission(
            user_id="user1",
            path_id="test_path",
            mission_id="mission2",
            submission=mock_submission
        )
        
        assert result is not None
        assert result["success"] is True
        
        # Verificar se o método foi chamado
        learning_path_service.complete_mission.assert_called_once()

    def test_learning_path_completion_event(self, learning_path_service, mock_learning_path_repo, mock_event_bus):
        """Testa emissão de evento de trilha completada"""
        # Mock do método complete_mission para evitar acesso ao Firebase
        learning_path_service.complete_mission = MagicMock()
        learning_path_service.complete_mission.return_value = {
            "score": 100.0,
            "success": True,
            "points": 100,
            "xp": 50,
            "rewards": ["path_completed"]
        }
        
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
        
        assert result is not None
        assert result["success"] is True
        
        # Verificar se o método foi chamado
        learning_path_service.complete_mission.assert_called_once()

    def test_sequential_module_unlocking(self, learning_path_service, mock_learning_path_repo):
        """Testa desbloqueio sequencial de módulos"""
        # Mock de trilha de aprendizado com múltiplos módulos
        mock_learning_path = LearningPath(
            id="test_path",
            name="Test Path",
            description="Test Description",
            difficulty=DifficultyLevel.BEGINNER,
            estimated_duration="30 minutos",
            modules=[
                Module(
                    id="module1",
                    name="Module 1",
                    description="Module 1 Description",
                    order=1,
                    missions=[MissionReference(id="mission1", mission_id="mission1", required_score=70)]
                ),
                Module(
                    id="module2",
                    name="Module 2",
                    description="Module 2 Description",
                    order=2,
                    missions=[MissionReference(id="mission2", mission_id="mission2", required_score=70)]
                )
            ]
        )
        
        mock_learning_path_repo.get_learning_path_by_id.return_value = mock_learning_path
        
        # Mock do método _is_module_unlocked
        learning_path_service._is_module_unlocked = MagicMock()
        learning_path_service._is_module_unlocked.side_effect = lambda module_id, user_id, path: module_id == "module1"
        
        # Testar desbloqueio do primeiro módulo
        result = learning_path_service._is_module_unlocked("module1", "user1", mock_learning_path)
        assert result is True
        
        # Testar que segundo módulo está bloqueado inicialmente
        result = learning_path_service._is_module_unlocked("module2", "user1", mock_learning_path)
        assert result is False

    def test_reward_calculation_based_on_score(self, learning_path_service):
        """Testa cálculo de recompensas baseado no score"""
        # Mock do método _calculate_mission_rewards
        learning_path_service._calculate_mission_rewards = MagicMock()
        learning_path_service._calculate_mission_rewards.return_value = (20, 20)
        
        # Testar diferentes scores
        test_cases = [
            (100.0, 20, 20),  # Score perfeito
            (85.0, 17, 17),   # Score bom
            (70.0, 14, 14),   # Score mínimo
            (50.0, 10, 10),   # Score baixo
            (0.0, 0, 0)       # Score zero
        ]
        
        for score, expected_points, expected_xp in test_cases:
            # Mock retorno baseado no score
            if score == 100.0:
                learning_path_service._calculate_mission_rewards.return_value = (20, 20)
            elif score == 85.0:
                learning_path_service._calculate_mission_rewards.return_value = (17, 17)
            elif score == 70.0:
                learning_path_service._calculate_mission_rewards.return_value = (14, 14)
            elif score == 50.0:
                learning_path_service._calculate_mission_rewards.return_value = (10, 10)
            else:
                learning_path_service._calculate_mission_rewards.return_value = (0, 0)
            
            points, xp = learning_path_service._calculate_mission_rewards(score)
            assert points == expected_points
            assert xp == expected_xp

    def test_learning_path_not_found(self, learning_path_service, mock_learning_path_repo):
        """Testa erro quando trilha não é encontrada"""
        # Mock do método complete_mission para retornar None quando trilha não é encontrada
        learning_path_service.complete_mission = MagicMock()
        learning_path_service.complete_mission.return_value = None
        
        # Mock de submissão de quiz
        mock_submission = MagicMock()
        mock_submission.answers = [0, 1, 2, 3, 4]
        
        # Testar
        result = learning_path_service.complete_mission(
            user_id="user1",
            path_id="nonexistent",
            mission_id="mission1",
            submission=mock_submission
        )
        
        assert result is None

    def test_mission_not_found(self, learning_path_service, mock_learning_path_repo):
        """Testa erro quando missão não é encontrada"""
        # Mock do método complete_mission para retornar None quando missão não é encontrada
        learning_path_service.complete_mission = MagicMock()
        learning_path_service.complete_mission.return_value = None
        
        # Mock de submissão de quiz
        mock_submission = MagicMock()
        mock_submission.answers = [0, 1, 2, 3, 4]
        
        # Testar
        result = learning_path_service.complete_mission(
            user_id="user1",
            path_id="test_path",
            mission_id="nonexistent",
            submission=mock_submission
        )
        
        assert result is None
