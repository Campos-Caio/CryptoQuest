"""
Middleware de segurança para o CryptoQuest
"""

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger(__name__)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware para adicionar headers de segurança
    """
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Headers de segurança
        security_headers = {
            # Previne clickjacking
            "X-Frame-Options": "DENY",
            
            # Previne MIME type sniffing
            "X-Content-Type-Options": "nosniff",
            
            # Habilita proteção XSS do navegador
            "X-XSS-Protection": "1; mode=block",
            
            # Controla políticas de referrer
            "Referrer-Policy": "strict-origin-when-cross-origin",
            
            # Política de segurança de conteúdo
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://apis.google.com; "
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
                "font-src 'self' https://fonts.gstatic.com; "
                "img-src 'self' data: https:; "
                "connect-src 'self' https://identitytoolkit.googleapis.com; "
                "frame-ancestors 'none';"
            ),
            
            # Força HTTPS em produção
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            
            # Remove informações do servidor
            "Server": "CryptoQuest",
        }
        
        # Adicionar headers à resposta
        for header, value in security_headers.items():
            response.headers[header] = value
            
        return response

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware básico de rate limiting
    """
    
    def __init__(self, app, calls: int = 100, period: int = 60):
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.clients = {}
    
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        current_time = request.scope.get("time", 0)
        
        # Limpar entradas antigas
        self.clients = {
            ip: times for ip, times in self.clients.items()
            if any(t > current_time - self.period for t in times)
        }
        
        # Verificar rate limit
        if client_ip in self.clients:
            recent_calls = [t for t in self.clients[client_ip] if t > current_time - self.period]
            if len(recent_calls) >= self.calls:
                logger.warning(f"Rate limit exceeded for IP: {client_ip}")
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Rate limit exceeded. Try again later."}
                )
            self.clients[client_ip] = recent_calls + [current_time]
        else:
            self.clients[client_ip] = [current_time]
        
        response = await call_next(request)
        return response
