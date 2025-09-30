from app.core.firebase import get_firestore_db
from app.models.user import UserProfile
from datetime import datetime, timezone
from typing import Optional, Union, List 
from fastapi import Depends
from google.protobuf.timestamp_pb2 import Timestamp

class UserRepository:
    def __init__(self, dbclient):
        self.db = dbclient
        self.collection = self.db.collection("users")

    def create_user_profile(self, uid: str, name: str, email: str) -> UserProfile:
        """
        Cria um novo documento de perfil de usuario no Firestore
        O UID do Firebase Auth eh usado como ID do documento
        """
        user_data = {
            "name": name,
            "email": email,
            "register_date": datetime.now(timezone.utc),
            "level": 1,
            "has_completed_questionnaire": False,  # ✅ EXPLICITAMENTE define como False para novos usuários
        }

        self.collection.document(uid).set(user_data)
        print(f"🔍 [UserRepository] Perfil criado no Firestore com dados: {user_data}")
        
        # Retorna o UserProfile Completo
        user_profile = UserProfile(
            uid=uid,
            name=name,
            email=email,
            register_date=user_data["register_date"],
            level=user_data["level"],
            has_completed_questionnaire=False,  # ✅ Garante que o campo seja incluído no retorno
        )
        print(f"🔍 [UserRepository] UserProfile retornado - has_completed_questionnaire: {user_profile.has_completed_questionnaire}")
        return user_profile

    def get_user_profile(self, uid: str) -> Union[UserProfile, None]:
        """
        Retorna o perfil do usuário pelo UID.
        """
        doc = self.collection.document(uid).get()
        if not doc.exists:
            return None

        data = doc.to_dict()

        # Verifica se o campo "register_date" existe e é um Timestamp
        if isinstance(data.get("register_date"), Timestamp):
            # Converte o Timestamp para datetime com fuso horário local (se possível)
            if hasattr(data["register_date"], "ToDatetime"):
                data["register_date"] = data["register_date"].ToDatetime().astimezone()

        # ✅ Garante que campos com valores padrão sejam definidos se não existirem
        # Isso é importante para perfis criados antes da correção
        if "has_completed_questionnaire" not in data:
            data["has_completed_questionnaire"] = False
            print(f"🔍 [UserRepository] Campo has_completed_questionnaire não encontrado, definindo como False")
        if "points" not in data:
            data["points"] = 0
        if "level" not in data:
            data["level"] = 1

        user_profile = UserProfile(uid=doc.id, **data)
        print(f"🔍 [UserRepository] Perfil recuperado - has_completed_questionnaire: {user_profile.has_completed_questionnaire}")
        return user_profile

    def update_user_Profile(self, uid:str, new_data: dict) -> bool: # Adicione tipo para new_data
        """
        Atualiza o perfil de um usuario existente
        """
        doc_ref = self.collection.document(uid)
        if doc_ref.get().exists:
            doc_ref.update(new_data)
            return True
        return False
    
    def update_user_profile(self, uid: str, new_data: dict) -> bool:
        """Alias para update_user_Profile para compatibilidade"""
        return self.update_user_Profile(uid, new_data)

    def delete_user_profile(self, uid:str) -> bool:
        doc_ref = self.collection.document(uid)
        if doc_ref.get().exists:
            doc_ref.delete()
            return True
        return False

    def get_all_users(self) -> List[UserProfile]:
        """Busca todos os usuários"""
        try:
            docs = self.collection.stream()
            users = []
            for doc in docs:
                data = doc.to_dict()
                # Garante que campos com valores padrão sejam definidos
                if "has_completed_questionnaire" not in data:
                    data["has_completed_questionnaire"] = False
                if "points" not in data:
                    data["points"] = 0
                if "level" not in data:
                    data["level"] = 1
                if "xp" not in data:
                    data["xp"] = 0
                if "badges" not in data:
                    data["badges"] = []
                if "completed_learning_paths" not in data:
                    data["completed_learning_paths"] = []
                if "daily_missions" not in data:
                    data["daily_missions"] = []
                if "current_streak" not in data:
                    data["current_streak"] = 0
                if "average_score" not in data:
                    data["average_score"] = 0
                if "current_streak" not in data:
                    data["current_streak"] = 0
                
                user_profile = UserProfile(uid=doc.id, **data)
                users.append(user_profile)
            return users
        except Exception as e:
            print(f"Erro ao buscar todos os usuários: {e}")
            return []

    def get_users_by_activity_period(self, start_date: datetime, end_date: datetime) -> List[UserProfile]:
        """Busca usuários ativos em um período específico"""
        try:
            # Por enquanto, retorna todos os usuários
            # Em uma implementação mais robusta, filtraria por data de última atividade
            return self.get_all_users()
        except Exception as e:
            print(f"Erro ao buscar usuários por período: {e}")
            return []

def get_user_repository() -> UserRepository:
    """Retorna instância do UserRepository"""
    db_client = get_firestore_db()
    return UserRepository(db_client)

__all__ = ['UserRepository', 'get_user_repository']