from pydantic import BaseModel, EmailStr 
from typing import Optional 
from datetime import datetime 

# Modelo para o corpo da requisicao 
# Representa os dados necessarios para registrar um novo usuario
class UserRegister(BaseModel): 
    name: str 
    email: EmailStr  
    password: str

# Modelo para corpo da requisicao de login 
# Representa os dados necessarios para login de usuario 
class UserLogin(BaseModel): 
    email: EmailStr 
    password: str 

# Modelo para o usuario retornado pelo Firebase Auth (apos autenticacao bem sucedida)
# Representa os dados retornados pelo Firebase Auth 
class FirebaseUser(BaseModel): 
    uid:str 
    email: EmailStr 
    name: Optional[str] = None 

# Modelo para perfil do Usuario Armazenado no Firestore 
# Representa os dados do perfil do usuario 
class UserProfile(BaseModel): 
    uid: str 
    name: str 
    email: EmailStr 
    register_date: datetime 
    level: Optional[int] = 1 

    class Config: 
        # Permite que o Pydantic mapeie o campo 'id' do Firestore para 'uid'
        # e outros campos que possam ser retornados com nomes diferentes.
        # Mas para Firestore, onde estamos usando uid como ID do documento,
        # 'uid' será o campo principal.
        # from_attributes = True # Pydantic v2+ (Antigo: orm_mode = True)
        pass 

# Modelo para resposta de sucesso login/registro 
# Representa a resposta de sucesso para login ou registro 
class AuthSuccess(BaseModel): 
    message: str 
    uid: str 
    token: Optional[str] = None # Token de ID JWT, util para testes
    user_profile: Optional[UserProfile] = None # Dados do perfil do Firestore