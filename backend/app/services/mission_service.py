from typing import Annotated

from fastapi import Depends
from app.repositories.user_repository import UserRepository, get_user_repository
from app.models.user import UserProfile
from app.models.mission import QuizSubmision
from app.core.firebase import get_firestore_db_async
from app.services.reward_service import RewardService, get_reward_service
from app.services.event_bus import get_event_bus
from app.services.cache_service import get_cache_service
from app.models.events import MissionCompletedEvent, LevelUpEvent
import random
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

# Define quantos pontos são necessários para cada nível.
# Manter isso aqui facilita a manutenção e o balanceamento do jogo.
LEVEL_UP_REQUIREMENTS = {
    # Níveis 1-10: 500 XP por nível
    2: 500,      # Nível 2: 500 XP total
    3: 1000,     # Nível 3: 1000 XP total
    4: 1500,     # Nível 4: 1500 XP total
    5: 2000,     # Nível 5: 2000 XP total
    6: 2500,     # Nível 6: 2500 XP total
    7: 3000,     # Nível 7: 3000 XP total
    8: 3500,     # Nível 8: 3500 XP total
    9: 4000,     # Nível 9: 4000 XP total
    10: 4500,    # Nível 10: 4500 XP total
    
    # Níveis 11-20: 750 XP por nível
    11: 5250,    # Nível 11: 5250 XP total
    12: 6000,    # Nível 12: 6000 XP total
    13: 6750,    # Nível 13: 6750 XP total
    14: 7500,    # Nível 14: 7500 XP total
    15: 8250,    # Nível 15: 8250 XP total
    16: 9000,    # Nível 16: 9000 XP total
    17: 9750,    # Nível 17: 9750 XP total
    18: 10500,   # Nível 18: 10500 XP total
    19: 11250,   # Nível 19: 11250 XP total
    20: 12000,   # Nível 20: 12000 XP total
    
    # Níveis 21-30: 1000 XP por nível
    21: 13000,   # Nível 21: 13000 XP total
    22: 14000,   # Nível 22: 14000 XP total
    23: 15000,   # Nível 23: 15000 XP total
    24: 16000,   # Nível 24: 16000 XP total
    25: 17000,   # Nível 25: 17000 XP total
    26: 18000,   # Nível 26: 18000 XP total
    27: 19000,   # Nível 27: 19000 XP total
    28: 20000,   # Nível 28: 20000 XP total
    29: 21000,   # Nível 29: 21000 XP total
    30: 22000,   # Nível 30: 22000 XP total
    
    # Níveis 31-40: 1500 XP por nível
    31: 23500,   # Nível 31: 23500 XP total
    32: 25000,   # Nível 32: 25000 XP total
    33: 26500,   # Nível 33: 26500 XP total
    34: 28000,   # Nível 34: 28000 XP total
    35: 29500,   # Nível 35: 29500 XP total
    36: 31000,   # Nível 36: 31000 XP total
    37: 32500,   # Nível 37: 32500 XP total
    38: 34000,   # Nível 38: 34000 XP total
    39: 35500,   # Nível 39: 35500 XP total
    40: 37000,   # Nível 40: 37000 XP total
    
    # Níveis 41-50: 2000 XP por nível
    41: 39000,   # Nível 41: 39000 XP total
    42: 41000,   # Nível 42: 41000 XP total
    43: 43000,   # Nível 43: 43000 XP total
    44: 45000,   # Nível 44: 45000 XP total
    45: 47000,   # Nível 45: 47000 XP total
    46: 49000,   # Nível 46: 49000 XP total
    47: 51000,   # Nível 47: 51000 XP total
    48: 53000,   # Nível 48: 53000 XP total
    49: 55000,   # Nível 49: 55000 XP total
    50: 57000,   # Nível 50: 57000 XP total
    
    # Níveis 51+: 2500 XP por nível
    51: 59500,   # Nível 51: 59500 XP total
    52: 62000,   # Nível 52: 62000 XP total
    53: 64500,   # Nível 53: 64500 XP total
    54: 67000,   # Nível 54: 67000 XP total
    55: 69500,   # Nível 55: 69500 XP total
    56: 72000,   # Nível 56: 72000 XP total
    57: 74500,   # Nível 57: 74500 XP total
    58: 77000,   # Nível 58: 77000 XP total
    59: 79500,   # Nível 59: 79500 XP total
    60: 82000,   # Nível 60: 82000 XP total
}


class MissionService:
    def __init__(self, user_repo: UserRepository, dbclient, reward_service: RewardService = None):
        self.user_repo = user_repo
        self.db = dbclient
        self.reward_service = reward_service
        self.event_bus = get_event_bus()
        self.cache = get_cache_service()
    
    def _calculate_level_from_xp(self, total_xp: int) -> int:
        """Calcula o nível baseado no XP total"""
        level = 1
        
        for required_level, required_xp in LEVEL_UP_REQUIREMENTS.items():
            if total_xp >= required_xp:
                level = required_level
            else:
                break
        
        return level

    async def get_daily_missions_for_user(self, user: UserProfile) -> list:
        """
        Retorna as missões elegíveis para o usuário com cache otimizado.
        
        Sistema de Rotação Dinâmica:
        - Retorna até 7 missões (ao invés de 3)
        - Seleção aleatória para variedade
        - Cache de 15 minutos para missões disponíveis
        - Filtra por nível e missões já completadas
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

        # Seleciona até 7 missões aleatoriamente (sistema de rotação dinâmica)
        num_missions = min(len(eligible_missions), 7)
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
            mission_passed = score_percentage >= 70.0
        else:
            # Para outros tipos de missão, considerar como aprovado
            mission_passed = True
            score_percentage = 100

        # Calcular score baseado no tipo de missão
        if mission_data.get("type") == "QUIZ":
            # score_percentage já foi calculado acima
            pass
        else:
            score_percentage = 100  # Para outros tipos de missão
            mission_passed = True

        # Determinar tipo de missão
        mission_type = "daily" if mission_data.get("type") == "DAILY" else "learning_path"

        # Recompensa e progressão - apenas se passou na missão
        old_level = user_data.get("level", 1) or 1
        current_xp = user_data.get("xp", 0) or 0
        current_points = user_data.get("points", 0) or 0
        
        if mission_passed:
            # Apenas conceder recompensas se passou
            new_points = current_points + (mission_data.get("reward_points", 0) or 0)
            reward_xp = mission_data.get("reward_xp", 0) or 0
            new_xp = current_xp + reward_xp
            
            # Calcular novo nível baseado em XP
            new_level = self._calculate_level_from_xp(new_xp)
            
            logger.info(f"XP CALCULATION - User: {user_id}")
            logger.info(f"   Current XP: {current_xp}")
            logger.info(f"   Reward XP: {reward_xp}")
            logger.info(f"   New XP: {new_xp}")
            logger.info(f"   Old Level: {old_level}")
            logger.info(f"   New Level: {new_level}")

            completion_field = f"completed_missions.{mission_id}"
            update_data = {
                "points": new_points,
                "xp": new_xp,
                "level": new_level,
                completion_field: datetime.now(timezone.utc),
            }

            await user_ref.update(update_data)
        else:
            # Não passou - não atualizar nada, mas manter valores atuais
            new_points = current_points
            new_xp = current_xp
            new_level = old_level
            logger.info(f"Missão {mission_id} não aprovada - Score: {score_percentage:.1f}% (mínimo: 70%)")
        
        if mission_passed:
            logger.info(f"FIRESTORE UPDATE - User: {user_id}")
            logger.info(f"   Points: {user_data.get('points', 0)} → {new_points}")
            logger.info(f"   XP: {current_xp} → {new_xp}")
            logger.info(f"   Level: {old_level} → {new_level}")
            logger.info(f"   Mission: {mission_id} completed at {datetime.now(timezone.utc)}")

            # Emitir eventos para o sistema de badges
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
                logger.info(f"Evento de missão completada emitido: {mission_id}")

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
                    logger.info(f"Evento de level up emitido: {old_level} -> {new_level}")

            except Exception as e:
                logger.error(f"Erro ao emitir eventos: {e}")
                # Não falha a missão se houver erro nos eventos

            # Sistema legado desabilitado para evitar duplicação de XP
            if False and self.reward_service:
                try:
                    logger.info(f"Concedendo recompensas legadas para missão {mission_id} (score: {score_percentage:.1f}%)")
                    
                    reward_result = await self.reward_service.award_mission_completion(
                        user_id=user_id,
                        mission_id=mission_id,
                        score=score_percentage,
                        mission_type=mission_type
                    )
                    
                    logger.info(f"Recompensas legadas concedidas: {reward_result}")
                    
                except Exception as e:
                    logger.error(f"Erro ao conceder recompensas legadas: {e}")
                    # Não falha a missão se houver erro nas recompensas

            # Atualizar completed_missions apenas se passou
            if not user_data.get("completed_missions"):
                user_data["completed_missions"] = {}
            user_data["completed_missions"][mission_id] = update_data[completion_field]
            
            # Invalidar cache do usuário quando missão é completada
            await self._invalidate_user_cache(user_id)
        else:
            # Não passou - não atualizar perfil, apenas retornar dados atuais
            logger.info(f"Missão {mission_id} não aprovada - mantendo perfil atual")
            # Não invalidar cache pois a missão não foi completada

        # Retornar perfil (atualizado se passou, ou atual se não passou)
        user_data.update({"points": new_points, "xp": new_xp, "level": new_level})
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
