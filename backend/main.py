import firebase_admin
from firebase_admin import credentials, firestore
import json
import os

# Inicializar Firebase Admin
cred = credentials.Certificate("firebase_key.json")
firebase_admin.initialize_app(cred)

# Conectar ao Firestore
db = firestore.client()

# Dados dos quizzes
quizzes_data = [
    {
        "id": "btc_quiz_01",
        "title": "Fundamentos do Bitcoin",
        "questions": [
            {
                "text": "O que é a Blockchain do Bitcoin?",
                "options": [
                    "Um registro de transações distribuído",
                    "Um tipo de carteira digital",
                    "Uma empresa de mineração"
                ],
                "correct_answer_index": 0
            },
            {
                "text": "Qual é a principal característica do Bitcoin?",
                "options": [
                    "É controlado por um banco central",
                    "É descentralizado e peer-to-peer",
                    "É uma moeda física",
                    "É emitido por governos"
                ],
                "correct_answer_index": 1
            }
        ]
    },
]

def populate_quizzes():
    """Popula a coleção quizzes com dados de exemplo"""
    collection_ref = db.collection('quizzes1')
    
    for quiz in quizzes_data:
        quiz_id = quiz.pop('id')  # Remove o id do dicionário
        doc_ref = collection_ref.document(quiz_id)
        
        try:
            doc_ref.set(quiz)
            print(f"✅ Quiz '{quiz_id}' criado com sucesso!")
        except Exception as e:
            print(f"❌ Erro ao criar quiz '{quiz_id}': {e}")