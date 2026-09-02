# config.py — all model names & keys in ONE place
# Change models here to test different LLMs

import os
from dotenv import load_dotenv

load_dotenv()  # loads .env file if present

# ========== GEMINI (Resume Analyzer) — REPLACED KIMI/NVIDIA ==========
# Gemini via Google Generative AI — https://aistudio.google.com/app/apikey
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "") or os.getenv("GEMINI_API_KEY", "")
# >>> SINGLE SOURCE OF TRUTH — change ONLY this line to test any model <<<
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-3.5-flash-lite")
# aliases — DO NOT EDIT (all point to LLM_MODEL)
KIMI_MODEL = BULLET_MODEL = ANALYZER_MODEL = LLM_MODEL
# compat aliases for old code using NVIDIA vars
NVIDIA_API_KEY = GOOGLE_API_KEY
NVIDIA_BASE_URL = "https://generativelanguage.googleapis.com"

# ========== GitHub Models (CareerBuddy Chat) — unchanged ==========
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
GITHUB_MODEL = os.getenv("GITHUB_MODEL", "openai/gpt-4o-mini")  # ← change to "openai/gpt-4o"
GITHUB_BASE_URL = "https://models.inference.ai.azure.com"

# ========== Embeddings (Semantic Score) ==========
# FAST: all-MiniLM-L6-v2 is 5x faster than e5-base (80MB vs 400MB, CPU encode 0.1s vs 0.6s)
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "intfloat/e5-base-v2")

# ========== App ==========
MAX_CHAT_HISTORY = 20
MAX_TOKENS = 1024
TEMPERATURE = 0.7

# quick check
def check_keys():
    if not GOOGLE_API_KEY:
        print("⚠️ GOOGLE_API_KEY/GEMINI_API_KEY missing — classify/analyze will 500 (set in .env)")
    if not GITHUB_TOKEN:
        print("⚠️ GITHUB_TOKEN missing — chat will fail")
