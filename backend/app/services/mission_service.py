from typing import Annotated

from fastapi import Depends
from app.repositories.user_repository import UserRepository, get_user_repository
from app.models.user import UserProfile
from app.models.mission import QuizSubmision
from app.core.firebase import get_firestore_db_async
from app.services.reward_service import RewardService, get_reward_service
from app.services.event_bus import get_event_bus
from app.services.cache_service import get_cache_service
from app.models.events import MissionCompletedEvent, LevelUpEvent, EventType
from app.core.logging_config import get_cryptoquest_logger, LogCategory
import random
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

# Define quantos pontos são necessários para cada nível.
# Manter isso aqui facilita a manutenção e o balanceamento do jogo.
LEVEL_UP_REQUIREMENTS = {
    2: 500,
    3: 1500,
    4: 2500,
    5: 5000,
}


class MissionService:
    def __init__(self, user_repo: UserRepository, dbclient, reward_service: RewardService = None):
        self.user_repo = user_repo
        self.db = dbclient
        self.reward_service = reward_service
        self.event_bus = get_event_bus()
        self.cache = get_cache_service()
        self.cryptoquest_logger = get_cryptoquest_logger()

    async def get_daily_missions_for_user(self, user: UserProfile) -> list:
        """
        Retorna as missões elegíveis para o usuário com cache otimizado.
        Cache de 15 minutos para missões disponíveis.
        """
        cache_key = f"daily_missions_user_{user.uid}"
        
        # Tentar buscar do cache primeiro
        cached_missions = await self.cache.get(cache_key)
        if cached_missions is not None:
            logger.debug(f"Cache hit para missões do usuário {user.uid}")
            return cached_missions
        
        logger.debug(f"Buscando missões elegíveis para usuário {user.uid} (nível: {user.level})")
        
        # Buscar todas as missões disponíveis (com cache de 1 hora)
        all_missions = await self._get_all_missions_cached()
        logger.debug(f"Total de missões encontradas: {len(all_missions)}")

        # Filtra missões elegíveis
        eligible_missions = []
        for mission in all_missions:
            mission_id = mission.get("id") or mission.get("_id")
            logger.debug(f"Verificando missão {mission_id} - Nível requerido: {mission.get('required_level', 1)}")
            
            # Filtro 1: Usuário tem o nível necessário?
            if user.level < mission.get("required_level", 1):
                logger.debug(f"Missão {mission_id} - Nível insuficiente (usuário: {user.level}, requerido: {mission.get('required_level', 1)})")
                continue

            # Filtro 2: Usuário já completou essa missão alguma vez?
            if mission_id in user.completed_missions:
                logger.debug(f"Missão {mission_id} - Já foi completada pelo usuário, pulando")
                continue

            logger.debug(f"Missão {mission_id} - Elegível para seleção")
            eligible_missions.append(mission)

        logger.debug(f"Missões elegíveis encontradas: {len(eligible_missions)}")

        # Seleciona até 3 missões aleatoriamente
        num_missions = min(len(eligible_missions), 3)
        if num_missions == 0:
            logger.debug("Nenhuma missão disponível para o usuário")
            selected_missions = []
        else:
            selected_missions = random.sample(eligible_missions, num_missions)
            selected_ids = [m.get("id") or m.get("_id") for m in selected_missions]
            logger.debug(f"Missões selecionadas: {selected_ids}")
        
        # Cache por 15 minutos (900 segundos)
        await self.cache.set(cache_key, selected_missions, ttl_seconds=900)
        
        return selected_missions

    async def _invalidate_user_cache(self, user_id: str) -> None:
        """Invalida cache do usuário quando missões são completadas"""
        cache_key = f"daily_missions_user_{user_id}"
        await self.cache.delete(cache_key)
        logger.debug(f"Cache invalidado para usuário {user_id}")

    async def _get_all_missions_cached(self) -> list:
        """Busca todas as missões com cache de 1 hora"""
        cache_key = "all_missions"
        
        # Tentar buscar do cache
        cached_missions = await self.cache.get(cache_key)
        if cached_missions is not None:
            logger.debug("Cache hit para todas as missões")
            return cached_missions
        
        logger.debug("Buscando todas as missões do Firestore")
        
        # Buscar do Firestore
        mission_ref = self.db.collection("missions")
        all_missions_docs = mission_ref.stream()
        all_missions = []

        async for doc in all_missions_docs:
            mission_data = doc.to_dict()
            mission_data["_id"] = doc.id
            all_missions.append(mission_data)

        # Cache por 1 hora (3600 segundos)
        await self.cache.set(cache_key, all_missions, ttl_seconds=3600)
        
        return all_missions
    
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

        # Verificar se o usuário já completou essa missão
        completed_map = user_data.get("completed_missions", {}) or {}
        if mission_id in completed_map:
            raise ValueError("Esta missão já foi concluída anteriormente.")

        # Verificar se o usuário tem nível suficiente
        if user_data.get("level", 1) < mission_data.get("required_level", 1):
            raise ValueError("Nível insuficiente para esta missão.")

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

        # Calcular score baseado no tipo de missão
        if mission_data.get("type") == "QUIZ":
            score_percentage = ((correct_answers / len(questions)) * 100) if questions else 0
        else:
            score_percentage = 100  # Para outros tipos de missão

        # Determinar tipo de missão
        mission_type = "daily" if mission_data.get("type") == "DAILY" else "learning_path"

        # Recompensa e progressão
        old_level = user_data.get("level", 1) or 1
        new_points = (user_data.get("points", 0) or 0) + (mission_data.get("reward_points", 0) or 0)
        new_level = old_level
        
        # Verificar level up
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

        # 🎯 NOVO: Emitir eventos para o sistema de badges
        try:
            # Evento de missão completada
            mission_event = MissionCompletedEvent(
                user_id=user_id,
                mission_id=mission_id,
                score=score_percentage,
                mission_type=mission_type,
                points_earned=mission_data.get("reward_points", 0) or 0,
                xp_earned=mission_data.get("reward_xp", 0) or 0
            )
            await self.event_bus.emit(mission_event)
            logger.info(f"🎯 Evento de missão completada emitido: {mission_id}")

            # Evento de level up (se aplicável)
            if new_level > old_level:
                level_up_event = LevelUpEvent(
                    user_id=user_id,
                    old_level=old_level,
                    new_level=new_level,
                    points_required=LEVEL_UP_REQUIREMENTS.get(new_level, 0),
                    points_earned=new_points - (user_data.get("points", 0) or 0)
                )
                await self.event_bus.emit(level_up_event)
                logger.info(f"🎯 Evento de level up emitido: {old_level} -> {new_level}")

        except Exception as e:
            logger.error(f"❌ Erro ao emitir eventos: {e}")
            # Não falha a missão se houver erro nos eventos

        # 🎁 SISTEMA LEGADO: Manter compatibilidade com RewardService
        if self.reward_service:
            try:
                logger.info(f"🎁 Concedendo recompensas legadas para missão {mission_id} (score: {score_percentage:.1f}%)")
                
                # Conceder recompensas
                reward_result = await self.reward_service.award_mission_completion(
                    user_id=user_id,
                    mission_id=mission_id,
                    score=score_percentage,
                    mission_type=mission_type
                )
                
                logger.info(f"✅ Recompensas legadas concedidas: {reward_result}")
                
            except Exception as e:
                logger.error(f"❌ Erro ao conceder recompensas legadas: {e}")
                # Não falha a missão se houver erro nas recompensas

        # Retorno do perfil atualizado
        user_data.update({"points": new_points, "level": new_level})
        # completed_missions pode não existir
        if not user_data.get("completed_missions"):
            user_data["completed_missions"] = {}
        user_data["completed_missions"][mission_id] = update_data[completion_field]
        
        # Invalidar cache do usuário quando missão é completada
        await self._invalidate_user_cache(user_id)
        
        return UserProfile(**{**user_data, "uid": user_id})


def get_mission_service(
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    reward_service: Annotated[RewardService, Depends(get_reward_service)],
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
    return MissionService(user_repo, db_client, reward_service)
