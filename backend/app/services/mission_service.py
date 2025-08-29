from typing import Annotated

from fastapi import Depends
from app.repositories.user_repository import UserRepository, get_user_repository
from app.models.user import UserProfile
from app.models.mission import QuizSubmision
from app.core.firebase import get_firestore_db_async
import random
from datetime import datetime, timezone

# Define quantos pontos são necessários para cada nível.
# Manter isso aqui facilita a manutenção e o balanceamento do jogo.
LEVEL_UP_REQUIREMENTS = {
    2: 500,
    3: 1500,
    4: 2500,
    5: 5000,
}


class MissionService:
    def __init__(self, user_repo: UserRepository, dbclient):
        self.user_repo = user_repo
        self.db = dbclient

    async def get_daily_missions_for_user(self, user: UserProfile) -> list:
        """
        Retorna as missões diárias do usuário. Se for a primeira chamada do dia,
        atribui novas missões. Caso contrário, retorna as missões já atribuídas.
        """
        today = datetime.now(timezone.utc).date()
        
        # Verifica se já tem missões atribuídas para hoje
        if (user.daily_assigned_at and 
            user.daily_assigned_at.date() == today and 
            user.daily_missions):
            # Retorna as missões já atribuídas para hoje
            return await self._get_missions_by_ids(user.daily_missions)
        
        # Primeira chamada do dia - atribui novas missões
        return await self._assign_daily_missions(user, today)
    
    async def _assign_daily_missions(self, user: UserProfile, today: datetime.date) -> list:
        """Atribui novas missões diárias para o usuário"""
        # Busca todas as missões disponíveis
        mission_ref = self.db.collection("missions")
        all_missions_docs = mission_ref.stream()
        all_missions = []

        async for doc in all_missions_docs:
            mission_data = doc.to_dict()
            mission_data["_id"] = doc.id
            all_missions.append(mission_data)

        # Filtra missões elegíveis
        eligible_missions = []
        for mission in all_missions:
            # Filtro 1: Usuário tem o nível necessário?
            if user.level < mission.get("required_level", 1):
                continue

            # Filtro 2: Usuário já completou essa missão hoje?
            mission_id = mission.get("id") or mission.get("_id")
            if mission_id in user.completed_missions:
                completion_date = user.completed_missions[mission_id].date()
                if completion_date == today:
                    continue  # Já completou hoje

            eligible_missions.append(mission)

        # Seleciona até 3 missões aleatoriamente
        num_missions = min(len(eligible_missions), 3)
        if num_missions == 0:
            return []  # Nenhuma missão disponível
            
        selected_missions = random.sample(eligible_missions, num_missions)
        selected_ids = [m.get("id") or m.get("_id") for m in selected_missions]
        
        # Salva as missões atribuídas no perfil do usuário
        update_data = {
            "daily_missions": selected_ids,
            "daily_assigned_at": datetime.now(timezone.utc)
        }
        await self.user_repo.update_user_Profile(user.uid, update_data)
        
        return selected_missions
    
    async def _get_missions_by_ids(self, mission_ids: list[str]) -> list:
        """Busca missões específicas por seus IDs"""
        missions = []
        for mission_id in mission_ids:
            doc = await self.db.collection("missions").document(mission_id).get()
            if doc.exists:
                mission_data = doc.to_dict()
                mission_data["_id"] = doc.id
                missions.append(mission_data)
        return missions

    async def complete_mission(self, user_id: str, mission_id: str, submission: QuizSubmision) -> UserProfile:
        """
        Valida a conclusao de uma missao de quiz, atualiza o perfil do usuario e retorna o perfil alterado.

        Args:
            user_uid(str): O UID do usuario que esta completando a missao
            mission_id: O ID da missao a ser completada
            submission(QuizSubmission): As respostas retornadas pelo Flutter

        Raises:
            ValueError: Se a missao nao for encontrada, se o quiz nao for encontrado,
            ou se o usuario nao atingir a pontuacao minima
        """

        mission_ref = self.db.collection("missions").document(mission_id)
        user_ref = self.db.collection("users").document(user_id)

        # Leitura dos documentos
        mission_doc = await mission_ref.get()
        if not mission_doc.exists:
            raise ValueError("Missão não encontrada!")

        user_doc = await user_ref.get()
        if not user_doc.exists:
            raise ValueError("Usuário não encontrado!")

        mission_data = mission_doc.to_dict()
        user_data = user_doc.to_dict() or {}

        # Verificações de conclusão anterior (no mesmo dia)
        completed_map = user_data.get("completed_missions", {}) or {}
        completed_at = completed_map.get(mission_id)
        if completed_at:
            try:
                completed_date = completed_at.date() if hasattr(completed_at, "date") else None
            except Exception:
                completed_date = None
            today = datetime.now(timezone.utc).date()
            if completed_date == today:
                raise ValueError("Missão já concluída hoje.")

        # Validação de QUIZ
        if mission_data.get("type") == "QUIZ":
            quiz_ref = self.db.collection("quizzes").document(mission_data.get("content_id"))
            quiz_doc = await quiz_ref.get()
            if not quiz_doc.exists:
                raise ValueError("Conteúdo do quiz não encontrado.")

            quiz_data = quiz_doc.to_dict()
            questions = quiz_data.get("questions", [])
            user_answers = submission.answers

            if len(user_answers) != len(questions):
                raise ValueError("Número de respostas inválido.")

            correct_answers = 0
            for i, question in enumerate(questions):
                if user_answers[i] == question.get("correct_answer_index"):
                    correct_answers += 1

            score_percentage = ((correct_answers / len(questions)) * 100) if questions else 0
            if score_percentage < 70.0:
                raise ValueError(
                    f"Você acertou {score_percentage:.0f}%. É necessário acertar pelo menos 70% para concluir."
                )

        # Recompensa e progressão
        new_points = (user_data.get("points", 0) or 0) + (mission_data.get("reward_points", 0) or 0)
        new_level = user_data.get("level", 1) or 1
        while True:
            required_points_for_next_level = LEVEL_UP_REQUIREMENTS.get(new_level + 1)
            if required_points_for_next_level and new_points >= required_points_for_next_level:
                new_level += 1
                continue
            break

        completion_field = f"completed_missions.{mission_id}"
        update_data = {
            "points": new_points,
            "level": new_level,
            completion_field: datetime.now(timezone.utc),
        }

        await user_ref.update(update_data)

        # Retorno do perfil atualizado
        user_data.update({"points": new_points, "level": new_level})
        # completed_missions pode não existir
        if not user_data.get("completed_missions"):
            user_data["completed_missions"] = {}
        user_data["completed_missions"][mission_id] = update_data[completion_field]
        return UserProfile(**{**user_data, "uid": user_id})


def get_mission_service(
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    db_client=Depends(get_firestore_db_async),
) -> MissionService:
    """
    Dependency provider para MissionService

    Cria uma instancia de MisisonService, injetando as suas dependencias.
    Usado pelo sistema de dependencia do FastAPI

    Args:
        user_repo: Repositorio do usuario, injetado automaticamente pelo FastAPI

    Return:
        Uma instancia de MissionService
    """
    return MissionService(user_repo=user_repo, dbclient=db_client)
