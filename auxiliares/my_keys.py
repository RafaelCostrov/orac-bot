import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_APIKEY")
GEMINI_API_KEY_PESSOAL = os.getenv("GEMINI_API_KEY_PESSOAL")
GEMINI_API_KEY_MILLENA = os.getenv("GEMINI_API_KEY_MILLENA")
GEMINI_API_KEY_RAFA = os.getenv("GEMINI_API_KEY_RAFA")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
