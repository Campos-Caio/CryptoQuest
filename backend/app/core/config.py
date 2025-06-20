import os 
from dotenv import load_dotenv 

load_dotenv()

class Settings: 
    FIREBASE_CREDENTIALS: str = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

settings = Settings() 