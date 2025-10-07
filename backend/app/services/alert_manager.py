"""
Sistema de alertas inteligentes para monitoramento em tempo real.
Detecta problemas e envia alertas baseados em métricas e padrões.
"""

import asyncio
import logging
from datetime import datetime, UTC, timedelta
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
from app.core.logging_config import get_cryptoquest_logger, LogCategory
from app.services.metrics_collector import get_metrics_collector

logger = logging.getLogger(__name__)

class AlertSeverity(Enum):
    """Severidade dos alertas"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertType(Enum):
    """Tipos de alertas"""
    ERROR_RATE = "error_rate"
    RESPONSE_TIME = "response_time"
    MEMORY_USAGE = "memory_usage"
    CPU_USAGE = "cpu_usage"
    DISK_USAGE = "disk_usage"
    BUSINESS_METRICS = "business_metrics"
    SYSTEM_HEALTH = "system_health"
    SECURITY = "security"

@dataclass
class AlertRule:
    """Regra de alerta"""
    name: str
    alert_type: AlertType
    severity: AlertSeverity
    threshold: float
    condition: str  # 'greater_than', 'less_than', 'equals'
    description: str
    enabled: bool = True
    cooldown_minutes: int = 15  # Tempo mínimo entre alertas do mesmo tipo
    last_triggered: Optional[datetime] = None

@dataclass
class Alert:
    """Alerta disparado"""
    id: str
    rule_name: str
    alert_type: AlertType
    severity: AlertSeverity
    message: str
    details: Dict[str, Any]
    timestamp: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None

class AlertManager:
    """
    Gerenciador de alertas inteligentes.
    """
    
    def __init__(self):
        self.cryptoquest_logger = get_cryptoquest_logger()
        self.metrics_collector = get_metrics_collector()
        
        # Alertas disparados
        self.active_alerts: List[Alert] = []
        self.alert_history: List[Alert] = []
        
        # Regras de alerta
        self.alert_rules = self._initialize_alert_rules()
        
        # Callbacks para notificações
        self.alert_callbacks: List[Callable[[Alert], None]] = []
        
        # Configurações
        self.check_interval = 60  # segundos
        self.max_history = 1000
        
        # Iniciar monitoramento
        self._start_monitoring()
        
        logger.info("AlertManager inicializado")
    
    def _initialize_alert_rules(self) -> Dict[str, AlertRule]:
        """Inicializa regras de alerta padrão"""
        rules = {
            "high_error_rate": AlertRule(
                name="Taxa de Erro Alta",
                alert_type=AlertType.ERROR_RATE,
                severity=AlertSeverity.HIGH,
                threshold=5.0,  # 5%
                condition="greater_than",
                description="Taxa de erro acima de 5%",
                cooldown_minutes=10
            ),
            "slow_response_time": AlertRule(
                name="Tempo de Resposta Lento",
                alert_type=AlertType.RESPONSE_TIME,
                severity=AlertSeverity.MEDIUM,
                threshold=2000.0,  # 2 segundos
                condition="greater_than",
                description="Tempo de resposta médio acima de 2 segundos",
                cooldown_minutes=15
            ),
            "high_memory_usage": AlertRule(
                name="Uso Alto de Memória",
                alert_type=AlertType.MEMORY_USAGE,
                severity=AlertSeverity.HIGH,
                threshold=512.0,  # 512 MB
                condition="greater_than",
                description="Uso de memória acima de 512 MB",
                cooldown_minutes=20
            ),
            "high_cpu_usage": AlertRule(
                name="Uso Alto de CPU",
                alert_type=AlertType.CPU_USAGE,
                severity=AlertSeverity.MEDIUM,
                threshold=80.0,  # 80%
                condition="greater_than",
                description="Uso de CPU acima de 80%",
                cooldown_minutes=15
            ),
            "high_disk_usage": AlertRule(
                name="Uso Alto de Disco",
                alert_type=AlertType.DISK_USAGE,
                severity=AlertSeverity.HIGH,
                threshold=90.0,  # 90%
                condition="greater_than",
                description="Uso de disco acima de 90%",
                cooldown_minutes=30
            ),
            "no_user_activity": AlertRule(
                name="Sem Atividade de Usuários",
                alert_type=AlertType.BUSINESS_METRICS,
                severity=AlertSeverity.LOW,
                threshold=0.0,
                condition="equals",
                description="Nenhuma atividade de usuários nas últimas 2 horas",
                cooldown_minutes=60
            ),
            "excessive_errors": AlertRule(
                name="Excesso de Erros",
                alert_type=AlertType.SYSTEM_HEALTH,
                severity=AlertSeverity.CRITICAL,
                threshold=50.0,
                condition="greater_than",
                description="Mais de 50 erros registrados",
                cooldown_minutes=5
            )
        }
        
        return rules
    
    def _start_monitoring(self):
        """Inicia monitoramento de alertas"""
        try:
            loop = asyncio.get_running_loop()
            asyncio.create_task(self._monitoring_loop())
        except RuntimeError:
            # Não há event loop rodando, não iniciar automaticamente
            pass
    
    async def _monitoring_loop(self):
        """Loop principal de monitoramento"""
        while True:
            try:
                await self.check_all_alerts()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Erro no loop de monitoramento: {e}")
                await asyncio.sleep(self.check_interval)
    
    async def check_all_alerts(self):
        """Verifica todas as regras de alerta"""
        try:
            current_metrics = self.metrics_collector.get_current_metrics()
            
            for rule_name, rule in self.alert_rules.items():
                if not rule.enabled:
                    continue
                
                # Verificar cooldown
                if self._is_in_cooldown(rule):
                    continue
                
                # Verificar condição
                if await self._check_alert_condition(rule, current_metrics):
                    await self._trigger_alert(rule, current_metrics)
                    
        except Exception as e:
            logger.error(f"Erro ao verificar alertas: {e}")
    
    def _is_in_cooldown(self, rule: AlertRule) -> bool:
        """Verifica se a regra está em cooldown"""
        if not rule.last_triggered:
            return False
        
        time_since_last = datetime.now(UTC) - rule.last_triggered
        return time_since_last.total_seconds() < (rule.cooldown_minutes * 60)
    
    async def _check_alert_condition(self, rule: AlertRule, metrics: Dict[str, Any]) -> bool:
        """Verifica se a condição do alerta foi atendida"""
        try:
            if rule.alert_type == AlertType.ERROR_RATE:
                return self._check_error_rate_condition(rule, metrics)
            elif rule.alert_type == AlertType.RESPONSE_TIME:
                return self._check_response_time_condition(rule, metrics)
            elif rule.alert_type == AlertType.MEMORY_USAGE:
                return self._check_memory_usage_condition(rule, metrics)
            elif rule.alert_type == AlertType.CPU_USAGE:
                return self._check_cpu_usage_condition(rule, metrics)
            elif rule.alert_type == AlertType.DISK_USAGE:
                return self._check_disk_usage_condition(rule, metrics)
            elif rule.alert_type == AlertType.BUSINESS_METRICS:
                return await self._check_business_metrics_condition(rule, metrics)
            elif rule.alert_type == AlertType.SYSTEM_HEALTH:
                return self._check_system_health_condition(rule, metrics)
            
            return False
            
        except Exception as e:
            logger.error(f"Erro ao verificar condição do alerta {rule.name}: {e}")
            return False
    
    def _check_error_rate_condition(self, rule: AlertRule, metrics: Dict[str, Any]) -> bool:
        """Verifica condição de taxa de erro"""
        api_metrics = metrics.get("api_metrics", {})
        for endpoint, endpoint_metrics in api_metrics.items():
            error_rate = endpoint_metrics.get("error_rate", 0)
            if self._evaluate_condition(error_rate, rule.threshold, rule.condition):
                return True
        return False
    
    def _check_response_time_condition(self, rule: AlertRule, metrics: Dict[str, Any]) -> bool:
        """Verifica condição de tempo de resposta"""
        api_metrics = metrics.get("api_metrics", {})
        for endpoint, endpoint_metrics in api_metrics.items():
            response_time = endpoint_metrics.get("avg_response_time", 0)
            if self._evaluate_condition(response_time, rule.threshold, rule.condition):
                return True
        return False
    
    def _check_memory_usage_condition(self, rule: AlertRule, metrics: Dict[str, Any]) -> bool:
        """Verifica condição de uso de memória"""
        memory_usage = metrics.get("system_metrics", {}).get("memory_usage_mb", 0)
        return self._evaluate_condition(memory_usage, rule.threshold, rule.condition)
    
    def _check_cpu_usage_condition(self, rule: AlertRule, metrics: Dict[str, Any]) -> bool:
        """Verifica condição de uso de CPU"""
        cpu_usage = metrics.get("system_metrics", {}).get("cpu_usage_percent", 0)
        return self._evaluate_condition(cpu_usage, rule.threshold, rule.condition)
    
    def _check_disk_usage_condition(self, rule: AlertRule, metrics: Dict[str, Any]) -> bool:
        """Verifica condição de uso de disco"""
        disk_usage = metrics.get("system_metrics", {}).get("disk_usage_percent", 0)
        return self._evaluate_condition(disk_usage, rule.threshold, rule.condition)
    
    async def _check_business_metrics_condition(self, rule: AlertRule, metrics: Dict[str, Any]) -> bool:
        """Verifica condição de métricas de negócio"""
        if rule.name == "Sem Atividade de Usuários":
            active_users = metrics.get("business_metrics", {}).get("daily_active_users_count", 0)
            return active_users == 0
        
        return False
    
    def _check_system_health_condition(self, rule: AlertRule, metrics: Dict[str, Any]) -> bool:
        """Verifica condição de saúde do sistema"""
        if rule.name == "Excesso de Erros":
            error_count = metrics.get("system_metrics", {}).get("error_count", 0)
            return self._evaluate_condition(error_count, rule.threshold, rule.condition)
        
        return False
    
    def _evaluate_condition(self, value: float, threshold: float, condition: str) -> bool:
        """Avalia condição de alerta"""
        if condition == "greater_than":
            return value > threshold
        elif condition == "less_than":
            return value < threshold
        elif condition == "equals":
            return value == threshold
        else:
            return False
    
    async def _trigger_alert(self, rule: AlertRule, metrics: Dict[str, Any]):
        """Dispara um alerta"""
        try:
            alert_id = f"{rule.name}_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}"
            
            alert = Alert(
                id=alert_id,
                rule_name=rule.name,
                alert_type=rule.alert_type,
                severity=rule.severity,
                message=f"🚨 {rule.description}",
                details=metrics,
                timestamp=datetime.now(UTC)
            )
            
            # Adicionar aos alertas ativos
            self.active_alerts.append(alert)
            
            # Adicionar ao histórico
            self.alert_history.append(alert)
            
            # Limitar histórico
            if len(self.alert_history) > self.max_history:
                self.alert_history = self.alert_history[-self.max_history:]
            
            # Atualizar último disparo da regra
            rule.last_triggered = datetime.now(UTC)
            
            # Log do alerta
            self._log_alert(alert)
            
            # Notificar callbacks
            for callback in self.alert_callbacks:
                try:
                    callback(alert)
                except Exception as e:
                    logger.error(f"Erro em callback de alerta: {e}")
            
            logger.warning(f"Alerta disparado: {rule.name} - {rule.description}")
            
        except Exception as e:
            logger.error(f"Erro ao disparar alerta {rule.name}: {e}")
    
    def _log_alert(self, alert: Alert):
        """Log do alerta"""
        try:
            # Log de sistema para alertas críticos e altos
            if alert.severity in [AlertSeverity.CRITICAL, AlertSeverity.HIGH]:
                self.cryptoquest_logger.log_system_event(
                    "alert_triggered",
                    level=50,  # CRITICAL
                    details={
                        "alert_id": alert.id,
                        "rule_name": alert.rule_name,
                        "severity": alert.severity.value,
                        "message": alert.message,
                        "timestamp": alert.timestamp.isoformat()
                    }
                )
            else:
                self.cryptoquest_logger.log_system_event(
                    "alert_triggered",
                    level=30,  # WARNING
                    details={
                        "alert_id": alert.id,
                        "rule_name": alert.rule_name,
                        "severity": alert.severity.value,
                        "message": alert.message,
                        "timestamp": alert.timestamp.isoformat()
                    }
                )
                
        except Exception as e:
            logger.error(f"Erro ao logar alerta: {e}")
    
    def add_alert_callback(self, callback: Callable[[Alert], None]):
        """Adiciona callback para notificações de alerta"""
        self.alert_callbacks.append(callback)
    
    def resolve_alert(self, alert_id: str):
        """Resolve um alerta"""
        try:
            for alert in self.active_alerts:
                if alert.id == alert_id:
                    alert.resolved = True
                    alert.resolved_at = datetime.now(UTC)
                    self.active_alerts.remove(alert)
                    
                    # Log da resolução
                    self.cryptoquest_logger.log_system_event(
                        "alert_resolved",
                        details={
                            "alert_id": alert_id,
                            "rule_name": alert.rule_name,
                            "resolved_at": alert.resolved_at.isoformat()
                        }
                    )
                    
                    logger.info(f"Alerta resolvido: {alert_id}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Erro ao resolver alerta {alert_id}: {e}")
            return False
    
    def get_active_alerts(self) -> List[Alert]:
        """Retorna alertas ativos"""
        return self.active_alerts.copy()
    
    def get_alert_history(self, hours: int = 24) -> List[Alert]:
        """Retorna histórico de alertas"""
        cutoff_time = datetime.now(UTC) - timedelta(hours=hours)
        return [
            alert for alert in self.alert_history
            if alert.timestamp > cutoff_time
        ]
    
    def get_alert_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de alertas"""
        total_alerts = len(self.alert_history)
        active_alerts = len(self.active_alerts)
        
        severity_counts = {}
        for severity in AlertSeverity:
            severity_counts[severity.value] = len([
                alert for alert in self.active_alerts
                if alert.severity == severity
            ])
        
        return {
            "total_alerts": total_alerts,
            "active_alerts": active_alerts,
            "resolved_alerts": total_alerts - active_alerts,
            "severity_breakdown": severity_counts,
            "rules_enabled": len([r for r in self.alert_rules.values() if r.enabled]),
            "rules_total": len(self.alert_rules)
        }

# Instância global
_alert_manager = None

def get_alert_manager() -> AlertManager:
    """Retorna a instância global do gerenciador de alertas"""
    global _alert_manager
    if _alert_manager is None:
        _alert_manager = AlertManager()
    return _alert_manager
