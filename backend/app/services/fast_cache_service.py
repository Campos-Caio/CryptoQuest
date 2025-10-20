"""
Serviço de cache em memória de alta performance.
Reduz drasticamente queries ao Firestore.
"""
import asyncio
import logging
from typing import Dict, Any, Optional, Callable
from datetime import datetime, UTC, timedelta
import threading
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Entrada de cache com TTL"""
    key: str
    value: Any
    created_at: datetime
    ttl_seconds: int
    hit_count: int = 0
    
    def is_expired(self) -> bool:
        """Verifica se a entrada expirou"""
        age = (datetime.now(UTC) - self.created_at).total_seconds()
        return age > self.ttl_seconds
    
    def get_age(self) -> float:
        """Retorna idade da entrada em segundos"""
        return (datetime.now(UTC) - self.created_at).total_seconds()


class FastCacheService:
    """
    Cache em memória de alta performance com:
    - TTL por entrada
    - Invalidação manual
    - Estatísticas de hit/miss
    - Thread-safe
    """
    
    def __init__(self):
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = threading.Lock()
        
        # Estatísticas
        self.stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "invalidations": 0,
            "expirations": 0
        }
        
        # Worker de limpeza
        self._cleanup_task: Optional[asyncio.Task] = None
        self._running = False
        
        logger.info("🚀 FastCacheService inicializado")
    
    async def start_cleanup_worker(self):
        """Inicia worker que limpa entradas expiradas"""
        if self._running:
            return
        
        self._running = True
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        logger.info("✅ Worker de limpeza de cache iniciado")
    
    async def stop_cleanup_worker(self):
        """Para worker de limpeza"""
        self._running = False
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        logger.info("🛑 Worker de limpeza de cache parado")
    
    async def _cleanup_loop(self):
        """Loop de limpeza periódica"""
        while self._running:
            try:
                await asyncio.sleep(60)  # Limpar a cada 60 segundos
                self._cleanup_expired()
            except Exception as e:
                logger.error(f"Erro no worker de limpeza: {e}")
    
    def _cleanup_expired(self):
        """Remove entradas expiradas"""
        with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items()
                if entry.is_expired()
            ]
            
            for key in expired_keys:
                del self._cache[key]
                self.stats["expirations"] += 1
            
            if expired_keys:
                logger.debug(f"🧹 Removidas {len(expired_keys)} entradas expiradas")
    
    def get(self, key: str) -> Optional[Any]:
        """
        Busca valor no cache.
        
        Args:
            key: Chave de cache
            
        Returns:
            Valor em cache ou None se não existir/expirado
        """
        with self._lock:
            entry = self._cache.get(key)
            
            if entry is None:
                self.stats["misses"] += 1
                return None
            
            if entry.is_expired():
                del self._cache[key]
                self.stats["misses"] += 1
                self.stats["expirations"] += 1
                return None
            
            # Hit!
            entry.hit_count += 1
            self.stats["hits"] += 1
            return entry.value
    
    def set(self, key: str, value: Any, ttl_seconds: int = 300):
        """
        Armazena valor no cache.
        
        Args:
            key: Chave de cache
            value: Valor a armazenar
            ttl_seconds: Tempo de vida em segundos (padrão: 5 min)
        """
        with self._lock:
            self._cache[key] = CacheEntry(
                key=key,
                value=value,
                created_at=datetime.now(UTC),
                ttl_seconds=ttl_seconds
            )
            self.stats["sets"] += 1
    
    async def get_or_fetch(
        self,
        key: str,
        fetch_func: Callable,
        ttl_seconds: int = 300
    ) -> Any:
        """
        Busca do cache ou executa função para obter valor.
        
        Args:
            key: Chave de cache
            fetch_func: Função para buscar valor (async ou sync)
            ttl_seconds: TTL para cache
            
        Returns:
            Valor (do cache ou fetchado)
        """
        # Tentar cache primeiro
        cached_value = self.get(key)
        if cached_value is not None:
            return cached_value
        
        # Cache miss - buscar valor
        if asyncio.iscoroutinefunction(fetch_func):
            value = await fetch_func()
        else:
            value = fetch_func()
        
        # Armazenar no cache
        if value is not None:
            self.set(key, value, ttl_seconds)
        
        return value
    
    def invalidate(self, key: str):
        """Remove entrada específica do cache"""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                self.stats["invalidations"] += 1
    
    def invalidate_pattern(self, pattern: str):
        """Remove todas as entradas que contém o padrão"""
        with self._lock:
            keys_to_remove = [
                key for key in self._cache.keys()
                if pattern in key
            ]
            
            for key in keys_to_remove:
                del self._cache[key]
                self.stats["invalidations"] += 1
            
            if keys_to_remove:
                logger.info(f"🗑️ Invalidadas {len(keys_to_remove)} entradas com padrão '{pattern}'")
    
    def clear(self):
        """Limpa todo o cache"""
        with self._lock:
            count = len(self._cache)
            self._cache.clear()
            logger.info(f"🗑️ Cache limpo: {count} entradas removidas")
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache"""
        with self._lock:
            total_requests = self.stats["hits"] + self.stats["misses"]
            hit_rate = (
                (self.stats["hits"] / total_requests * 100)
                if total_requests > 0 else 0
            )
            
            return {
                **self.stats,
                "cache_size": len(self._cache),
                "total_requests": total_requests,
                "hit_rate_percentage": round(hit_rate, 2)
            }
    
    def get_entry_info(self, key: str) -> Optional[Dict[str, Any]]:
        """Retorna informações sobre uma entrada"""
        with self._lock:
            entry = self._cache.get(key)
            if not entry:
                return None
            
            return {
                "key": entry.key,
                "age_seconds": entry.get_age(),
                "ttl_seconds": entry.ttl_seconds,
                "is_expired": entry.is_expired(),
                "hit_count": entry.hit_count,
                "created_at": entry.created_at.isoformat()
            }


# Instância global
_cache_service_instance: Optional[FastCacheService] = None
_cache_lock = threading.Lock()


def get_fast_cache() -> FastCacheService:
    """Retorna instância singleton do FastCacheService"""
    global _cache_service_instance
    
    if _cache_service_instance is None:
        with _cache_lock:
            if _cache_service_instance is None:
                _cache_service_instance = FastCacheService()
    
    return _cache_service_instance


# Funções de conveniência
def cache_user_profile(user_id: str, profile: Any, ttl: int = 300):
    """Cache profile de usuário (5 min)"""
    get_fast_cache().set(f"user_profile:{user_id}", profile, ttl)


def get_cached_user_profile(user_id: str) -> Optional[Any]:
    """Busca profile de usuário do cache"""
    return get_fast_cache().get(f"user_profile:{user_id}")


def invalidate_user_cache(user_id: str):
    """Invalida todo cache relacionado ao usuário"""
    get_fast_cache().invalidate_pattern(user_id)


def cache_user_badges(user_id: str, badges: Any, ttl: int = 600):
    """Cache badges de usuário (10 min)"""
    get_fast_cache().set(f"user_badges:{user_id}", badges, ttl)


def get_cached_user_badges(user_id: str) -> Optional[Any]:
    """Busca badges de usuário do cache"""
    return get_fast_cache().get(f"user_badges:{user_id}")

