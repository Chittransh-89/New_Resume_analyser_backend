# main.py — clean entry point, easy to read
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.classify import router as classify_router
from routers.analyze import router as analyze_router
from routers.chat import router as chat_router

app = FastAPI(title="Resume Analyzer — Clean Structure")

# CORS — configurable via CORS_ORIGINS env (comma-separated); "*" for dev.
_cors_env = os.getenv("CORS_ORIGINS", "*")
_allow_origins = [o.strip() for o in _cors_env.split(",") if o.strip()] or ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_allow_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# register routes
app.include_router(classify_router)
app.include_router(analyze_router)
app.include_router(chat_router)


@app.get("/")
def root():
    return {"msg": "Resume Analyzer API running", "docs": "/docs", "health": "/health"}


@app.get("/health")
def health():
    """Deployment health check (also available at /api/health via chat router)."""
    return {"status": "ok"}


# run: uvicorn main:app --reload --port 8000
