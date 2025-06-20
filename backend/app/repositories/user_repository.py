from app.core.firebase import get_firestore_db, get_firestore_db_async 
from app.models.user import UserProfile
from datetime import datetime
from typing import Optional, Union 
from fastapi import Depends

class UserRepository:
    def __init__(self, dbclient):
        self.db = dbclient
        self.collection = self.db.collection("users")

    async def create_user_profile(self, uid: str, name: str, email: str) -> UserProfile:
        """
        Cria um novo documento de perfil de usuario no Firestore
        O UID do Firebase Auth eh usado como ID do documento
        """
        user_data = {
            "name": name,
            "email": email,
            "register_date": datetime.now(),
            "level": 1,
        }

        await self.collection.document(uid).set(user_data)
        # Retorna o UserProfile Completo
        return UserProfile(
            uid=uid,
            name=name,
            email=email,
            register_date=user_data["register_date"],
            level=user_data["level"],
        )

    async def get_user_profile(self, uid:str) -> Union[UserProfile, None]: # Use Union ou Optional[UserProfile]
        """
        Retorna o perfil do usuario pelo UID
        """
        doc = await self.collection.document(uid).get()
        if doc.exists:
            data = doc.to_dict()
            # Certifique-se de que a data seja tratada corretamente se for um objeto Timestamp do Firestore
            # Exemplo: data["register_date"] = data["register_date"].astimezone() if hasattr(data["register_date"], 'astimezone') else data["register_date"]
            if isinstance(data.get("register_date"), type(self.db.collection_group(None).document("dummy").get()._data.get("timestamp_field"))):
                data["register_date"] = data["register_date"].astimezone()
            return UserProfile(uid=doc.id, **data)
        return None

    async def update_user_Profile(self, uid:str, new_data: dict) -> bool: # Adicione tipo para new_data
        """
        Atualiza o perfil de um usuario existente
        """
        doc_ref = self.collection.document(uid)
        if(await doc_ref.get()).exists:
            await doc_ref.update(new_data)
            return True
        return False

    async def delete_user_profile(self, uid:str) -> bool:
        doc_ref = self.collection.document(uid)
        if(await doc_ref.get()).exists:
            await doc_ref.delete()
            return True
        return False

async def get_user_repository(
    # Injeta o cliente DB assíncrono, aguardando sua inicialização
    db_client = Depends(get_firestore_db_async)
) -> UserRepository:
    return UserRepository(db_client)

__all__ = ['UserRepository', 'get_user_repository']