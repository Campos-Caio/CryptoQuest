"""
API para dashboard de monitoramento e métricas em tempo real.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, Any, List, Optional
from datetime import datetime, UTC, timedelta
from app.services.metrics_collector import get_metrics_collector
from app.services.alert_manager import get_alert_manager, Alert
from app.core.logging_config import get_cryptoquest_logger, LogCategory
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/monitoring", tags=["Monitoring"])

@router.get("/metrics/current", summary="Métricas Atuais")
async def get_current_metrics():
    """
    Retorna métricas atuais do sistema.
    """
    try:
        metrics_collector = get_metrics_collector()
        metrics = metrics_collector.get_current_metrics()
        
        # Log da consulta de métricas
        cryptoquest_logger = get_cryptoquest_logger()
        cryptoquest_logger.log_system_event(
            "metrics_dashboard_accessed",
            details={"endpoint": "/monitoring/metrics/current"}
        )
        
        return {
            "success": True,
            "data": metrics,
            "timestamp": datetime.now(UTC).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter métricas atuais: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/metrics/history", summary="Histórico de Métricas")
async def get_metrics_history(
    hours: int = Query(24, description="Horas de histórico", ge=1, le=168)
):
    """
    Retorna histórico de métricas.
    """
    try:
        metrics_collector = get_metrics_collector()
        history = metrics_collector.get_metrics_history(hours=hours)
        
        return {
            "success": True,
            "data": history,
            "period_hours": hours,
            "total_points": len(history),
            "timestamp": datetime.now(UTC).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter histórico de métricas: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/alerts/active", summary="Alertas Ativos")
async def get_active_alerts():
    """
    Retorna alertas ativos do sistema.
    """
    try:
        alert_manager = get_alert_manager()
        active_alerts = alert_manager.get_active_alerts()
        
        # Converter Alert objects para dict
        alerts_data = []
        for alert in active_alerts:
            alerts_data.append({
                "id": alert.id,
                "rule_name": alert.rule_name,
                "alert_type": alert.alert_type.value,
                "severity": alert.severity.value,
                "message": alert.message,
                "details": alert.details,
                "timestamp": alert.timestamp.isoformat(),
                "resolved": alert.resolved
            })
        
        return {
            "success": True,
            "data": alerts_data,
            "total_active": len(active_alerts),
            "timestamp": datetime.now(UTC).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter alertas ativos: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/alerts/history", summary="Histórico de Alertas")
async def get_alert_history(
    hours: int = Query(24, description="Horas de histórico", ge=1, le=168)
):
    """
    Retorna histórico de alertas.
    """
    try:
        alert_manager = get_alert_manager()
        history = alert_manager.get_alert_history(hours=hours)
        
        # Converter Alert objects para dict
        alerts_data = []
        for alert in history:
            alerts_data.append({
                "id": alert.id,
                "rule_name": alert.rule_name,
                "alert_type": alert.alert_type.value,
                "severity": alert.severity.value,
                "message": alert.message,
                "details": alert.details,
                "timestamp": alert.timestamp.isoformat(),
                "resolved": alert.resolved,
                "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None
            })
        
        return {
            "success": True,
            "data": alerts_data,
            "period_hours": hours,
            "total_alerts": len(history),
            "timestamp": datetime.now(UTC).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter histórico de alertas: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.post("/alerts/{alert_id}/resolve", summary="Resolver Alerta")
async def resolve_alert(alert_id: str):
    """
    Resolve um alerta específico.
    """
    try:
        alert_manager = get_alert_manager()
        success = alert_manager.resolve_alert(alert_id)
        
        if success:
            # Log da resolução manual
            cryptoquest_logger = get_cryptoquest_logger()
            cryptoquest_logger.log_system_event(
                "alert_manually_resolved",
                details={"alert_id": alert_id}
            )
            
            return {
                "success": True,
                "message": f"Alerta {alert_id} resolvido com sucesso",
                "timestamp": datetime.now(UTC).isoformat()
            }
        else:
            raise HTTPException(status_code=404, detail="Alerta não encontrado")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao resolver alerta {alert_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/alerts/stats", summary="Estatísticas de Alertas")
async def get_alert_stats():
    """
    Retorna estatísticas de alertas.
    """
    try:
        alert_manager = get_alert_manager()
        stats = alert_manager.get_alert_stats()
        
        return {
            "success": True,
            "data": stats,
            "timestamp": datetime.now(UTC).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas de alertas: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/dashboard/summary", summary="Resumo do Dashboard")
async def get_dashboard_summary():
    """
    Retorna resumo completo para o dashboard.
    """
    try:
        metrics_collector = get_metrics_collector()
        alert_manager = get_alert_manager()
        
        # Obter métricas atuais
        current_metrics = metrics_collector.get_current_metrics()
        
        # Obter alertas ativos
        active_alerts = alert_manager.get_active_alerts()
        
        # Obter estatísticas de alertas
        alert_stats = alert_manager.get_alert_stats()
        
        # Calcular saúde geral do sistema
        system_health = _calculate_system_health(current_metrics, active_alerts)
        
        summary = {
            "system_health": system_health,
            "current_metrics": current_metrics,
            "active_alerts": [
                {
                    "id": alert.id,
                    "rule_name": alert.rule_name,
                    "severity": alert.severity.value,
                    "message": alert.message,
                    "timestamp": alert.timestamp.isoformat()
                }
                for alert in active_alerts
            ],
            "alert_stats": alert_stats,
            "timestamp": datetime.now(UTC).isoformat()
        }
        
        return {
            "success": True,
            "data": summary,
            "timestamp": datetime.now(UTC).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter resumo do dashboard: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/logs/recent", summary="Logs Recentes")
async def get_recent_logs(
    category: Optional[str] = Query(None, description="Categoria do log"),
    level: Optional[str] = Query(None, description="Nível do log"),
    limit: int = Query(50, description="Número de logs", ge=1, le=200)
):
    """
    Retorna logs recentes do sistema.
    """
    try:
        import json
        import os
        
        logs = []
        log_categories = ["application", "security", "performance", "business", "system"]
        
        if category and category in log_categories:
            log_categories = [category]
        
        for log_category in log_categories:
            log_dir = f"logs/{log_category}"
            if os.path.exists(log_dir):
                for file in os.listdir(log_dir):
                    if file.endswith('.log'):
                        file_path = os.path.join(log_dir, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                for line in f:
                                    if line.strip():
                                        try:
                                            data = json.loads(line.strip())
                                            if level and data.get('level', '').upper() != level.upper():
                                                continue
                                            logs.append(data)
                                        except json.JSONDecodeError:
                                            continue
                        except Exception:
                            continue
        
        # Ordenar por timestamp (mais recentes primeiro)
        logs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        # Limitar resultados
        logs = logs[:limit]
        
        return {
            "success": True,
            "data": logs,
            "total_found": len(logs),
            "filters": {
                "category": category,
                "level": level,
                "limit": limit
            },
            "timestamp": datetime.now(UTC).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter logs recentes: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

def _calculate_system_health(metrics: Dict[str, Any], active_alerts: List[Alert]) -> Dict[str, Any]:
    """
    Calcula a saúde geral do sistema baseada em métricas e alertas.
    """
    try:
        health_score = 100
        issues = []
        
        # Verificar alertas críticos
        critical_alerts = [a for a in active_alerts if a.severity.value == "critical"]
        if critical_alerts:
            health_score -= 30
            issues.append(f"{len(critical_alerts)} alerta(s) crítico(s)")
        
        # Verificar alertas altos
        high_alerts = [a for a in active_alerts if a.severity.value == "high"]
        if high_alerts:
            health_score -= 20
            issues.append(f"{len(high_alerts)} alerta(s) de alta prioridade")
        
        # Verificar métricas de sistema
        system_metrics = metrics.get("system_metrics", {})
        
        # CPU
        cpu_usage = system_metrics.get("cpu_usage_percent", 0)
        if cpu_usage > 90:
            health_score -= 15
            issues.append(f"CPU muito alta: {cpu_usage:.1f}%")
        elif cpu_usage > 80:
            health_score -= 10
            issues.append(f"CPU alta: {cpu_usage:.1f}%")
        
        # Memória
        memory_usage = system_metrics.get("memory_usage_mb", 0)
        if memory_usage > 1024:  # 1GB
            health_score -= 15
            issues.append(f"Memória alta: {memory_usage:.1f} MB")
        
        # Disco
        disk_usage = system_metrics.get("disk_usage_percent", 0)
        if disk_usage > 95:
            health_score -= 20
            issues.append(f"Disco quase cheio: {disk_usage:.1f}%")
        elif disk_usage > 90:
            health_score -= 10
            issues.append(f"Disco alto: {disk_usage:.1f}%")
        
        # Verificar taxa de erro
        api_metrics = metrics.get("api_metrics", {})
        total_errors = 0
        total_requests = 0
        
        for endpoint, endpoint_metrics in api_metrics.items():
            total_requests += endpoint_metrics.get("total_requests", 0)
            error_rate = endpoint_metrics.get("error_rate", 0)
            total_errors += (error_rate / 100) * endpoint_metrics.get("total_requests", 0)
        
        if total_requests > 0:
            overall_error_rate = (total_errors / total_requests) * 100
            if overall_error_rate > 10:
                health_score -= 25
                issues.append(f"Taxa de erro alta: {overall_error_rate:.1f}%")
            elif overall_error_rate > 5:
                health_score -= 15
                issues.append(f"Taxa de erro elevada: {overall_error_rate:.1f}%")
        
        # Garantir que o score não seja negativo
        health_score = max(0, health_score)
        
        # Determinar status
        if health_score >= 90:
            status = "excellent"
            status_text = "Excelente"
        elif health_score >= 75:
            status = "good"
            status_text = "Bom"
        elif health_score >= 50:
            status = "warning"
            status_text = "Atenção"
        else:
            status = "critical"
            status_text = "Crítico"
        
        return {
            "score": health_score,
            "status": status,
            "status_text": status_text,
            "issues": issues,
            "total_issues": len(issues),
            "last_updated": datetime.now(UTC).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erro ao calcular saúde do sistema: {e}")
        return {
            "score": 0,
            "status": "unknown",
            "status_text": "Desconhecido",
            "issues": ["Erro ao calcular saúde do sistema"],
            "total_issues": 1,
            "last_updated": datetime.now(UTC).isoformat()
        }
