from typing import Annotated

from fastapi import Depends
from app.repositories.user_repository import UserRepository, get_user_repository
from app.models.user import UserProfile
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
        # 1 Busca a biblioteca de todas a missoes no firestore
        mission_ref = self.db.collection("missions")
        all_missions_docs = mission_ref.stream()
        all_missions = []


        async for doc in all_missions_docs:
            if doc.exists:
                mission_data = doc.to_dict()
                mission_data["_id"] = doc.id  # Adiciona o ID do documento
                all_missions.append(mission_data)
                # Filtra as missoe sque o usuario pode fazer
                elegible_missions = []
        today = datetime.now(timezone.utc).date()

        for mission in all_missions:
            # Filtro 1: O usuario tem o nivel necessario?
            if user.level < mission.get("required_level", 1):
                continue

            # Filtro 2: O usuario ja completou essa missao hoje?
            mission_id = mission.get("id")
            if mission_id in user.completed_missions:
                completion_date = user.completed_missions[mission_id].date()
                if completion_date == today:
                    continue  # Ja completou hj

            elegible_missions.append(mission)

        # Seleciona aleatoriamente um numero de missoes
        num_missoes_to_return = min(len(elegible_missions), 3)
        daily_missions = random.sample(elegible_missions, num_missoes_to_return)

        return daily_missions

    async def complete_mission(self, user_id: str, mission_id: str) -> UserProfile:
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

        # Usando uma transacao para garantir que todas ou nenhuma as atualizacoes acontecam
        transaction = self.db.transaction()

        @transactional
        async def update_in_transaction(transaction):
            # Busca os docs DENTRO da transacao
            mission_doc = await mission_ref.get(transaction=transaction)
            if not mission_doc.exists:
                raise ValueError("Missão não encontrada!")

            user_doc = await user_ref.get(transaction=transaction)
            if not user_doc.exists:
                raise ValueError("Usuário  não encontrado!")

            mission_data = mission_doc.to_dict()
            user_data = user_doc.to_dict()

            # Logica de validacao, ex: verificar respostasa do quizz etc
            if mission_data.get("type") == "QUIZ":
                quiz_ref = self.db.collection("quizzes").document(
                    mission_data["content_id"]
                )
                quiz_doc = await quiz_ref.get()
                if not quiz_doc.exists:
                    raise ValueError("Conteúdo do quiz não encontrado.")

                quiz_data = quiz_doc.to_dict()
                questions = quiz_data.get("questions", [])
                user_answers = submission.answers

                # Garante que o numero de respostas corresponde ao de perguntas
                if len(user_answers) != len(questions):
                    raise ValueError("Número de respostas inválido.")

                # Calcula a pontuacao
                correct_answers = 0
                for i, question in enumerate(questions):
                    if user_answers[i] == question.get("correct_answer_index"):
                        correct_answers += 1

                # Criterio de sucesso: acertar pelo menos 70%
                score_percentage = (
                    (correct_answers / len(questions)) * 100 if questions else 0
                )
                if score_percentage <= 70.0:
                    raise ValueError(
                        f"Você acertou {score_percentage:.0f}%. É necessário acertar pelo menos 70% para concluir."
                    )

            # Logica de Recompensa e Progressao
            new_points = user_data.get("points", 0) + mission_data.get(
                "reward_points", 0
            )
            new_level = user_data.get("level", 1)

            # Logica de Level Up
            required_points_for_next_level = LEVEL_UP_REQUIREMENTS.get(new_level + 1)
            if (
                required_points_for_next_level
                and new_points >= required_points_for_next_level
            ):
                new_level += 1

                # (TODO) Adicionar notificacao de Lvl Up

            #  Prepara a atualizacao para o firestore
            completion_field = f"completed_missions.{mission_id}"
            update_data = {
                "points": new_points,
                "level": new_level,
                completion_field: datetime.now(timezone.utc),
            }

            # Executa a atualizacao dentro da transacao
            transaction.update(user_ref, update_data)

            # Retorna o perfil atualizado para a API
            user_data.update(update_data)
            user_data["completed_missions"][mission_id] = update_data.pop(
                completion_field
            )
            return user_data

        # Executa  funcao transacional
        update_user_data = await update_in_transaction
        return UserProfile(**update_user_data)


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
