import os
from google.cloud import firestore
from dotenv import load_dotenv

load_dotenv()

def get_firestore_client():
    return firestore.Client()
