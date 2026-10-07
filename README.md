# 📄 Resume Analyzer Backend

> 🚀 AI-powered resume and job-description analysis backend built with FastAPI, Gemini, Sentence Transformers, rule-based skill matching, and ChromaDB-powered CareerBuddy RAG.

---

## 🌟 Overview

This repository contains the backend of an AI-powered **Resume Analyzer** application.

The backend combines **LLMs, semantic embeddings, deterministic rules, and RAG** to analyze a resume against a job description and provide actionable feedback.

### ✨ What it provides

- 📄 Resume PDF processing
- 📋 Job Description PDF processing
- 🔍 Document classification
- 🎯 ATS-style resume scoring
- 🧠 Semantic similarity analysis
- 🛠️ Skill extraction and matching
- ❌ Missing-skill detection
- 🤖 AI-generated HR review
- ✍️ Resume bullet improvement
- 💬 CareerBuddy AI career assistant
- 📚 ChromaDB-powered RAG
- 🧭 LLM-based query routing
- 🌐 Optional web-search support
- ⚡ FastAPI REST APIs
- 📖 Automatic Swagger documentation
- 🐳 Docker support

---

# 🏗️ System Architecture

```text
                         🌐 Frontend
                              |
                              v
                       ⚡ FastAPI
                         main.py
                              |
              +---------------+---------------+
              |               |               |
              v               v               v
        /classify/        /analyze/        /api/chat
              |               |               |
              v               v               v
       📋 Classification   📄 Analysis     🤖 CareerBuddy
                              |               |
               +--------------+-------+       |
               |              |       |       |
               v              v       v       v
          PDF Extraction   LLM Parser  ATS  Query Router
                                             |
                                      +------+------+
                                      |             |
                                      v             v
                                  📚 ChromaDB    🌐 Web Search
```

---

# 🔄 Resume Analysis Flow

```text
📄 Resume PDF + 📋 Job Description PDF
                    |
                    v
             📑 PDF Extraction
                    |
                    v
          🔍 Document Validation
                    |
                    v
        🤖 Resume + JD Parsing
                    |
          +---------+---------+
          |                   |
          v                   v
   🛠️ Skill Extraction    📊 Structured Data
          |                   |
          v                   v
   🎯 Skill Matching      🧠 Semantic Scoring
          |                   |
          +---------+---------+
                    |
                    v
             🎯 Final ATS Score
                    |
             +------+------+
             |             |
             v             v
       🤖 HR Review    ✍️ Bullet Improvement
             |             |
             +------+------+
                    |
                    v
             📦 JSON Response
```

---

# 📂 Project Structure

```text
New_Resume_analyser_backend/
│
├── main.py
├── config.py
├── logger_config.py
├── rule_matcher.py
├── skills_map.py
├── requirements.txt
├── DockerFile
├── .env.example
├── .gitignore
│
├── routers/
│   ├── analyze.py
│   ├── classify.py
│   └── chat.py
│
├── services/
│   ├── pdf_service.py
│   ├── parser.py
│   ├── classifier.py
│   ├── scoring.py
│   ├── bullets.py
│   ├── llm_service.py
│   ├── chat_service.py
│   └── web_search.py
│
├── prompts/
│   ├── SYSTEM_PROMPT.txt
│   ├── QUESTION_TYPE_DETECTION_PROMPT.txt
│   ├── query_router_system_prompt.txt
│   ├── review_prompt.txt
│   └── improve_bullets_prompt.txt
│
└── Career_Buddy_rag/
    ├── embeddings_store.py
    ├── new_brain.py
    ├── query_router.py
    │
    └── database/
        ├── career_database/
        │   └── career_data.py
        │
        ├── skills_database/
        │   └── skills_data.py
        │
        └── resources_database/
            └── resources_data.py
```

---

# 🧩 Component Responsibilities

## 🚀 Application Layer

### `main.py`

Creates the FastAPI application, configures CORS, registers routers, and exposes the root endpoint.

---

# 🛣️ Router Layer

### `routers/analyze.py`

Orchestrates the complete resume-versus-job-description analysis workflow.

### `routers/classify.py`

Handles PDF document classification.

### `routers/chat.py`

Provides CareerBuddy chat, conversation reset, and health endpoints.

---

# ⚙️ Service Layer

### `services/pdf_service.py`

Extracts PDF text using PyMuPDF first and pdfplumber as a fallback.

### `services/parser.py`

Uses the LLM to convert resume and job-description text into structured information.

### `services/classifier.py`

Handles document type and job-role classification.

### `services/scoring.py`

Responsible for:

- 🛠️ Skill extraction
- 🎯 Skill matching
- 🧠 Semantic scoring
- 📊 Final ATS score calculation

### `services/bullets.py`

Extracts resume bullets and generates improved versions.

### `services/llm_service.py`

Centralizes LLM communication and JSON response repair.

Development can use Ollama while deployment can use Gemini.

### `services/chat_service.py`

Connects the API layer with CareerBuddy.

### `services/web_search.py`

Generates Google and YouTube search links when web retrieval is requested.

---

# 🤖 CareerBuddy RAG

CareerBuddy is the AI career-assistant component of the backend.

It combines:

- 🧭 Query routing
- 📚 ChromaDB retrieval
- 🧠 Embeddings
- 🤖 LLM generation
- 💬 Conversation history
- 🌐 Optional web search

### `Career_Buddy_rag/embeddings_store.py`

Builds and queries the ChromaDB career knowledge base.

### `Career_Buddy_rag/query_router.py`

Determines which retrieval strategy should be used for a user query.

### `Career_Buddy_rag/new_brain.py`

Acts as the main CareerBuddy orchestration layer.

It combines routing, retrieval, optional web context, LLM generation, conversation history, and response cleanup.

---

# 🧭 CareerBuddy Query Routing

CareerBuddy does not retrieve documents for every question.

The query router classifies requests into four paths:

| Intent | 📚 ChromaDB | 🌐 Web |
|---|---:|---:|
| `casual` | ❌ | ❌ |
| `rag` | ✅ | ❌ |
| `rag_web` | ✅ | ✅ |
| `off_topic` | ❌ | ❌ |

This reduces unnecessary retrieval and makes the assistant's behavior more predictable.

---

# 📚 Career Knowledge Base

The CareerBuddy knowledge base contains information related to:

- 💼 Career paths
- 🛠️ Technical skills
- 🎓 Learning platforms
- ▶️ YouTube channels
- 💻 Interview resources
- 👥 Developer communities

The information is embedded and stored in ChromaDB for semantic retrieval.

---

# 🎯 ATS Scoring Pipeline

## 1️⃣ Skill Extraction

Resume text is normalized and matched against the project's canonical skills map.

Known skill variants are mapped to canonical skills before comparison with required and preferred job-description skills.

---

## 2️⃣ Semantic Scoring

Sentence Transformers generate embeddings for relevant resume and job-description sections.

Cosine similarity is used to measure semantic alignment.

The scoring system considers areas such as:

- 🛠️ Skills
- 💼 Experience and responsibilities
- 🚀 Projects and requirements
- 🎓 Education and qualifications

The raw similarity is calibrated before contributing to the final score.

---

## 3️⃣ Final Score

The final score combines:

- 🎯 Deterministic skill matching
- 🧠 Semantic relevance

The scoring engine also contains gating rules for situations such as:

- Low required-skill coverage
- Missing experience information
- Missing project information
- Keyword stuffing

This prevents semantic similarity alone from producing an unrealistically high ATS score.

---

# 🤖 LLM Reliability

LLM responses are treated as potentially imperfect.

The LLM service includes JSON repair logic for common malformed responses.

The analysis pipeline also contains fallback behavior so that selected LLM failures do not automatically destroy the complete analysis.

Where possible, deterministic scoring information can still be returned when generated content fails.

---

# 🔌 API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/` | 🚀 API status |
| `GET` | `/api/health` | ❤️ Backend health |
| `POST` | `/classify/` | 📋 Classify a PDF |
| `POST` | `/analyze/` | 📄 Analyze resume against JD |
| `POST` | `/api/chat` | 🤖 CareerBuddy chat |
| `POST` | `/api/chat/clear` | 🧹 Clear conversation |

FastAPI automatically provides interactive API documentation.

### 📖 Swagger UI

```text
/docs
```

---

# 📄 Resume Analysis API

## `POST /analyze/`

Accepts:

- `resume` → Resume PDF
- `jd` → Job Description PDF
- `debug` → Optional debug flag

### Example

```text
curl -X POST "http://127.0.0.1:8000/analyze/" ^
  -F "resume=@resume.pdf" ^
  -F "jd=@job_description.pdf"
```

The response contains information such as:

- 📋 Document validation
- 👤 Candidate information
- 💼 Job requirements
- 🛠️ Matched skills
- ❌ Missing skills
- 🧠 Semantic score
- 🎯 Final score
- 🏆 Verdict
- 🤖 HR review
- ✍️ Improved resume bullets

### Example Response

```json
{
  "document_validation": {
    "resume_roles": [],
    "jd_roles": [],
    "role_match": true
  },
  "candidate": {
    "name": "Candidate Name",
    "email": "candidate@example.com",
    "experience_years": 2,
    "projects_count": 3
  },
  "job_needs": {
    "title": "AI Engineer",
    "required_skills": [],
    "preferred_skills": []
  },
  "analysis": {
    "matched_skills": [],
    "missing_skills": [],
    "semantic_score": 0
  },
  "score": {
    "final_score": 0,
    "verdict": "REVIEW_REQUIRED"
  }
}
```

---

# 💬 CareerBuddy API

## `POST /api/chat`

Example request:

```json
{
  "message": "What skills do I need to become an AI Engineer?",
  "use_web_search": false
}
```

The query router determines whether the request needs:

- ❌ No retrieval
- 📚 ChromaDB RAG
- 📚 ChromaDB + 🌐 web search
- 🚫 No retrieval for unsupported/off-topic queries

---

## `POST /api/chat/clear`

Clears the current CareerBuddy conversation history.

---

## `GET /api/health`

Example response:

```json
{
  "status": "online",
  "name": "CareerBuddy AI",
  "brain_loaded": true
}
```

---

# 🛠️ Technology Stack

| Component | Technology |
|---|---|
| ⚡ Backend | FastAPI |
| 🚀 ASGI Server | Uvicorn |
| 🤖 LLM | Google Gemini |
| 🧪 Development LLM | Ollama |
| 🧠 Embeddings | Sentence Transformers |
| 📚 Vector Database | ChromaDB |
| 📐 Similarity | scikit-learn cosine similarity |
| 📄 PDF Extraction | PyMuPDF + pdfplumber fallback |
| 🐍 Language | Python |
| 🐳 Containerization | Docker |

---

# ⚙️ Configuration

Configuration is centralized in `config.py`.

Important environment variables include:

| Variable | Purpose |
|---|---|
| `GEMINI_API_KEY` | 🔑 Gemini API authentication |
| `LLM_MODEL` | 🤖 LLM model name |
| `BASE_URL` | 🌐 LLM API base URL when applicable |
| `EMBEDDING_MODEL` | 🧠 Sentence Transformer model |
| `CORS_ORIGINS` | 🌍 Allowed frontend origins |

⚠️ **Never commit real API keys or credentials.**

Use `.env.example` as the configuration reference.

---

# 🚀 Local Setup

## 1️⃣ Clone the Repository

```bash
git clone https://github.com/Chittransh-89/New_Resume_analyser_backend.git
cd New_Resume_analyser_backend
```

## 2️⃣ Create a Virtual Environment

### Windows

```text
python -m venv .venv
```

### Linux / macOS

```bash
python -m venv .venv
source .venv/bin/activate
```

Activate the environment using the method supported by your shell.

---

## 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4️⃣ Configure Environment Variables

Create a `.env` file using `.env.example` as a reference.

Add the required API and model configuration.

---

## 5️⃣ Start FastAPI

```bash
uvicorn main:app --reload --port 8000
```

The API will be available at:

```text
http://127.0.0.1:8000
```

### 📖 Swagger Documentation

```text
http://127.0.0.1:8000/docs
```

---

# 🐳 Docker

A Dockerfile is included for container-based deployment.

### Build

```bash
docker build -f DockerFile -t resume-analyzer-backend .
```

### Run

```bash
docker run -p 8000:8000 --env-file .env resume-analyzer-backend
```

---

# 🌐 Frontend Integration

The backend is designed to work with a separate frontend.

```text
             🌐 Frontend
                  |
                  | HTTPS API
                  v
          ⚡ FastAPI Backend
                  |
        +---------+---------+
        |         |         |
        v         v         v
    📄 Resume   🎯 ATS   🤖 CareerBuddy
    Analysis    Scoring       |
                             |
                    +--------+--------+
                    |                 |
                    v                 v
                 📚 RAG           🌐 Web
                ChromaDB         Search
```

For local development, the backend runs on port `8000`.

For deployment, the frontend should use the public HTTPS URL of the backend.

---

# 🧠 Design Decisions

## Why FastAPI?

FastAPI provides:

- ⚡ High-performance API handling
- 📖 Automatic OpenAPI documentation
- 🧩 Typed request handling
- 📄 File upload support
- 🔌 Easy frontend integration

---

## Why combine Rules, Embeddings and LLMs?

A single technique is not ideal for the complete problem.

### 🤖 LLM

Used for:

- Understanding unstructured documents
- Structured extraction
- HR-style explanations
- Resume bullet improvement

### 📐 Embeddings

Used for:

- Semantic similarity
- Resume and JD relevance

### 📊 Rules

Used for:

- Skill matching
- Canonical skill normalization
- Score constraints
- Gating logic

This creates a more reliable hybrid analysis pipeline.

---

## Why ChromaDB?

CareerBuddy requires retrieval over a structured career knowledge base.

ChromaDB provides persistent local vector storage without requiring a separate database server.

---

## Why a Query Router?

Not every user question needs RAG.

The query router decides whether a request should use:

```text
Casual
  ↓
No retrieval

RAG
  ↓
ChromaDB

RAG + Web
  ↓
ChromaDB + Web Search

Off-topic
  ↓
No retrieval
```

This avoids unnecessary retrieval and external searches.

---

# ⚠️ Current Limitations

- 📷 Scanned image-only PDFs may require OCR.
- 🤖 LLM availability and provider rate limits can affect generated analysis.
- 📚 Local ChromaDB storage is not a distributed production database.
- 🧠 The embedding model is loaded into memory by the scoring service.
- 🔐 Public deployment requires environment variables and model dependencies to be configured correctly.
- 🌍 CORS is currently broad for development and frontend integration. Production deployments should restrict allowed origins to trusted frontend domains.

---

# 🔐 Security Notes

Never commit:

- 🔑 Gemini API keys
- 🔐 GitHub tokens
- `.env` files
- 🔒 Private credentials
- 📚 Local vector database files

The local ChromaDB directory is ignored so generated vector-store files are not committed to Git history.

---

# 🔗 Repository

GitHub:

https://github.com/Chittransh-89/New_Resume_analyser_backend

---

# 👨‍💻 Author

**Chittransh Verma**

Built with ❤️ using:

**FastAPI + Gemini + Sentence Transformers + ChromaDB + Python**

---

# 📜 License

This project is intended for educational, portfolio, and experimentation purposes.
