"""
Serviço de cache em memória para otimização de performance.
Implementa cache simples sem dependências externas.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, UTC, timedelta
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class CacheEntry:
    """Entrada do cache com metadados"""
    value: Any
    created_at: datetime
    ttl_seconds: int
    
    def is_expired(self) -> bool:
        """Verifica se a entrada expirou"""
        return datetime.now(UTC) > (self.created_at + timedelta(seconds=self.ttl_seconds))

class CacheService:
    """
    Serviço de cache em memória com TTL (Time To Live).
    
    Características:
    - Cache thread-safe para operações assíncronas
    - TTL configurável por entrada
    - Limpeza automática de entradas expiradas
    - Métricas de cache hit/miss
    """
    
    def __init__(self, default_ttl: int = 300):  # 5 minutos padrão
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = asyncio.Lock()
        self._default_ttl = default_ttl
        self._stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0
        }
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Recupera um valor do cache.
        
        Args:
            key: Chave do cache
            
        Returns:
            Valor armazenado ou None se não encontrado/expirado
        """
        async with self._lock:
            if key not in self._cache:
                self._stats["misses"] += 1
                logger.debug(f"Cache miss: {key}")
                return None
            
            entry = self._cache[key]
            if entry.is_expired():
                del self._cache[key]
                self._stats["misses"] += 1
                logger.debug(f"Cache expired: {key}")
                return None
            
            self._stats["hits"] += 1
            logger.debug(f"Cache hit: {key}")
            return entry.value
    
    async def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        """
        Armazena um valor no cache.
        
        Args:
            key: Chave do cache
            value: Valor a ser armazenado
            ttl_seconds: TTL em segundos (usa padrão se None)
        """
        async with self._lock:
            ttl = ttl_seconds or self._default_ttl
            self._cache[key] = CacheEntry(
                value=value,
                created_at=datetime.now(UTC),
                ttl_seconds=ttl
            )
            self._stats["sets"] += 1
            logger.debug(f"Cache set: {key} (TTL: {ttl}s)")
    
    async def delete(self, key: str) -> bool:
        """
        Remove uma entrada do cache.
        
        Args:
            key: Chave do cache
            
        Returns:
            True se a entrada foi removida, False se não existia
        """
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                self._stats["deletes"] += 1
                logger.debug(f"Cache delete: {key}")
                return True
            return False
    
    async def clear(self) -> None:
        """Limpa todo o cache"""
        async with self._lock:
            self._cache.clear()
            logger.info("Cache cleared")
    
    async def cleanup_expired(self) -> int:
        """
        Remove entradas expiradas do cache.
        
        Returns:
            Número de entradas removidas
        """
        async with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items()
                if entry.is_expired()
            ]
            
            for key in expired_keys:
                del self._cache[key]
            
            if expired_keys:
                logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
            
            return len(expired_keys)
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas do cache.
        
        Returns:
            Dicionário com estatísticas de uso
        """
        async with self._lock:
            total_requests = self._stats["hits"] + self._stats["misses"]
            hit_rate = (self._stats["hits"] / total_requests * 100) if total_requests > 0 else 0
            
            return {
                "entries_count": len(self._cache),
                "hits": self._stats["hits"],
                "misses": self._stats["misses"],
                "hit_rate": round(hit_rate, 2),
                "sets": self._stats["sets"],
                "deletes": self._stats["deletes"],
                "total_requests": total_requests
            }
    
    async def get_cache_info(self) -> Dict[str, Any]:
        """
        Retorna informações detalhadas do cache.
        
        Returns:
            Dicionário com informações de cada entrada
        """
        async with self._lock:
            now = datetime.now(UTC)
            info = {}
            
            for key, entry in self._cache.items():
                expires_at = entry.created_at + timedelta(seconds=entry.ttl_seconds)
                remaining_ttl = (expires_at - now).total_seconds()
                
                info[key] = {
                    "created_at": entry.created_at.isoformat(),
                    "ttl_seconds": entry.ttl_seconds,
                    "expires_at": expires_at.isoformat(),
                    "remaining_ttl": max(0, remaining_ttl),
                    "is_expired": entry.is_expired()
                }
            
            return info

# Instância global do cache
_cache_service = None

def get_cache_service() -> CacheService:
    """Retorna a instância global do serviço de cache"""
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService()
    return _cache_service
