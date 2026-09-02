# main.py — clean entry point, easy to read
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.classify import router as classify_router
from routers.analyze import router as analyze_router
from routers.chat import router as chat_router

app = FastAPI(title="Resume Analyzer — Clean Structure")

# CORS — allow frontend (Vercel / localhost)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# register routes
app.include_router(classify_router)
app.include_router(analyze_router)
app.include_router(chat_router)

@app.get("/")
def root():
    return {"msg":"Resume Analyzer API running","docs":"/docs","health":"/api/health"}

# run: uvicorn main:app --reload --port 8000
