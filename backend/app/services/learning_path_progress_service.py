"""
Serviço para gerenciar progresso de usuários em learning paths.
Separação de responsabilidades do LearningPathService.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, UTC
from app.models.learning_path import UserPathProgress
from app.repositories.learning_path_repository import LearningPathRepository
from app.services.cache_service import get_cache_service

logger = logging.getLogger(__name__)

class LearningPathProgressService:
    """
    Serviço especializado em gerenciar progresso de usuários em learning paths.
    
    Responsabilidades:
    - Gerenciar progresso de usuários em trilhas
    - Cache de progresso para otimização
    - Validação de progresso
    - Atualização de estatísticas
    """
    
    def __init__(self, learning_path_repo: LearningPathRepository):
        self.learning_path_repo = learning_path_repo
        self.cache = get_cache_service()
    
    async def get_user_progress(self, user_id: str, path_id: str) -> Optional[UserPathProgress]:
        """
        Obtém o progresso do usuário em uma trilha específica.
        
        Args:
            user_id: ID do usuário
            path_id: ID da trilha
            
        Returns:
            UserPathProgress ou None se não encontrado
        """
        cache_key = f"user_progress_{user_id}_{path_id}"
        
        # Tentar buscar do cache primeiro
        cached_progress = await self.cache.get(cache_key)
        if cached_progress is not None:
            logger.debug(f"Cache hit para progresso do usuário {user_id} na trilha {path_id}")
            return cached_progress
        
        # Buscar do repositório
        progress = self.learning_path_repo.get_user_progress(user_id, path_id)
        
        # Cache por 5 minutos
        if progress:
            await self.cache.set(cache_key, progress, ttl_seconds=300)
        
        return progress
    
    async def create_user_progress(self, user_id: str, path_id: str) -> UserPathProgress:
        """
        Cria um novo progresso para o usuário em uma trilha.
        
        Args:
            user_id: ID do usuário
            path_id: ID da trilha
            
        Returns:
            UserPathProgress criado
        """
        progress = self.learning_path_repo.create_user_progress(user_id, path_id)
        
        # Invalidar cache
        cache_key = f"user_progress_{user_id}_{path_id}"
        await self.cache.delete(cache_key)
        
        logger.info(f"Progresso criado para usuário {user_id} na trilha {path_id}")
        return progress
    
    async def update_progress(self, user_id: str, path_id: str, 
                            completed_module_id: Optional[str] = None,
                            completed_mission_id: Optional[str] = None,
                            score: int = 0) -> UserPathProgress:
        """
        Atualiza o progresso do usuário em uma trilha.
        
        Args:
            user_id: ID do usuário
            path_id: ID da trilha
            completed_module_id: ID do módulo completado (opcional)
            completed_mission_id: ID da missão completada (opcional)
            score: Pontuação obtida
            
        Returns:
            UserPathProgress atualizado
        """
        progress = await self.get_user_progress(user_id, path_id)
        
        if not progress:
            # Criar novo progresso se não existir
            progress = await self.create_user_progress(user_id, path_id)
        
        # Atualizar progresso
        if completed_module_id and completed_module_id not in progress.completed_modules:
            progress.completed_modules.append(completed_module_id)
        
        if completed_mission_id and completed_mission_id not in progress.completed_missions:
            progress.completed_missions.append(completed_mission_id)
        
        # Atualizar pontuação total
        progress.total_score += score
        
        # Verificar se a trilha foi completada
        if self._is_path_completed(progress, path_id):
            progress.completed_at = datetime.now(UTC)
        
        # Salvar no repositório
        updated_progress = self.learning_path_repo.update_user_progress(user_id, path_id, progress)
        
        # Invalidar cache
        cache_key = f"user_progress_{user_id}_{path_id}"
        await self.cache.delete(cache_key)
        
        logger.info(f"Progresso atualizado para usuário {user_id} na trilha {path_id}")
        return updated_progress
    
    def _is_path_completed(self, progress: UserPathProgress, path_id: str) -> bool:
        """
        Verifica se o usuário completou a trilha.
        
        Args:
            progress: Progresso do usuário
            path_id: ID da trilha
            
        Returns:
            True se completou, False caso contrário
        """
        # Implementar lógica de verificação de conclusão
        # Por enquanto, retorna False (implementação futura)
        return False
    
    async def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """
        Obtém estatísticas do usuário em learning paths.
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Dicionário com estatísticas
        """
        cache_key = f"user_stats_{user_id}"
        
        # Tentar buscar do cache
        cached_stats = await self.cache.get(cache_key)
        if cached_stats is not None:
            return cached_stats
        
        # Buscar progressos do usuário
        progress_list = self.learning_path_repo.get_user_progress_list(user_id)
        
        stats = {
            "total_paths_started": len(progress_list),
            "total_paths_completed": len([p for p in progress_list if p.completed_at]),
            "total_modules_completed": sum(len(p.completed_modules) for p in progress_list),
            "total_missions_completed": sum(len(p.completed_missions) for p in progress_list),
            "total_score": sum(p.total_score for p in progress_list),
            "average_score": 0
        }
        
        if stats["total_missions_completed"] > 0:
            stats["average_score"] = stats["total_score"] / stats["total_missions_completed"]
        
        # Cache por 10 minutos
        await self.cache.set(cache_key, stats, ttl_seconds=600)
        
        return stats
    
    async def invalidate_user_cache(self, user_id: str) -> None:
        """
        Invalida todo o cache relacionado ao usuário.
        
        Args:
            user_id: ID do usuário
        """
        # Invalidar cache de estatísticas
        stats_cache_key = f"user_stats_{user_id}"
        await self.cache.delete(stats_cache_key)
        
        logger.debug(f"Cache invalidado para usuário {user_id}")

def get_learning_path_progress_service(
    learning_path_repo: LearningPathRepository
) -> LearningPathProgressService:
    """Factory function para criar instância do serviço"""
    return LearningPathProgressService(learning_path_repo)
