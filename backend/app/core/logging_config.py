"""
Configuração centralizada de logging para o CryptoQuest.
Implementa logging estruturado com rotação automática e categorização.
"""

import os
import json
import logging
import logging.handlers
from datetime import datetime, UTC
from pathlib import Path
from typing import Dict, Any, Optional
from enum import IntEnum

class LogLevel(IntEnum):
    """Níveis de log customizados"""
    CRITICAL = 50
    ERROR = 40
    WARNING = 30
    INFO = 20
    AUDIT = 25  # Logs de auditoria
    PERF = 15   # Logs de performance
    DEBUG = 10

class LogCategory:
    """Categorias de log"""
    APPLICATION = "application"
    SECURITY = "security"
    PERFORMANCE = "performance"
    BUSINESS = "business"
    SYSTEM = "system"

class JSONFormatter(logging.Formatter):
    """Formatter para logs em JSON estruturado"""
    
    def format(self, record):
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created, UTC).isoformat(),
            "level": record.levelname,
            "category": getattr(record, 'category', 'application'),
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Adicionar contexto se disponível
        if hasattr(record, 'context') and record.context:
            log_entry["context"] = record.context
            
        # Adicionar metadados específicos
        metadata = {}
        for attr in ['user_id', 'request_id', 'session_id', 'ip_address', 
                    'endpoint', 'method', 'status_code', 'duration_ms', 
                    'operation', 'records_count', 'cache_hit']:
            if hasattr(record, attr):
                metadata[attr] = getattr(record, attr)
                
        if metadata:
            log_entry["metadata"] = metadata
            
        # Adicionar exceção se presente
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_entry, ensure_ascii=False, default=str)

class CryptoQuestLogger:
    """
    Logger centralizado para o CryptoQuest.
    Gerencia diferentes categorias de log com rotação automática.
    """
    
    def __init__(self, log_dir: str = "logs", max_file_size: int = 100 * 1024 * 1024, 
                 backup_count: int = 5, retention_days: int = 7):
        self.log_dir = Path(log_dir)
        self.max_file_size = max_file_size  # 100MB
        self.backup_count = backup_count    # 5 arquivos de backup
        self.retention_days = retention_days # 7 dias de retenção
        
        # Criar diretórios se não existirem
        self.log_dir.mkdir(exist_ok=True)
        for category in [LogCategory.APPLICATION, LogCategory.SECURITY, 
                        LogCategory.PERFORMANCE, LogCategory.BUSINESS, LogCategory.SYSTEM]:
            (self.log_dir / category).mkdir(exist_ok=True)
            
        self.loggers = {}
        self.formatter = JSONFormatter()
        
        # Configurar níveis customizados
        logging.addLevelName(LogLevel.AUDIT, 'AUDIT')
        logging.addLevelName(LogLevel.PERF, 'PERF')
        
    def get_logger(self, category: str, name: Optional[str] = None) -> logging.Logger:
        """
        Retorna um logger para a categoria especificada.
        
        Args:
            category: Categoria do log (application, security, performance, business, system)
            name: Nome específico do logger (opcional)
            
        Returns:
            Logger configurado para a categoria
        """
        logger_name = f"{category}.{name}" if name else category
        logger_key = logger_name
        
        if logger_key not in self.loggers:
            logger = logging.getLogger(logger_name)
            logger.setLevel(logging.DEBUG)
            
            # Evitar duplicação de handlers
            if logger.handlers:
                return logger
                
            # Configurar handler com rotação
            log_file = self.log_dir / category / f"{name or category}.log"
            handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=self.max_file_size,
                backupCount=self.backup_count,
                encoding='utf-8'
            )
            handler.setFormatter(self.formatter)
            logger.addHandler(handler)
            
            # Handler para console em desenvolvimento
            if os.getenv("ENVIRONMENT", "development") == "development":
                console_handler = logging.StreamHandler()
                console_handler.setFormatter(self.formatter)
                logger.addHandler(console_handler)
                
            self.loggers[logger_key] = logger
            
        return self.loggers[logger_key]
    
    def log_user_action(self, user_id: str, action: str, details: Dict[str, Any] = None):
        """Log específico para ações do usuário"""
        logger = self.get_logger(LogCategory.BUSINESS, "user-actions")
        logger.info(
            f"User action: {action}",
            extra={
                'category': LogCategory.BUSINESS,
                'user_id': user_id,
                'context': details or {}
            }
        )
    
    def log_security_event(self, event_type: str, severity: str, details: Dict[str, Any] = None):
        """Log específico para eventos de segurança"""
        logger = self.get_logger(LogCategory.SECURITY, "auth")
        level = getattr(logging, severity.upper(), logging.INFO)
        
        logger.log(
            level,
            f"Security event: {event_type}",
            extra={
                'category': LogCategory.SECURITY,
                'context': details or {}
            }
        )
    
    def log_performance(self, operation: str, duration_ms: float, metadata: Dict[str, Any] = None):
        """Log específico para métricas de performance"""
        logger = self.get_logger(LogCategory.PERFORMANCE, "api-response")
        logger.log(
            LogLevel.PERF,
            f"Performance: {operation}",
            extra={
                'category': LogCategory.PERFORMANCE,
                'duration_ms': duration_ms,
                'operation': operation,
                'metadata': metadata or {}
            }
        )
    
    def log_business_event(self, event_type: str, details: Dict[str, Any] = None):
        """Log específico para eventos de negócio"""
        logger = self.get_logger(LogCategory.BUSINESS, "events")
        logger.info(
            f"Business event: {event_type}",
            extra={
                'category': LogCategory.BUSINESS,
                'context': details or {}
            }
        )
    
    def log_system_event(self, event_type: str, level: int = logging.INFO, details: Dict[str, Any] = None):
        """Log específico para eventos do sistema"""
        logger = self.get_logger(LogCategory.SYSTEM, "events")
        logger.log(
            level,
            f"System event: {event_type}",
            extra={
                'category': LogCategory.SYSTEM,
                'context': details or {}
            }
        )

# Instância global do logger
_logger_instance = None

def get_cryptoquest_logger() -> CryptoQuestLogger:
    """Retorna a instância global do logger"""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = CryptoQuestLogger()
    return _logger_instance

def get_logger(category: str, name: Optional[str] = None) -> logging.Logger:
    """Função de conveniência para obter um logger"""
    return get_cryptoquest_logger().get_logger(category, name)
