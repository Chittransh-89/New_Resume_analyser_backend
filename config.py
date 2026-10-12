"""
CareerBuddy - Configuration File (FastAPI)
Loads all environment variables and app settings.
"""

import os
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load .env file
load_dotenv()

# ========== GEMINI (Resume Analyzer) ==========
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
LLM_PROVIDER = "gemini"
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-3.5-flash-lite")
BASE_URL = os.getenv("BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/")
# Aliases
GEMINI_MODEL = KIMI_MODEL = BULLET_MODEL = ANALYZER_MODEL = LLM_MODEL

# ========== Databases & Storage (portable; no hardcoded machine paths) ==========
# CareerBuddy now uses deterministic keyword retrieval over bundled data files,
# so no ChromaDB persist dir is required. Kept for backwards-compat only.
CHROMA_PERSIST_DIR = os.getenv(
    "CHROMA_PERSIST_DIR",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "Career_Buddy_rag", "chroma_db"),
)
# DATABASE_PATH = os.getenv("DATABASE_PATH", "career_assistant.db")

# ========== External APIs ==========
# EMBEDDING_MODEL is deprecated: resume scoring is LLM-only, no local embeddings.
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "")
# YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")

# ========== FastAPI App Settings ==========
APP_NAME = "CareerBuddy API"
API_V1_STR = os.getenv("API_V1_STR", "/api/v1")
HOST = os.getenv("HOST", "0.0.0.0")
try:
    PORT = int(os.getenv("PORT", "8000"))
except ValueError:
    PORT = 8000
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
    BASE_URL = BASE_URL
    GEMINI_MODEL = GEMINI_MODEL
    KIMI_MODEL = KIMI_MODEL
    BULLET_MODEL = BULLET_MODEL
    ANALYZER_MODEL = ANALYZER_MODEL

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
        """Warn when critical API keys are missing. Returns True always;
        routes fail clearly later if the key is actually needed."""
        if not cls.GEMINI_API_KEY:
            print("⚠️  Warning: GEMINI_API_KEY not set (Resume analysis will fail)")
            logger.warning("⚠️  Warning: GEMINI_API_KEY not set (Resume analysis will fail)")

        print("✅ Config loaded successfully for FastAPI")
        logger.info("✅ Config loaded successfully for FastAPI")
        return True


def check_keys():
    if not GEMINI_API_KEY:
        print("⚠️  GEMINI_API_KEY missing — classify/analyze will 500 (set in .env)")
        logger.warning("⚠️  GEMINI_API_KEY missing — classify/analyze will 500 (set in .env)")


# Auto-validate when imported
if __name__ == "__main__":
    Config.validate()
    print(f"Model: {Config.GEMINI_MODEL}")
    logger.info("Model: %s", Config.GEMINI_MODEL)
    print(f"Port: {Config.PORT}")
    logger.info("Port: %s", Config.PORT)
    print(f"API Prefix: {Config.API_V1_STR}")
    logger.info("API Prefix: %s", Config.API_V1_STR)
    print(f"CORS Origins: {Config.CORS_ORIGINS}")
    logger.info("CORS Origins: %s", Config.CORS_ORIGINS)
    check_keys()