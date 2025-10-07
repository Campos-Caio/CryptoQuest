"""
Coletor de métricas automáticas para monitoramento em tempo real.
Coleta métricas de API, negócio, performance e sistema.
"""

import asyncio
import time
import logging
from datetime import datetime, UTC, timedelta
from typing import Dict, Any, List, Optional
from collections import defaultdict, deque
from dataclasses import dataclass, field
from app.core.logging_config import get_cryptoquest_logger, LogCategory
import json
import os

logger = logging.getLogger(__name__)

@dataclass
class APIMetrics:
    """Métricas de API"""
    endpoint: str
    method: str
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    avg_response_time: float = 0.0
    min_response_time: float = float('inf')
    max_response_time: float = 0.0
    response_times: deque = field(default_factory=lambda: deque(maxlen=100))
    last_request: Optional[datetime] = None
    
    @property
    def success_rate(self) -> float:
        return (self.successful_requests / self.total_requests * 100) if self.total_requests > 0 else 0.0
    
    @property
    def error_rate(self) -> float:
        return (self.failed_requests / self.total_requests * 100) if self.total_requests > 0 else 0.0

@dataclass
class BusinessMetrics:
    """Métricas de negócio"""
    missions_completed: int = 0
    learning_paths_completed: int = 0
    badges_awarded: int = 0
    points_distributed: int = 0
    xp_distributed: int = 0
    active_users: set = field(default_factory=set)
    daily_active_users: set = field(default_factory=set)
    user_engagement_score: float = 0.0

@dataclass
class SystemMetrics:
    """Métricas do sistema"""
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    disk_usage_percent: float = 0.0
    log_file_size_mb: float = 0.0
    error_count: int = 0
    warning_count: int = 0
    uptime_seconds: int = 0

class MetricsCollector:
    """
    Coletor centralizado de métricas para monitoramento.
    """
    
    def __init__(self):
        self.cryptoquest_logger = get_cryptoquest_logger()
        self.start_time = datetime.now(UTC)
        
        # Métricas por categoria
        self.api_metrics: Dict[str, APIMetrics] = defaultdict(lambda: APIMetrics("", ""))
        self.business_metrics = BusinessMetrics()
        self.system_metrics = SystemMetrics()
        
        # Configurações
        self.collection_interval = int(os.getenv("METRICS_COLLECTION_INTERVAL", "30"))  # segundos
        self.retention_hours = int(os.getenv("METRICS_RETENTION_HOURS", "24"))
        
        # Histórico de métricas
        self.metrics_history: List[Dict[str, Any]] = []
        
        # Iniciar coleta automática
        self._start_collection_loop()
        
        logger.info("MetricsCollector inicializado")
    
    def _start_collection_loop(self):
        """Inicia loop de coleta automática de métricas"""
        try:
            loop = asyncio.get_running_loop()
            asyncio.create_task(self._collection_loop())
        except RuntimeError:
            # Não há event loop rodando, não iniciar automaticamente
            pass
    
    async def _collection_loop(self):
        """Loop principal de coleta de métricas"""
        while True:
            try:
                await self.collect_all_metrics()
                await asyncio.sleep(self.collection_interval)
            except Exception as e:
                logger.error(f"Erro no loop de coleta de métricas: {e}")
                await asyncio.sleep(self.collection_interval)
    
    async def collect_all_metrics(self):
        """Coleta todas as métricas do sistema"""
        try:
            # Coletar métricas de sistema
            await self._collect_system_metrics()
            
            # Coletar métricas de negócio
            await self._collect_business_metrics()
            
            # Coletar métricas de logs
            await self._collect_log_metrics()
            
            # Salvar métricas no histórico
            await self._save_metrics_to_history()
            
            # Log das métricas coletadas
            self._log_metrics()
            
        except Exception as e:
            logger.error(f"Erro ao coletar métricas: {e}")
    
    async def _collect_system_metrics(self):
        """Coleta métricas do sistema"""
        try:
            import psutil
            
            # Métricas de memória
            memory = psutil.virtual_memory()
            self.system_metrics.memory_usage_mb = memory.used / (1024 * 1024)
            
            # Métricas de CPU
            self.system_metrics.cpu_usage_percent = psutil.cpu_percent(interval=1)
            
            # Métricas de disco
            disk = psutil.disk_usage('/')
            self.system_metrics.disk_usage_percent = (disk.used / disk.total) * 100
            
            # Uptime
            self.system_metrics.uptime_seconds = int((datetime.now(UTC) - self.start_time).total_seconds())
            
        except ImportError:
            # psutil não disponível, usar valores padrão
            self.system_metrics.memory_usage_mb = 0.0
            self.system_metrics.cpu_usage_percent = 0.0
            self.system_metrics.disk_usage_percent = 0.0
        except Exception as e:
            logger.error(f"Erro ao coletar métricas de sistema: {e}")
    
    async def _collect_business_metrics(self):
        """Coleta métricas de negócio dos logs"""
        try:
            # Resetar métricas diárias se necessário
            if datetime.now(UTC).hour == 0 and datetime.now(UTC).minute < 5:
                self.business_metrics.daily_active_users.clear()
            
            # Ler logs de negócio para extrair métricas
            await self._analyze_business_logs()
            
        except Exception as e:
            logger.error(f"Erro ao coletar métricas de negócio: {e}")
    
    async def _analyze_business_logs(self):
        """Analisa logs de negócio para extrair métricas"""
        try:
            business_logs_dir = "logs/business"
            if not os.path.exists(business_logs_dir):
                return
            
            # Analisar logs de eventos
            events_file = os.path.join(business_logs_dir, "events.log")
            if os.path.exists(events_file):
                await self._analyze_events_log(events_file)
            
            # Analisar logs de ações do usuário
            actions_file = os.path.join(business_logs_dir, "user-actions.log")
            if os.path.exists(actions_file):
                await self._analyze_user_actions_log(actions_file)
                
        except Exception as e:
            logger.error(f"Erro ao analisar logs de negócio: {e}")
    
    async def _analyze_events_log(self, file_path: str):
        """Analisa arquivo de eventos de negócio"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        try:
                            data = json.loads(line.strip())
                            message = data.get('message', '')
                            context = data.get('context', {})
                            
                            if 'mission_completion' in message:
                                self.business_metrics.missions_completed += 1
                                if 'points_earned' in context:
                                    self.business_metrics.points_distributed += context.get('points_earned', 0)
                                if 'xp_earned' in context:
                                    self.business_metrics.xp_distributed += context.get('xp_earned', 0)
                            
                            elif 'learning_path_completed' in message:
                                self.business_metrics.learning_paths_completed += 1
                            
                            elif 'badge_awarded' in message:
                                self.business_metrics.badges_awarded += 1
                                
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            logger.error(f"Erro ao analisar log de eventos: {e}")
    
    async def _analyze_user_actions_log(self, file_path: str):
        """Analisa arquivo de ações do usuário"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        try:
                            data = json.loads(line.strip())
                            metadata = data.get('metadata', {})
                            user_id = metadata.get('user_id')
                            
                            if user_id:
                                self.business_metrics.active_users.add(user_id)
                                self.business_metrics.daily_active_users.add(user_id)
                                
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            logger.error(f"Erro ao analisar log de ações do usuário: {e}")
    
    async def _collect_log_metrics(self):
        """Coleta métricas dos arquivos de log"""
        try:
            total_size = 0
            error_count = 0
            warning_count = 0
            
            for root, dirs, files in os.walk("logs"):
                for file in files:
                    if file.endswith('.log'):
                        file_path = os.path.join(root, file)
                        file_size = os.path.getsize(file_path)
                        total_size += file_size
                        
                        # Contar erros e warnings
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                for line in f:
                                    if '"level":"ERROR"' in line:
                                        error_count += 1
                                    elif '"level":"WARNING"' in line:
                                        warning_count += 1
                        except Exception:
                            continue
            
            self.system_metrics.log_file_size_mb = total_size / (1024 * 1024)
            self.system_metrics.error_count = error_count
            self.system_metrics.warning_count = warning_count
            
        except Exception as e:
            logger.error(f"Erro ao coletar métricas de logs: {e}")
    
    def record_api_request(self, endpoint: str, method: str, status_code: int, duration_ms: float):
        """Registra uma requisição de API"""
        try:
            key = f"{method} {endpoint}"
            metrics = self.api_metrics[key]
            
            if metrics.endpoint == "":
                metrics.endpoint = endpoint
                metrics.method = method
            
            metrics.total_requests += 1
            metrics.last_request = datetime.now(UTC)
            
            if 200 <= status_code < 400:
                metrics.successful_requests += 1
            else:
                metrics.failed_requests += 1
            
            # Atualizar tempos de resposta
            metrics.response_times.append(duration_ms)
            metrics.min_response_time = min(metrics.min_response_time, duration_ms)
            metrics.max_response_time = max(metrics.max_response_time, duration_ms)
            
            # Calcular média móvel
            metrics.avg_response_time = sum(metrics.response_times) / len(metrics.response_times)
            
        except Exception as e:
            logger.error(f"Erro ao registrar requisição de API: {e}")
    
    async def _save_metrics_to_history(self):
        """Salva métricas no histórico"""
        try:
            timestamp = datetime.now(UTC)
            
            metrics_snapshot = {
                "timestamp": timestamp.isoformat(),
                "api_metrics": {
                    endpoint: {
                        "total_requests": m.total_requests,
                        "success_rate": m.success_rate,
                        "error_rate": m.error_rate,
                        "avg_response_time": m.avg_response_time,
                        "min_response_time": m.min_response_time if m.min_response_time != float('inf') else 0,
                        "max_response_time": m.max_response_time
                    }
                    for endpoint, m in self.api_metrics.items()
                },
                "business_metrics": {
                    "missions_completed": self.business_metrics.missions_completed,
                    "learning_paths_completed": self.business_metrics.learning_paths_completed,
                    "badges_awarded": self.business_metrics.badges_awarded,
                    "points_distributed": self.business_metrics.points_distributed,
                    "xp_distributed": self.business_metrics.xp_distributed,
                    "active_users_count": len(self.business_metrics.active_users),
                    "daily_active_users_count": len(self.business_metrics.daily_active_users)
                },
                "system_metrics": {
                    "memory_usage_mb": self.system_metrics.memory_usage_mb,
                    "cpu_usage_percent": self.system_metrics.cpu_usage_percent,
                    "disk_usage_percent": self.system_metrics.disk_usage_percent,
                    "log_file_size_mb": self.system_metrics.log_file_size_mb,
                    "error_count": self.system_metrics.error_count,
                    "warning_count": self.system_metrics.warning_count,
                    "uptime_seconds": self.system_metrics.uptime_seconds
                }
            }
            
            self.metrics_history.append(metrics_snapshot)
            
            # Limitar histórico
            cutoff_time = timestamp - timedelta(hours=self.retention_hours)
            self.metrics_history = [
                m for m in self.metrics_history 
                if datetime.fromisoformat(m["timestamp"]) > cutoff_time
            ]
            
        except Exception as e:
            logger.error(f"Erro ao salvar métricas no histórico: {e}")
    
    def _log_metrics(self):
        """Log das métricas coletadas"""
        try:
            # Log de métricas de sistema
            self.cryptoquest_logger.log_system_event(
                "metrics_collected",
                details={
                    "memory_mb": self.system_metrics.memory_usage_mb,
                    "cpu_percent": self.system_metrics.cpu_usage_percent,
                    "disk_percent": self.system_metrics.disk_usage_percent,
                    "log_size_mb": self.system_metrics.log_file_size_mb,
                    "errors": self.system_metrics.error_count,
                    "warnings": self.system_metrics.warning_count,
                    "uptime_hours": self.system_metrics.uptime_seconds / 3600
                }
            )
            
            # Log de métricas de negócio
            self.cryptoquest_logger.log_business_event(
                "business_metrics_summary",
                {
                    "missions_completed": self.business_metrics.missions_completed,
                    "learning_paths_completed": self.business_metrics.learning_paths_completed,
                    "badges_awarded": self.business_metrics.badges_awarded,
                    "points_distributed": self.business_metrics.points_distributed,
                    "active_users": len(self.business_metrics.active_users),
                    "daily_active_users": len(self.business_metrics.daily_active_users)
                }
            )
            
        except Exception as e:
            logger.error(f"Erro ao logar métricas: {e}")
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Retorna métricas atuais"""
        return {
            "timestamp": datetime.now(UTC).isoformat(),
            "api_metrics": {
                endpoint: {
                    "total_requests": m.total_requests,
                    "success_rate": m.success_rate,
                    "error_rate": m.error_rate,
                    "avg_response_time": m.avg_response_time,
                    "min_response_time": m.min_response_time if m.min_response_time != float('inf') else 0,
                    "max_response_time": m.max_response_time,
                    "last_request": m.last_request.isoformat() if m.last_request else None
                }
                for endpoint, m in self.api_metrics.items()
            },
            "business_metrics": {
                "missions_completed": self.business_metrics.missions_completed,
                "learning_paths_completed": self.business_metrics.learning_paths_completed,
                "badges_awarded": self.business_metrics.badges_awarded,
                "points_distributed": self.business_metrics.points_distributed,
                "xp_distributed": self.business_metrics.xp_distributed,
                "active_users_count": len(self.business_metrics.active_users),
                "daily_active_users_count": len(self.business_metrics.daily_active_users)
            },
            "system_metrics": {
                "memory_usage_mb": self.system_metrics.memory_usage_mb,
                "cpu_usage_percent": self.system_metrics.cpu_usage_percent,
                "disk_usage_percent": self.system_metrics.disk_usage_percent,
                "log_file_size_mb": self.system_metrics.log_file_size_mb,
                "error_count": self.system_metrics.error_count,
                "warning_count": self.system_metrics.warning_count,
                "uptime_seconds": self.system_metrics.uptime_seconds
            }
        }
    
    def get_metrics_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Retorna histórico de métricas"""
        cutoff_time = datetime.now(UTC) - timedelta(hours=hours)
        return [
            m for m in self.metrics_history 
            if datetime.fromisoformat(m["timestamp"]) > cutoff_time
        ]

# Instância global
_metrics_collector = None

def get_metrics_collector() -> MetricsCollector:
    """Retorna a instância global do coletor de métricas"""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector
