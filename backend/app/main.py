from fastapi import FastAPI
from app.repositories.user_repository import create_user, get_user

app = FastAPI()

@app.get("/")
def root():
    return {"message": "API funcionando!"}

@app.get("/users")
def teste_create(): 
    user = {"nome": "Caio","email" : "caio@gmail.com"}
    return create_user(user) 

@app.get("/users/{user_id}")
def get_user(user_id):
    return get_user(user_id)