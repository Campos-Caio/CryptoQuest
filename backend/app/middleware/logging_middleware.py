"""
Middleware de logging para requests/responses e performance.
"""

import time
import uuid
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
from app.core.logging_config import get_cryptoquest_logger, LogCategory
from app.services.metrics_collector import get_metrics_collector

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware para logging de requests e responses.
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.logger = get_cryptoquest_logger()
        self.metrics_collector = get_metrics_collector()
        
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Gerar ID único para a requisição
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Extrair informações da requisição
        start_time = time.time()
        user_id = getattr(request.state, 'user_id', None)
        
        # Log da requisição
        self.logger.log_performance(
            operation=f"{request.method} {request.url.path}",
            duration_ms=0,
            metadata={
                'request_id': request_id,
                'method': request.method,
                'path': request.url.path,
                'query_params': str(request.query_params),
                'user_id': user_id,
                'ip_address': request.client.host if request.client else None,
                'user_agent': request.headers.get('user-agent', ''),
                'event_type': 'request_start'
            }
        )
        
        # Processar requisição
        try:
            response = await call_next(request)
            
            # Calcular duração
            duration_ms = (time.time() - start_time) * 1000
            
            # Log da resposta
            self.logger.log_performance(
                operation=f"{request.method} {request.url.path}",
                duration_ms=duration_ms,
                metadata={
                    'request_id': request_id,
                    'method': request.method,
                    'path': request.url.path,
                    'status_code': response.status_code,
                    'user_id': user_id,
                    'duration_ms': duration_ms,
                    'event_type': 'request_complete'
                }
            )
            
            # Registrar métricas de API
            self.metrics_collector.record_api_request(
                endpoint=request.url.path,
                method=request.method,
                status_code=response.status_code,
                duration_ms=duration_ms
            )
            
            return response
            
        except Exception as e:
            # Calcular duração mesmo em caso de erro
            duration_ms = (time.time() - start_time) * 1000
            
            # Log do erro
            self.logger.log_performance(
                operation=f"{request.method} {request.url.path}",
                duration_ms=duration_ms,
                metadata={
                    'request_id': request_id,
                    'method': request.method,
                    'path': request.url.path,
                    'status_code': 500,
                    'user_id': user_id,
                    'duration_ms': duration_ms,
                    'error': str(e),
                    'event_type': 'request_error'
                }
            )
            raise

class ErrorLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware para logging de erros não tratados.
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.logger = get_cryptoquest_logger()
        
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            return await call_next(request)
        except Exception as e:
            # Log detalhado do erro
            request_id = getattr(request.state, 'request_id', 'unknown')
            user_id = getattr(request.state, 'user_id', None)
            
            self.logger.log_system_event(
                event_type="unhandled_exception",
                level=50,  # CRITICAL
                details={
                    'request_id': request_id,
                    'user_id': user_id,
                    'path': request.url.path,
                    'method': request.method,
                    'exception_type': type(e).__name__,
                    'exception_message': str(e),
                    'ip_address': request.client.host if request.client else None
                }
            )
            raise
