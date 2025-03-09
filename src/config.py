from typing import Dict
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    
    PG_CONNECTION = "postgresql://admin:admin@localhost:5432/vector_db"
    VECTOR_COLLECTION = "my_docs"
    
    LLM_MODEL = "mixtral-8x7b-32768"
    LLM_TEMPERATURE = 0
    LLM_MAX_TOKENS = None
    LLM_TIMEOUT = None
    LLM_MAX_RETRIES = 2 