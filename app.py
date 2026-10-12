# app.py — HF Spaces / local launcher alias.
# The real application lives in main.py (FastAPI `app`).
# This file exists so both `main:app` and `app:app` work as entry points.
from main import app  # noqa: F401

if __name__ == "__main__":
    import os
    import uvicorn

    port = int(os.getenv("PORT", "7860"))
    uvicorn.run(app, host="0.0.0.0", port=port)
