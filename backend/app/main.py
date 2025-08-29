from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth
from app.api import questionnaire_api
from app.api import missions_api
from app.api import user_api
from app.api import quizzes_api


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

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Bem-vindo ao Backend CryptoQuest!"}
