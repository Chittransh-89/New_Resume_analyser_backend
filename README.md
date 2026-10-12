---
title: New Resume Analyser Backend
emoji: 👀
colorFrom: yellow
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
---

# Resume Analyzer Backend (LLM-only, embedding-free)

FastAPI backend that analyzes a resume PDF against a job-description PDF using
**Gemini LLM evaluation + deterministic Python scoring**. No local embedding
model is downloaded or required at startup.

## Architecture changes (refactor summary)

- **Removed from scoring pipeline:** `sentence-transformers`, `torch`,
  `scikit-learn`, `chromadb`, `rapidfuzz` semantic matching, cosine similarity,
  `SentenceTransformer(...)` model loads in `services/scoring.py` and
  `rule_matcher.py`.
- **New LLM evaluation:** `services/evaluation.py` asks Gemini for structured
   JSON scores (experience / projects / education / JD relevance + evidence),
   validated with Pydantic. Invalid JSON, empty responses, timeouts, rate limits
   raise a clear error (HTTP 502) instead of hiding behind fake zero scores.
- **Deterministic scoring:** `services/scoring.py` computes the final score in
  plain Python (see formula below). Skills use `rule_matcher.py` exact
  alias-map + word-boundary matching (full / partial / missing).
- **CareerBuddy RAG preserved without embeddings:**
  `Career_Buddy_rag/embeddings_store.py` keeps the same class/method API but is
  now an in-memory **keyword** index over the bundled `database/` files. No
  ChromaDB, no model download. Chat endpoints unchanged.
- **Lazy chat init:** `services/chat_service.py` no longer constructs the brain
  at import time, so `import main` starts fast and never pulls models.
- **Upload hardening:** `services/pdf_service.py` validates PDF magic bytes,
  size limits, empty/scanned PDFs with clear 400 errors.

## Scoring formula

```
final = 0.35*required_skills + 0.25*experience(LLM)
      + 0.15*projects(LLM) + 0.10*education(LLM) + 0.15*jd_relevance(LLM)
if keyword stuffing detected: final *= 0.80   (documented 20% penalty)
```

- `required_skills` 0–100 from deterministic matching:
  `group = (full + 0.5*partial) / total * 100`.
- Contextual categories are validated LLM 0–100 scores with evidence.
- Preferred skills are shown but do **not** affect the final score
  (avoids double-counting; documented).
- Verdicts: ≥80 Strong Match, ≥65 Good Match, ≥45 Moderate Match, else Low Match.

## API

- `GET /` — status
- `GET /health` and `GET /api/health` — health checks
- `POST /classify/` — form file `file` (PDF)
- `POST /analyze/` — form files `resume`, `jd` (PDFs), optional `debug=true`
- `POST /api/chat` — `{"message": "...", "use_web_search": false}`
- `POST /api/chat/clear` — clear history
- Swagger: `/docs`

## Local setup

```bash
git clone https://github.com/Chittransh-89/New_Resume_analyser_backend.git
cd New_Resume_analyser_backend
python -m venv .venv
# Windows: .venv\Scripts\activate | Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then set GEMINI_API_KEY
uvicorn main:app --reload --port 8000
```

## Environment variables

| Var | Purpose |
|---|---|
| `GEMINI_API_KEY` | Gemini auth (required for evaluation; never commit) |
| `LLM_MODEL` | default `gemini-3.5-flash-lite` |
| `BASE_URL` | OpenAI-compatible base URL for Gemini |
| `PORT` | server port (Docker default 7860 for HF Spaces; local uvicorn default 8000) |
| `CORS_ORIGINS` | comma-separated origins, `*` for dev |

## Docker / Hugging Face Spaces (Docker)

```bash
docker build -t resume-analyzer-backend .
docker run -p 7860:7860 --env-file .env resume-analyzer-backend
# Another host / port: docker run -p 8000:8000 -e PORT=8000 --env-file .env resume-analyzer-backend
```

For a Docker Space: push this repo, set Space SDK to Docker, add
`GEMINI_API_KEY` as a Space secret. Health check path: `/health`.
No Windows paths, no local model files, no temp-file leaks (uploads stay in memory).

## Tests

```bash
pytest -q
```

LLM calls are mocked in unit tests. One live integration test is skipped
unless `GEMINI_API_KEY` + `RUN_LIVE_TESTS=1` are set.

## Limitations

- Scanned/image-only PDFs return a clear 400 (OCR not bundled).
- LLM quality/quotas affect contextual scores; deterministic skills always work.
- CareerBuddy knowledge is the bundled static `database/` (keyword search, not semantic).
