from app.api import quizzes_api
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth
from app.api import questionnaire_api
from app.api import missions_api
from app.api import user_api
from app.api import quizzes_api
from app.api import learning_paths_api
from app.api import ranking_api
from app.api import rewards_api
from app.services.event_bus import get_event_bus
from app.services.badge_engine import get_badge_engine


app = FastAPI(
    title="CryptoQuest backend", 
    description="API do backend do App CrytpoQuest",
    version='0.1.0', 
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#incluir os routers
app.include_router(auth.router)
app.include_router(questionnaire_api.router)
app.include_router(missions_api.router)
app.include_router(user_api.router)
app.include_router(quizzes_api.router)
app.include_router(learning_paths_api.router)
app.include_router(ranking_api.router)
app.include_router(rewards_api.router)

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Bem-vindo ao Backend CryptoQuest!"}

@app.get("/health", tags=["Health"])
async def health_check():
    """Endpoint para verificação de saúde do serviço (Docker healthcheck)"""
    return {"status": "healthy", "service": "cryptoquest-backend"}

@app.on_event("startup")
async def startup_event():
    """Inicializa o sistema de eventos na startup"""
    # Inicializar EventBus e BadgeEngine
    event_bus = get_event_bus()
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
