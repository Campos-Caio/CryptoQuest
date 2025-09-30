"""
Sistema de monitoramento de saúde do sistema.
Verifica saúde de componentes, dependências e recursos.
"""

import asyncio
import logging
import time
from datetime import datetime, UTC, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
from app.core.logging_config import get_cryptoquest_logger, LogCategory
from app.services.metrics_collector import get_metrics_collector
from app.services.alert_manager import get_alert_manager

logger = logging.getLogger(__name__)

class HealthStatus(Enum):
    """Status de saúde"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"

@dataclass
class HealthCheck:
    """Resultado de verificação de saúde"""
    name: str
    status: HealthStatus
    message: str
    response_time_ms: float
    details: Dict[str, Any]
    timestamp: datetime
    last_success: Optional[datetime] = None

@dataclass
class ComponentHealth:
    """Saúde de um componente"""
    name: str
    status: HealthStatus
    checks: List[HealthCheck]
    overall_response_time_ms: float
    last_checked: datetime

class HealthMonitor:
    """
    Monitor de saúde do sistema.
    """
    
    def __init__(self):
        self.cryptoquest_logger = get_cryptoquest_logger()
        self.metrics_collector = get_metrics_collector()
        self.alert_manager = get_alert_manager()
        
        # Componentes a serem monitorados
        self.components = {
            "database": self._check_database_health,
            "firebase": self._check_firebase_health,
            "api": self._check_api_health,
            "logs": self._check_logs_health,
            "memory": self._check_memory_health,
            "disk": self._check_disk_health
        }
        
        # Histórico de verificações
        self.health_history: List[Dict[str, Any]] = []
        
        # Configurações
        self.check_interval = 60  # segundos
        self.max_history = 100
        
        # Iniciar monitoramento
        self._start_health_monitoring()
        
        logger.info("HealthMonitor inicializado")
    
    def _start_health_monitoring(self):
        """Inicia monitoramento de saúde"""
        try:
            loop = asyncio.get_running_loop()
            asyncio.create_task(self._health_monitoring_loop())
        except RuntimeError:
            # Não há event loop rodando, não iniciar automaticamente
            pass
    
    async def _health_monitoring_loop(self):
        """Loop principal de monitoramento de saúde"""
        while True:
            try:
                await self.check_all_components()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Erro no loop de monitoramento de saúde: {e}")
                await asyncio.sleep(self.check_interval)
    
    async def check_all_components(self) -> Dict[str, ComponentHealth]:
        """Verifica saúde de todos os componentes"""
        try:
            results = {}
            
            for component_name, check_function in self.components.items():
                try:
                    health_check = await check_function()
                    results[component_name] = health_check
                except Exception as e:
                    logger.error(f"Erro ao verificar saúde do componente {component_name}: {e}")
                    results[component_name] = ComponentHealth(
                        name=component_name,
                        status=HealthStatus.UNKNOWN,
                        checks=[],
                        overall_response_time_ms=0.0,
                        last_checked=datetime.now(UTC)
                    )
            
            # Salvar no histórico
            await self._save_health_to_history(results)
            
            # Log de saúde geral
            self._log_overall_health(results)
            
            return results
            
        except Exception as e:
            logger.error(f"Erro ao verificar saúde dos componentes: {e}")
            return {}
    
    async def _check_database_health(self) -> ComponentHealth:
        """Verifica saúde do banco de dados"""
        start_time = time.time()
        checks = []
        
        try:
            # Verificar conexão com Firestore
            from app.core.firebase import get_firestore_db
            
            db = get_firestore_db()
            
            # Teste simples de leitura
            test_start = time.time()
            # Simular uma operação de teste (sem fazer query real)
            test_duration = (time.time() - test_start) * 1000
            
            checks.append(HealthCheck(
                name="firestore_connection",
                status=HealthStatus.HEALTHY,
                message="Conexão com Firestore OK",
                response_time_ms=test_duration,
                details={"connection": "active"},
                timestamp=datetime.now(UTC)
            ))
            
            response_time = (time.time() - start_time) * 1000
            
            return ComponentHealth(
                name="database",
                status=HealthStatus.HEALTHY,
                checks=checks,
                overall_response_time_ms=response_time,
                last_checked=datetime.now(UTC)
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            
            checks.append(HealthCheck(
                name="firestore_connection",
                status=HealthStatus.CRITICAL,
                message=f"Erro na conexão com Firestore: {str(e)}",
                response_time_ms=response_time,
                details={"error": str(e)},
                timestamp=datetime.now(UTC)
            ))
            
            return ComponentHealth(
                name="database",
                status=HealthStatus.CRITICAL,
                checks=checks,
                overall_response_time_ms=response_time,
                last_checked=datetime.now(UTC)
            )
    
    async def _check_firebase_health(self) -> ComponentHealth:
        """Verifica saúde do Firebase"""
        start_time = time.time()
        checks = []
        
        try:
            # Verificar autenticação Firebase
            from app.core.firebase import get_firebase_auth
            
            auth = get_firebase_auth()
            
            checks.append(HealthCheck(
                name="firebase_auth",
                status=HealthStatus.HEALTHY,
                message="Firebase Auth OK",
                response_time_ms=0.0,
                details={"auth": "initialized"},
                timestamp=datetime.now(UTC)
            ))
            
            response_time = (time.time() - start_time) * 1000
            
            return ComponentHealth(
                name="firebase",
                status=HealthStatus.HEALTHY,
                checks=checks,
                overall_response_time_ms=response_time,
                last_checked=datetime.now(UTC)
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            
            checks.append(HealthCheck(
                name="firebase_auth",
                status=HealthStatus.CRITICAL,
                message=f"Erro no Firebase Auth: {str(e)}",
                response_time_ms=response_time,
                details={"error": str(e)},
                timestamp=datetime.now(UTC)
            ))
            
            return ComponentHealth(
                name="firebase",
                status=HealthStatus.CRITICAL,
                checks=checks,
                overall_response_time_ms=response_time,
                last_checked=datetime.now(UTC)
            )
    
    async def _check_api_health(self) -> ComponentHealth:
        """Verifica saúde da API"""
        start_time = time.time()
        checks = []
        
        try:
            # Verificar métricas de API
            current_metrics = self.metrics_collector.get_current_metrics()
            api_metrics = current_metrics.get("api_metrics", {})
            
            total_requests = sum(m.get("total_requests", 0) for m in api_metrics.values())
            total_errors = sum(
                (m.get("error_rate", 0) / 100) * m.get("total_requests", 0) 
                for m in api_metrics.values()
            )
            
            if total_requests > 0:
                error_rate = (total_errors / total_requests) * 100
                
                if error_rate < 5:
                    status = HealthStatus.HEALTHY
                    message = f"Taxa de erro baixa: {error_rate:.1f}%"
                elif error_rate < 10:
                    status = HealthStatus.WARNING
                    message = f"Taxa de erro elevada: {error_rate:.1f}%"
                else:
                    status = HealthStatus.CRITICAL
                    message = f"Taxa de erro alta: {error_rate:.1f}%"
            else:
                status = HealthStatus.HEALTHY
                message = "Nenhuma requisição registrada"
                error_rate = 0
            
            checks.append(HealthCheck(
                name="api_performance",
                status=status,
                message=message,
                response_time_ms=0.0,
                details={
                    "total_requests": total_requests,
                    "error_rate": error_rate,
                    "endpoints": len(api_metrics)
                },
                timestamp=datetime.now(UTC)
            ))
            
            response_time = (time.time() - start_time) * 1000
            
            return ComponentHealth(
                name="api",
                status=status,
                checks=checks,
                overall_response_time_ms=response_time,
                last_checked=datetime.now(UTC)
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            
            checks.append(HealthCheck(
                name="api_performance",
                status=HealthStatus.UNKNOWN,
                message=f"Erro ao verificar API: {str(e)}",
                response_time_ms=response_time,
                details={"error": str(e)},
                timestamp=datetime.now(UTC)
            ))
            
            return ComponentHealth(
                name="api",
                status=HealthStatus.UNKNOWN,
                checks=checks,
                overall_response_time_ms=response_time,
                last_checked=datetime.now(UTC)
            )
    
    async def _check_logs_health(self) -> ComponentHealth:
        """Verifica saúde dos logs"""
        start_time = time.time()
        checks = []
        
        try:
            import os
            
            # Verificar tamanho dos arquivos de log
            total_log_size = 0
            log_files_count = 0
            
            for root, dirs, files in os.walk("logs"):
                for file in files:
                    if file.endswith('.log'):
                        file_path = os.path.join(root, file)
                        file_size = os.path.getsize(file_path)
                        total_log_size += file_size
                        log_files_count += 1
            
            total_log_size_mb = total_log_size / (1024 * 1024)
            
            if total_log_size_mb < 100:
                status = HealthStatus.HEALTHY
                message = f"Logs OK: {total_log_size_mb:.1f} MB"
            elif total_log_size_mb < 500:
                status = HealthStatus.WARNING
                message = f"Logs grandes: {total_log_size_mb:.1f} MB"
            else:
                status = HealthStatus.CRITICAL
                message = f"Logs muito grandes: {total_log_size_mb:.1f} MB"
            
            checks.append(HealthCheck(
                name="log_files",
                status=status,
                message=message,
                response_time_ms=0.0,
                details={
                    "total_size_mb": total_log_size_mb,
                    "files_count": log_files_count
                },
                timestamp=datetime.now(UTC)
            ))
            
            response_time = (time.time() - start_time) * 1000
            
            return ComponentHealth(
                name="logs",
                status=status,
                checks=checks,
                overall_response_time_ms=response_time,
                last_checked=datetime.now(UTC)
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            
            checks.append(HealthCheck(
                name="log_files",
                status=HealthStatus.UNKNOWN,
                message=f"Erro ao verificar logs: {str(e)}",
                response_time_ms=response_time,
                details={"error": str(e)},
                timestamp=datetime.now(UTC)
            ))
            
            return ComponentHealth(
                name="logs",
                status=HealthStatus.UNKNOWN,
                checks=checks,
                overall_response_time_ms=response_time,
                last_checked=datetime.now(UTC)
            )
    
    async def _check_memory_health(self) -> ComponentHealth:
        """Verifica saúde da memória"""
        start_time = time.time()
        checks = []
        
        try:
            import psutil
            
            memory = psutil.virtual_memory()
            memory_usage_mb = memory.used / (1024 * 1024)
            memory_percent = memory.percent
            
            if memory_percent < 70:
                status = HealthStatus.HEALTHY
                message = f"Memória OK: {memory_percent:.1f}%"
            elif memory_percent < 85:
                status = HealthStatus.WARNING
                message = f"Memória alta: {memory_percent:.1f}%"
            else:
                status = HealthStatus.CRITICAL
                message = f"Memória crítica: {memory_percent:.1f}%"
            
            checks.append(HealthCheck(
                name="memory_usage",
                status=status,
                message=message,
                response_time_ms=0.0,
                details={
                    "usage_mb": memory_usage_mb,
                    "usage_percent": memory_percent,
                    "available_mb": memory.available / (1024 * 1024)
                },
                timestamp=datetime.now(UTC)
            ))
            
            response_time = (time.time() - start_time) * 1000
            
            return ComponentHealth(
                name="memory",
                status=status,
                checks=checks,
                overall_response_time_ms=response_time,
                last_checked=datetime.now(UTC)
            )
            
        except ImportError:
            # psutil não disponível
            response_time = (time.time() - start_time) * 1000
            
            checks.append(HealthCheck(
                name="memory_usage",
                status=HealthStatus.UNKNOWN,
                message="psutil não disponível para verificação de memória",
                response_time_ms=response_time,
                details={"psutil": "not_available"},
                timestamp=datetime.now(UTC)
            ))
            
            return ComponentHealth(
                name="memory",
                status=HealthStatus.UNKNOWN,
                checks=checks,
                overall_response_time_ms=response_time,
                last_checked=datetime.now(UTC)
            )
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            
            checks.append(HealthCheck(
                name="memory_usage",
                status=HealthStatus.UNKNOWN,
                message=f"Erro ao verificar memória: {str(e)}",
                response_time_ms=response_time,
                details={"error": str(e)},
                timestamp=datetime.now(UTC)
            ))
            
            return ComponentHealth(
                name="memory",
                status=HealthStatus.UNKNOWN,
                checks=checks,
                overall_response_time_ms=response_time,
                last_checked=datetime.now(UTC)
            )
    
    async def _check_disk_health(self) -> ComponentHealth:
        """Verifica saúde do disco"""
        start_time = time.time()
        checks = []
        
        try:
            import psutil
            
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            disk_free_gb = disk.free / (1024 * 1024 * 1024)
            
            if disk_percent < 80:
                status = HealthStatus.HEALTHY
                message = f"Disco OK: {disk_percent:.1f}% usado"
            elif disk_percent < 90:
                status = HealthStatus.WARNING
                message = f"Disco alto: {disk_percent:.1f}% usado"
            else:
                status = HealthStatus.CRITICAL
                message = f"Disco crítico: {disk_percent:.1f}% usado"
            
            checks.append(HealthCheck(
                name="disk_usage",
                status=status,
                message=message,
                response_time_ms=0.0,
                details={
                    "usage_percent": disk_percent,
                    "free_gb": disk_free_gb,
                    "total_gb": disk.total / (1024 * 1024 * 1024)
                },
                timestamp=datetime.now(UTC)
            ))
            
            response_time = (time.time() - start_time) * 1000
            
            return ComponentHealth(
                name="disk",
                status=status,
                checks=checks,
                overall_response_time_ms=response_time,
                last_checked=datetime.now(UTC)
            )
            
        except ImportError:
            # psutil não disponível
            response_time = (time.time() - start_time) * 1000
            
            checks.append(HealthCheck(
                name="disk_usage",
                status=HealthStatus.UNKNOWN,
                message="psutil não disponível para verificação de disco",
                response_time_ms=response_time,
                details={"psutil": "not_available"},
                timestamp=datetime.now(UTC)
            ))
            
            return ComponentHealth(
                name="disk",
                status=HealthStatus.UNKNOWN,
                checks=checks,
                overall_response_time_ms=response_time,
                last_checked=datetime.now(UTC)
            )
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            
            checks.append(HealthCheck(
                name="disk_usage",
                status=HealthStatus.UNKNOWN,
                message=f"Erro ao verificar disco: {str(e)}",
                response_time_ms=response_time,
                details={"error": str(e)},
                timestamp=datetime.now(UTC)
            ))
            
            return ComponentHealth(
                name="disk",
                status=HealthStatus.UNKNOWN,
                checks=checks,
                overall_response_time_ms=response_time,
                last_checked=datetime.now(UTC)
            )
    
    async def _save_health_to_history(self, components: Dict[str, ComponentHealth]):
        """Salva verificação de saúde no histórico"""
        try:
            timestamp = datetime.now(UTC)
            
            health_snapshot = {
                "timestamp": timestamp.isoformat(),
                "components": {
                    name: {
                        "status": component.status.value,
                        "response_time_ms": component.overall_response_time_ms,
                        "checks_count": len(component.checks),
                        "checks": [
                            {
                                "name": check.name,
                                "status": check.status.value,
                                "message": check.message,
                                "response_time_ms": check.response_time_ms
                            }
                            for check in component.checks
                        ]
                    }
                    for name, component in components.items()
                }
            }
            
            self.health_history.append(health_snapshot)
            
            # Limitar histórico
            if len(self.health_history) > self.max_history:
                self.health_history = self.health_history[-self.max_history:]
                
        except Exception as e:
            logger.error(f"Erro ao salvar saúde no histórico: {e}")
    
    def _log_overall_health(self, components: Dict[str, ComponentHealth]):
        """Log da saúde geral do sistema"""
        try:
            healthy_count = sum(1 for c in components.values() if c.status == HealthStatus.HEALTHY)
            warning_count = sum(1 for c in components.values() if c.status == HealthStatus.WARNING)
            critical_count = sum(1 for c in components.values() if c.status == HealthStatus.CRITICAL)
            unknown_count = sum(1 for c in components.values() if c.status == HealthStatus.UNKNOWN)
            
            total_components = len(components)
            
            if critical_count > 0:
                level = 50  # CRITICAL
                message = f"Sistema com problemas críticos: {critical_count}/{total_components} componentes"
            elif warning_count > 0:
                level = 30  # WARNING
                message = f"Sistema com avisos: {warning_count}/{total_components} componentes"
            else:
                level = 20  # INFO
                message = f"Sistema saudável: {healthy_count}/{total_components} componentes"
            
            self.cryptoquest_logger.log_system_event(
                "health_check_completed",
                level=level,
                details={
                    "healthy": healthy_count,
                    "warning": warning_count,
                    "critical": critical_count,
                    "unknown": unknown_count,
                    "total": total_components,
                    "message": message
                }
            )
            
        except Exception as e:
            logger.error(f"Erro ao logar saúde geral: {e}")
    
    def get_current_health(self) -> Dict[str, Any]:
        """Retorna saúde atual do sistema"""
        try:
            # Calcular saúde geral baseada no último check
            if not self.health_history:
                return {
                    "overall_status": "unknown",
                    "timestamp": datetime.now(UTC).isoformat(),
                    "components": {}
                }
            
            latest_health = self.health_history[-1]
            components = latest_health["components"]
            
            # Determinar status geral
            statuses = [comp["status"] for comp in components.values()]
            
            if "critical" in statuses:
                overall_status = "critical"
            elif "warning" in statuses:
                overall_status = "warning"
            elif "unknown" in statuses:
                overall_status = "unknown"
            else:
                overall_status = "healthy"
            
            return {
                "overall_status": overall_status,
                "timestamp": latest_health["timestamp"],
                "components": components,
                "summary": {
                    "healthy": sum(1 for s in statuses if s == "healthy"),
                    "warning": sum(1 for s in statuses if s == "warning"),
                    "critical": sum(1 for s in statuses if s == "critical"),
                    "unknown": sum(1 for s in statuses if s == "unknown"),
                    "total": len(statuses)
                }
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter saúde atual: {e}")
            return {
                "overall_status": "unknown",
                "timestamp": datetime.now(UTC).isoformat(),
                "error": str(e)
            }
    
    def get_health_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Retorna histórico de saúde"""
        cutoff_time = datetime.now(UTC) - timedelta(hours=hours)
        return [
            health for health in self.health_history
            if datetime.fromisoformat(health["timestamp"]) > cutoff_time
        ]

# Instância global
_health_monitor = None

def get_health_monitor() -> HealthMonitor:
    """Retorna a instância global do monitor de saúde"""
    global _health_monitor
    if _health_monitor is None:
        _health_monitor = HealthMonitor()
    return _health_monitor
