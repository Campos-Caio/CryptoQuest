from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth


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

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Bem-vindo ao Backend CryptoQuest!"}
