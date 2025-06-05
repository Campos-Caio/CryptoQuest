from backend.app.core.firestore import get_firestore_client
from uuid import uuid4 

db = get_firestore_client()
colection = db.collection("users_test")

def create_user(data):
    user_id = str(uuid4())
    data["id"] = user_id
    colection.document(user_id).set(data)
    return data

def get_user(user_id):
    doc = colection.document(user_id).get()
    if doc.exists: 
        return doc.to_dict()
    return None 

def update_user(user_id, new_data):
    if(colection.document(user_id).get().exists):
        colection.document(user_id).update(new_data)
        return True 
    return False 

def delete_user(user_id): 
    if(colection.document(user_id).get().exists): 
        colection.document(user_id).delete()
        return True 
    return False

__all__ = ['UserRepository']