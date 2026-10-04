"""
CareerBuddy - Configuration File (FastAPI)
Loads all environment variables and app settings.
"""

import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# ========== GEMINI (Resume Analyzer) ==========
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-3.5-flash-lite")

# Aliases
GEMINI_MODEL = KIMI_MODEL = BULLET_MODEL = ANALYZER_MODEL = LLM_MODEL

# ========== Databases & Storage ==========
CHROMA_PERSIST_DIR = r"E:\NEW_RESUME_ANALYSER_BACKEND\Career_Buddy_rag\chroma_db"
# DATABASE_PATH = os.getenv("DATABASE_PATH", "career_assistant.db")

# ========== Embeddings & External APIs ==========
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
# YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")

# ========== FastAPI App Settings ==========
APP_NAME = "CareerBuddy API"
API_V1_STR = os.getenv("API_V1_STR", "/api/v1")
HOST = os.getenv("HOST", "0.0.0.0")
PORT =  8000
DEBUG = os.getenv("DEBUG", "True").lower() == "true"
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

MAX_CHAT_HISTORY = 20
MAX_SEARCH_RESULTS = 5
MAX_TOKENS = 2500
TEMPERATURE =  0.7

class Config:
    """Application configuration for FastAPI."""

    GEMINI_API_KEY = GEMINI_API_KEY
    LLM_MODEL = LLM_MODEL
    GEMINI_MODEL = GEMINI_MODEL
    KIMI_MODEL = KIMI_MODEL
    BULLET_MODEL = BULLET_MODEL
    ANALYZER_MODEL = ANALYZER_MODEL

    # DATABASE_PATH = DATABASE_PATH
    CHROMA_PERSIST_DIR = CHROMA_PERSIST_DIR
    EMBEDDING_MODEL = EMBEDDING_MODEL


    APP_NAME = APP_NAME
    API_V1_STR = API_V1_STR
    HOST = HOST
    PORT = PORT
    DEBUG = DEBUG
    CORS_ORIGINS = CORS_ORIGINS

    MAX_CHAT_HISTORY = MAX_CHAT_HISTORY
    MAX_SEARCH_RESULTS = MAX_SEARCH_RESULTS
    MAX_TOKENS = MAX_TOKENS
    TEMPERATURE = TEMPERATURE

    @classmethod
    def validate(cls):
        """Validate critical API keys."""
        errors = []

        if not cls.GEMINI_API_KEY:
            print("⚠️  Warning: GEMINI_API_KEY not set (Resume analysis will fail)")

        if errors:
            for err in errors:
                print(err)
            raise ValueError("Missing required environment variables!")

        print("✅ Config loaded successfully for FastAPI")
        return True


def check_keys():
    if not GEMINI_API_KEY:
        print("⚠️  GEMINI_API_KEY missing — classify/analyze will 500 (set in .env)")


# Auto-validate when imported
if __name__ == "__main__":
    Config.validate()
    print(f"Model: {Config.GEMINI_MODEL}")
    print(f"Port: {Config.PORT}")
    print(f"API Prefix: {Config.API_V1_STR}")
    # print(f"DB Path: {Config.DATABASE_PATH}")
    print(f"CORS Origins: {Config.CORS_ORIGINS}")
    check_keys()