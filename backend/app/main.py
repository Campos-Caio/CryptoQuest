import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from app.api import auth
from app.api import questionnaire_api
from app.api import missions_api
from app.api import user_api
from app.api import quizzes_api
from app.api import learning_paths_api
from app.api import ranking_api
from app.api import rewards_api
from app.api import ai_api
from app.services.event_bus import get_event_bus
from app.services.badge_engine import get_badge_engine
from app.services.metrics_collector import get_metrics_collector
from app.services.alert_manager import get_alert_manager
from app.services.health_monitor import get_health_monitor
from app.services.background_task_service import get_background_service
from app.services.fast_cache_service import get_fast_cache
from app.middleware.security import SecurityHeadersMiddleware, RateLimitMiddleware
from app.middleware.logging_middleware import RequestLoggingMiddleware, ErrorLoggingMiddleware
from app.api import monitoring_api
import logging

# Configurar logging
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação"""
    # Startup
    logging.info("🚀 Inicializando CryptoQuest Backend...")
    
    # ⚡ Inicializar workers de processamento assíncrono
    background_service = get_background_service()
    await background_service.start_worker()
    logging.info("✅ Background task worker inicializado!")
    
    # Inicializar cache service
    cache_service = get_fast_cache()
    await cache_service.start_cleanup_worker()
    logging.info("✅ Cache service inicializado!")
    
    # Inicializar BadgeEngine
    badge_engine = get_badge_engine()
    
    # Registrar handlers de eventos
    await badge_engine._register_event_handlers()
    
    # Inicializar sistema de monitoramento avançado
    get_metrics_collector()
    get_alert_manager()
    get_health_monitor()
    logging.info("✅ Sistema de monitoramento avançado inicializado!")
    
    logging.info("✅ Sistema de eventos inicializado com sucesso!")
    logging.info("🎉 CryptoQuest Backend pronto para processar requisições!")
    
    yield
    
    # Shutdown
    logging.info("🛑 Finalizando CryptoQuest Backend...")
    
    # Parar workers
    await background_service.stop_worker()
    await cache_service.stop_cleanup_worker()
    logging.info("✅ Workers finalizados com sucesso!")

app = FastAPI(
    title=os.getenv("API_TITLE", "CryptoQuest Backend"),
    description="API segura do backend do App CryptoQuest",
    version=os.getenv("API_VERSION", "0.1.0"),
    docs_url="/docs" if os.getenv("ENVIRONMENT", "development") == "development" else None,
    redoc_url="/redoc" if os.getenv("ENVIRONMENT", "development") == "development" else None,
    lifespan=lifespan
)

# Configuração segura de CORS
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
if ENVIRONMENT == "development":
    # Em desenvolvimento, permitir todas as origens
    ALLOWED_ORIGINS = ["*"]
else:
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8080").split(",")

ALLOWED_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
ALLOWED_HEADERS = ["Content-Type", "Authorization", "Accept", "Origin", "X-Requested-With"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True if ENVIRONMENT != "development" else False,
    allow_methods=ALLOWED_METHODS,
    allow_headers=ALLOWED_HEADERS,
)

# Middleware de segurança para hosts confiáveis (apenas em produção)
if os.getenv("ENVIRONMENT", "development") == "production":
    ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=ALLOWED_HOSTS
    )

# Middleware de logging (deve ser o primeiro)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(ErrorLoggingMiddleware)

# Middleware de headers de segurança
app.add_middleware(SecurityHeadersMiddleware)

# Middleware de rate limiting (apenas em produção)
if os.getenv("ENVIRONMENT", "development") == "production":
    app.add_middleware(RateLimitMiddleware, calls=100, period=60)

#incluir os routers
app.include_router(auth.router)
app.include_router(questionnaire_api.router)
app.include_router(missions_api.router)
app.include_router(user_api.router)
app.include_router(quizzes_api.router)
app.include_router(learning_paths_api.router)
app.include_router(ai_api.router)  # 🆕 API de IA
app.include_router(ranking_api.router)
app.include_router(rewards_api.router)

# Incluir API de monitoramento
app.include_router(monitoring_api.router)

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Bem-vindo ao Backend CryptoQuest!"}

@app.get("/health", tags=["Health"])
async def health_check():
    """Endpoint para verificação de saúde do serviço (Docker healthcheck)"""
    try:
        # Verificação básica de saúde
        health_monitor = get_health_monitor()
        health_status = health_monitor.get_current_health()
        
        if health_status["overall_status"] in ["healthy", "warning"]:
            return {
                "status": "healthy", 
                "service": "cryptoquest-backend",
                "details": health_status
            }
        else:
            return {
                "status": "unhealthy",
                "service": "cryptoquest-backend", 
                "details": health_status
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "cryptoquest-backend",
            "error": str(e)
        }

@app.on_event("startup")
async def startup_event():
    """Inicializa o sistema de eventos na startup"""
    # Inicializar BadgeEngine
    badge_engine = get_badge_engine()
    
    # Registrar handlers de eventos
    await badge_engine._register_event_handlers()
    
    print("🚀 Sistema de eventos inicializado com sucesso!")

@app.get("/events/stats", tags=["Events"])
async def get_event_stats():
    """Endpoint para verificar estatísticas do sistema de eventos"""
    event_bus = get_event_bus()
    badge_engine = get_badge_engine()
    
    return {
        "event_bus_stats": event_bus.get_event_counts(),
        "badge_engine_stats": badge_engine.get_engine_stats()
    }

@app.get("/background/stats", tags=["Background"])
async def get_background_stats():
    """Endpoint para verificar estatísticas do processamento em background"""
    background_service = get_background_service()
    cache_service = get_fast_cache()
    
    return {
        "background_tasks": background_service.get_metrics(),
        "cache": cache_service.get_stats()
    }
