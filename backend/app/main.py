from fastapi import FastAPI
from app.repositories import user_repository
from app.api import auth


app = FastAPI(
    title="CryptoQuest backend", 
    description="API do backend do App CrytpoQuest",
    version='0.1.0', 
)

#incluir os routers
app.include_router(auth.router)

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Bem-vindo ao Backend CryptoQuest!"}
