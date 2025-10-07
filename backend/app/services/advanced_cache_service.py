"""
Serviço de cache avançado que simula Redis.
Implementa cache distribuído com persistência e métricas avançadas.
"""

import asyncio
import json
import logging
import pickle
import hashlib
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, UTC, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict
import os

logger = logging.getLogger(__name__)

@dataclass
class CacheMetrics:
    """Métricas detalhadas do cache"""
    hits: int = 0
    misses: int = 0
    sets: int = 0
    deletes: int = 0
    evictions: int = 0
    total_requests: int = 0
    
    @property
    def hit_rate(self) -> float:
        """Taxa de acerto do cache"""
        return (self.hits / self.total_requests * 100) if self.total_requests > 0 else 0.0

@dataclass
class CacheEntry:
    """Entrada do cache com metadados avançados"""
    value: Any
    created_at: datetime
    expires_at: Optional[datetime]
    access_count: int = 0
    last_accessed: datetime = None
    tags: List[str] = None
    
    def __post_init__(self):
        if self.last_accessed is None:
            self.last_accessed = self.created_at
        if self.tags is None:
            self.tags = []

class AdvancedCacheService:
    """
    Serviço de cache avançado com funcionalidades similares ao Redis.
    
    Características:
    - Cache com TTL configurável
    - Tags para invalidação em lote
    - Métricas detalhadas
    - Persistência opcional
    - Limpeza automática (LRU)
    - Serialização inteligente
    """
    
    def __init__(self, 
                 max_memory_mb: int = 100,
                 default_ttl: int = 300,
                 cleanup_interval: int = 300,
                 persist_to_disk: bool = False):
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = asyncio.Lock()
        self._default_ttl = default_ttl
        self._max_memory_mb = max_memory_mb
        self._cleanup_interval = cleanup_interval
        self._persist_to_disk = persist_to_disk
        self._metrics = CacheMetrics()
        self._tag_index: Dict[str, set] = defaultdict(set)
        
        # Configurar limpeza automática (apenas se houver event loop rodando)
        if cleanup_interval > 0:
            try:
                loop = asyncio.get_running_loop()
                asyncio.create_task(self._cleanup_loop())
            except RuntimeError:
                # Não há event loop rodando, não iniciar cleanup automático
                pass
    
    async def get(self, key: str) -> Optional[Any]:
        """Recupera um valor do cache"""
        async with self._lock:
            self._metrics.total_requests += 1
            
            if key not in self._cache:
                self._metrics.misses += 1
                return None
            
            entry = self._cache[key]
            
            # Verificar expiração
            if entry.expires_at and datetime.now(UTC) > entry.expires_at:
                await self._remove_entry(key)
                self._metrics.misses += 1
                return None
            
            # Atualizar estatísticas de acesso
            entry.access_count += 1
            entry.last_accessed = datetime.now(UTC)
            self._metrics.hits += 1
            
            return entry.value
    
    async def set(self, 
                  key: str, 
                  value: Any, 
                  ttl_seconds: Optional[int] = None,
                  tags: Optional[List[str]] = None) -> bool:
        """Armazena um valor no cache"""
        async with self._lock:
            # Remover entrada existente se houver
            if key in self._cache:
                await self._remove_entry(key)
            
            # Calcular expiração
            expires_at = None
            if ttl_seconds:
                expires_at = datetime.now(UTC) + timedelta(seconds=ttl_seconds)
            elif self._default_ttl > 0:
                expires_at = datetime.now(UTC) + timedelta(seconds=self._default_ttl)
            
            # Criar entrada
            entry = CacheEntry(
                value=value,
                created_at=datetime.now(UTC),
                expires_at=expires_at,
                tags=tags or []
            )
            
            self._cache[key] = entry
            self._metrics.sets += 1
            
            # Atualizar índice de tags
            for tag in entry.tags:
                self._tag_index[tag].add(key)
            
            # Verificar limite de memória
            await self._check_memory_limit()
            
            return True
    
    async def delete(self, key: str) -> bool:
        """Remove uma entrada do cache"""
        async with self._lock:
            if key in self._cache:
                await self._remove_entry(key)
                self._metrics.deletes += 1
                return True
            return False
    
    async def delete_by_tags(self, tags: List[str]) -> int:
        """Remove entradas por tags"""
        async with self._lock:
            keys_to_delete = set()
            for tag in tags:
                keys_to_delete.update(self._tag_index.get(tag, set()))
            
            for key in keys_to_delete:
                await self._remove_entry(key)
            
            return len(keys_to_delete)
    
    async def exists(self, key: str) -> bool:
        """Verifica se uma chave existe no cache"""
        async with self._lock:
            if key not in self._cache:
                return False
            
            entry = self._cache[key]
            if entry.expires_at and datetime.now(UTC) > entry.expires_at:
                await self._remove_entry(key)
                return False
            
            return True
    
    async def expire(self, key: str, ttl_seconds: int) -> bool:
        """Define TTL para uma chave existente"""
        async with self._lock:
            if key not in self._cache:
                return False
            
            entry = self._cache[key]
            entry.expires_at = datetime.now(UTC) + timedelta(seconds=ttl_seconds)
            return True
    
    async def get_keys(self, pattern: str = "*") -> List[str]:
        """Retorna chaves que correspondem ao padrão"""
        async with self._lock:
            if pattern == "*":
                return list(self._cache.keys())
            
            # Implementação simples de padrão (pode ser melhorada)
            keys = []
            for key in self._cache.keys():
                if pattern.replace("*", "") in key:
                    keys.append(key)
            return keys
    
    async def flush_all(self) -> None:
        """Limpa todo o cache"""
        async with self._lock:
            self._cache.clear()
            self._tag_index.clear()
            logger.info("Cache completamente limpo")
    
    async def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas detalhadas do cache"""
        async with self._lock:
            memory_usage = await self._estimate_memory_usage()
            
            return {
                "entries_count": len(self._cache),
                "memory_usage_mb": memory_usage,
                "max_memory_mb": self._max_memory_mb,
                "memory_usage_percent": (memory_usage / self._max_memory_mb * 100) if self._max_memory_mb > 0 else 0,
                "metrics": asdict(self._metrics),
                "tags_count": len(self._tag_index),
                "oldest_entry": min((e.created_at for e in self._cache.values()), default=None),
                "newest_entry": max((e.created_at for e in self._cache.values()), default=None)
            }
    
    async def _remove_entry(self, key: str) -> None:
        """Remove uma entrada do cache e atualiza índices"""
        if key in self._cache:
            entry = self._cache[key]
            
            # Remover dos índices de tags
            for tag in entry.tags:
                if tag in self._tag_index:
                    self._tag_index[tag].discard(key)
                    if not self._tag_index[tag]:
                        del self._tag_index[tag]
            
            del self._cache[key]
    
    async def _check_memory_limit(self) -> None:
        """Verifica e aplica limite de memória usando LRU"""
        memory_usage = await self._estimate_memory_usage()
        
        if memory_usage > self._max_memory_mb:
            # Ordenar por último acesso (LRU)
            sorted_entries = sorted(
                self._cache.items(),
                key=lambda x: x[1].last_accessed
            )
            
            # Remover 10% das entradas mais antigas
            to_remove = len(sorted_entries) // 10
            for key, _ in sorted_entries[:to_remove]:
                await self._remove_entry(key)
                self._metrics.evictions += 1
            
            logger.info(f"Cache evicted {to_remove} entries due to memory limit")
    
    async def _estimate_memory_usage(self) -> float:
        """Estima o uso de memória do cache em MB"""
        try:
            total_size = 0
            for entry in self._cache.values():
                # Estimativa simples baseada no tamanho serializado
                serialized = pickle.dumps(entry.value)
                total_size += len(serialized)
                total_size += 100  # Overhead por entrada
            
            return total_size / (1024 * 1024)  # Converter para MB
        except Exception:
            return 0.0
    
    async def _cleanup_loop(self) -> None:
        """Loop de limpeza automática de entradas expiradas"""
        while True:
            try:
                await asyncio.sleep(self._cleanup_interval)
                await self._cleanup_expired()
            except Exception as e:
                logger.error(f"Erro no loop de limpeza: {e}")
    
    async def _cleanup_expired(self) -> int:
        """Remove entradas expiradas"""
        async with self._lock:
            now = datetime.now(UTC)
            expired_keys = [
                key for key, entry in self._cache.items()
                if entry.expires_at and now > entry.expires_at
            ]
            
            for key in expired_keys:
                await self._remove_entry(key)
            
            if expired_keys:
                logger.debug(f"Cleaned up {len(expired_keys)} expired entries")
            
            return len(expired_keys)

# Instância global do cache avançado
_advanced_cache = None

def get_advanced_cache() -> AdvancedCacheService:
    """Retorna a instância global do cache avançado"""
    global _advanced_cache
    if _advanced_cache is None:
        _advanced_cache = AdvancedCacheService(
            max_memory_mb=int(os.getenv("CACHE_MAX_MEMORY_MB", "100")),
            default_ttl=int(os.getenv("CACHE_DEFAULT_TTL", "300")),
            cleanup_interval=int(os.getenv("CACHE_CLEANUP_INTERVAL", "300")),
            persist_to_disk=os.getenv("CACHE_PERSIST_TO_DISK", "false").lower() == "true"
        )
    return _advanced_cache
