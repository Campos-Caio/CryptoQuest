from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from app.models.ranking import Ranking, RankingEntry, RankingType, UserRankingStats
from app.models.user import UserProfile
from app.repositories.user_repository import UserRepository, get_user_repository
from app.repositories.ranking_repository import RankingRepository, get_ranking_repository
from fastapi import Depends
import logging

logger = logging.getLogger(__name__)

class RankingService:
    def __init__(self, user_repo: UserRepository, ranking_repo: RankingRepository):
        self.user_repo = user_repo
        self.ranking_repo = ranking_repo

    async def generate_global_ranking(self, limit: int = 100) -> Ranking:
        """Gera ranking global de usuários"""
        try:
            users = self.user_repo.get_all_users()
            
            # Calcular score de ranking para cada usuário
            ranking_entries = []
            for user in users:
                score = await self._calculate_ranking_score(user)
                entry = RankingEntry(
                    user_id=user.uid,
                    name=user.name,
                    email=user.email,
                    points=user.points,
                    xp=user.xp,
                    level=user.level,
                    rank=0,  # Será definido após ordenação
                    badges=user.badges,
                    last_activity=user.register_date  # Usar campo apropriado
                )
                ranking_entries.append(entry)

            # Ordenar por score de ranking
            ranking_entries.sort(key=lambda x: x.xp + x.points, reverse=True)
            
            # Definir ranks
            for i, entry in enumerate(ranking_entries):
                entry.rank = i + 1

            ranking = Ranking(
                type=RankingType.GLOBAL,
                period="all_time",
                entries=ranking_entries[:limit],
                total_users=len(users)
            )

            self.ranking_repo.save_ranking(ranking)
            return ranking

        except Exception as e:
            logger.error(f"Erro ao gerar ranking global: {e}")
            raise

    async def generate_weekly_ranking(self, week_start: datetime) -> Ranking:
        """Gera ranking semanal"""
        try:
            week_end = week_start + timedelta(days=7)
            users = self.user_repo.get_users_by_activity_period(week_start, week_end)
            
            # Implementar lógica específica para ranking semanal
            ranking_entries = []
            for user in users:
                weekly_score = await self._calculate_weekly_score(user, week_start, week_end)
                entry = RankingEntry(
                    user_id=user.uid,
                    name=user.name,
                    email=user.email,
                    points=weekly_score,
                    xp=weekly_score,
                    level=user.level,
                    rank=0,
                    badges=user.badges,
                    last_activity=week_start
                )
                ranking_entries.append(entry)

            ranking_entries.sort(key=lambda x: x.xp, reverse=True)
            for i, entry in enumerate(ranking_entries):
                entry.rank = i + 1

            ranking = Ranking(
                type=RankingType.WEEKLY,
                period=week_start.strftime("%Y-W%U"),
                entries=ranking_entries,
                total_users=len(users)
            )

            self.ranking_repo.save_ranking(ranking)
            return ranking

        except Exception as e:
            logger.error(f"Erro ao gerar ranking semanal: {e}")
            raise

    async def get_user_ranking_stats(self, user_id: str) -> UserRankingStats:
        """Retorna estatísticas de ranking do usuário"""
        try:
            global_ranking = self.ranking_repo.get_latest_ranking(RankingType.GLOBAL)
            weekly_ranking = self.ranking_repo.get_latest_ranking(RankingType.WEEKLY)
            
            # Encontrar posição do usuário em cada ranking
            global_rank = self._find_user_rank(global_ranking, user_id)
            weekly_rank = self._find_user_rank(weekly_ranking, user_id)
            
            # Calcular percentil
            total_users = global_ranking.total_users if global_ranking else 0
            percentile = ((total_users - global_rank + 1) / total_users * 100) if total_users > 0 else 0

            return UserRankingStats(
                user_id=user_id,
                global_rank=global_rank,
                weekly_rank=weekly_rank,
                monthly_rank=0,  # Implementar
                level_rank=0,    # Implementar
                total_users=total_users,
                percentile=percentile
            )

        except Exception as e:
            logger.error(f"Erro ao obter estatísticas de ranking: {e}")
            raise

    async def _calculate_ranking_score(self, user: UserProfile) -> int:
        """Calcula score de ranking para o usuário"""
        base_score = user.points + (user.xp if hasattr(user, 'xp') else 0)
        
        # Bônus por consistência (streak)
        streak_bonus = min(user.current_streak * 10, 200) if hasattr(user, 'current_streak') else 0
        
        # Bônus por diversidade (diferentes trilhas)
        diversity_bonus = len(user.completed_learning_paths) * 50 if hasattr(user, 'completed_learning_paths') else 0
        
        # Bônus por qualidade (scores altos)
        quality_bonus = user.average_score * 2 if hasattr(user, 'average_score') else 0
        
        return base_score + streak_bonus + diversity_bonus + quality_bonus

    async def _calculate_weekly_score(self, user: UserProfile, start: datetime, end: datetime) -> int:
        """Calcula score semanal do usuário"""
        # Implementar lógica específica para score semanal
        return user.points  # Placeholder

    def _find_user_rank(self, ranking: Ranking, user_id: str) -> int:
        """Encontra a posição do usuário no ranking"""
        if not ranking:
            return 0
        
        for entry in ranking.entries:
            if entry.user_id == user_id:
                return entry.rank
        return 0

def get_ranking_service(
    user_repo = Depends(get_user_repository),
    ranking_repo = Depends(get_ranking_repository)
) -> RankingService:
    return RankingService(user_repo, ranking_repo)