# 📄 Resume Analyzer Backend — AI-Powered ATS Pipeline

> A production-grade FastAPI backend that analyzes resumes against job descriptions using **Gemini AI**, **Sentence Transformers**, and a **custom ATS scoring engine** with anti-keyword-stuffing detection.

---

## 🚀 Features

| Feature | Description |
|---|---|
| 📑 **Document Classification** | Auto-detects Resume vs Job Description vs Notes using LLM |
| 🧠 **Semantic Scoring** | Section-to-section similarity using Sentence Transformers with calibrated curves |
| 🎯 **Skills Matching** | Rule-based skill extraction with synonym/variant mapping (`SKILLS_MAP`) |
| 🛡️ **Anti-Spam Detection** | Penalizes keyword-stuffed resumes (density > 35% triggers 20% penalty) |
| ✍️ **Bullet Improvement** | AI-powered rewrite of resume bullets aligned to JD requirements |
| 📊 **HR Review** | LLM-generated strengths, weaknesses, and hiring verdict |
| ⚡ **Parallel Pipeline** | Async execution with `asyncio.gather` — full analysis in ~4-6 seconds |
| 🔧 **Self-Healing JSON** | 3-level JSON repair (standard → regex → ast) for unreliable LLM outputs |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Client (Frontend)                  │
│              POST /analyze/ (Resume + JD)            │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│              FastAPI Router (analyze.py)             │
│         Async orchestration + Error handling         │
└──┬───────────┬───────────┬───────────┬──────────────┘
   │           │           │           │
   ▼           ▼           ▼           ▼
┌──────┐  ┌────────┐  ┌────────┐  ┌──────────┐
│ PDF  │  │Classify│  │ Parser │  │ Scoring  │
│Service│  │  (LLM) │  │ (LLM)  │  │ Engine   │
│(fitz)│  │        │  │        │  │          │
└──────┘  └────────┘  └────────┘  └────┬─────┘
                                       │
                              ┌────────┴────────┐
                              │                 │
                        ┌─────▼─────┐    ┌──────▼──────┐
                        │  Skills   │    │  Semantic   │
                        │  Matcher  │    │  (SBERT)    │
                        │ (Regex)   │    │  Cosine Sim │
                        └─────┬─────┘    └──────┬──────┘
                              │                 │
                              └────────┬────────┘
                                       ▼
                              ┌────────────────┐
                              │  Final Score   │
                              │  + Gating      │
                              │  + Calibration │
                              └────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Framework** | FastAPI + Uvicorn |
| **LLM** | Google Gemini 2.5 Flash (`google-genai` SDK) |
| **Embeddings** | Sentence Transformers (`intfloat/e5-base-v2`) |
| **PDF Parsing** | PyMuPDF (primary) + pdfplumber (fallback) |
| **Similarity** | scikit-learn (Cosine Similarity) |
| **Language** | Python 3.11+ |

---

## 📁 Project Structure

```
NEW_RESUME_ANALYSER_BACKEND/
├── .env.example              # Environment variables template
├── config.py                 # Loads .env into app config
├── main.py                   # FastAPI app entry point + CORS
├── requirements.txt          # Python dependencies
│
├── routers/                  # HTTP Route Handlers
│   ├── analyze.py            # POST /analyze/ — Full pipeline
│   └── classify.py           # POST /classify/ — Quick doc check
│
├── services/                 # Business Logic Layer
│   ├── llm_service.py        # Gemini SDK client + JSON repair
│   ├── parser.py             # Resume & JD → Structured JSON
│   ├── classifier.py         # Document type + role detection
│   ├── pdf_service.py        # PDF → Plain text extraction
│   ├── scoring.py            # ATS scoring engine + embeddings
│   ├── bullets.py            # Bullet extraction + AI improvement
│   ├── skills_map.py         # Skill synonyms & variants dictionary
│   └── rule_matcher.py       # Rule-based skill matching logic
│
└── prompts/                  # LLM Prompt Templates
    └── improve_bullets_prompt.txt
```

---

## ⚙️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/Chittransh-89/New_Resume_analyser_backend.git
cd New_Resume_analyser_backend
```

### 2. Create Virtual Environment
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
```bash
cp .env.example .env
```

Edit `.env` with your credentials:
```env
GOOGLE_API_KEY=your_gemini_api_key_here
LLM_MODEL=gemini-2.5-flash
EMBEDDING_MODEL=intfloat/e5-base-v2
```

> 🔑 Get your free Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey)

### 5. Run the Server
```bash
uvicorn main:app --reload
```

Server starts at **http://127.0.0.1:8000**

📖 Interactive API Docs: **http://127.0.0.1:8000/docs**

---

## 📡 API Endpoints

### `POST /analyze/`
Full resume analysis pipeline.

**Request:** `multipart/form-data`
| Field | Type | Required | Description |
|---|---|---|---|
| `resume` | File (PDF) | ✅ | Candidate's resume |
| `jd` | File (PDF) | ✅ | Job description |
| `debug` | Boolean | ❌ | Enable debug mode |

**Response:**
```json
{
  "document_validation": {
    "resume_roles": ["SOFTWARE_ENGINEER"],
    "jd_roles": ["BACKEND_DEVELOPER"],
    "role_match": true
  },
  "candidate": {
    "name": "John Doe",
    "email": "john@example.com",
    "experience_years": 3,
    "projects_count": 4
  },
  "job_needs": {
    "title": "Backend Developer",
    "required_skills": ["Python", "FastAPI", "PostgreSQL"],
    "preferred_skills": ["Docker", "AWS"]
  },
  "analysis": {
    "matched_skills": ["Python", "FastAPI"],
    "missing_skills": ["PostgreSQL"],
    "semantic_score": 72.45
  },
  "score": {
    "final_score": 68.5,
    "verdict": "Good Match"
  },
  "review": {
    "verdict": "Good Match",
    "strengths": ["Strong Python experience", "Relevant project work"],
    "weaknesses": ["Missing PostgreSQL experience"],
    "reason": "Candidate meets 70% of requirements..."
  },
  "improvements": {
    "line_by_line": [
      {
        "original": "Worked on backend APIs",
        "improved": "Designed and deployed RESTful APIs serving 10K+ daily requests using FastAPI",
        "changed": true
      }
    ],
    "top_suggestions": ["..."],
    "summary": {
      "total_bullets": 5,
      "improved_count": 3
    }
  }
}
```

### `POST /classify/`
Quick document type classification.

**Response:**
```json
{
  "document_a": {
    "type": "RESUME",
    "job_role": "SOFTWARE_ENGINEER",
    "confidence": 0.95
  },
  "document_b": {
    "type": "JOB_DESCRIPTION",
    "job_role": "BACKEND_DEVELOPER",
    "confidence": 0.91
  }
}
```

---

## 📊 Scoring Pipeline — How It Works

### Step 1: Skills Matching (Rule-Based)
- Extracts skills from resume using `SKILLS_MAP` (synonym-aware regex)
- Compares against JD required + preferred skills
- Outputs: `matched_required`, `missing_required`, `skill_score`

### Step 2: Semantic Scoring (AI Embeddings)
- Compares resume sections against **relevant** JD sections:
  - Resume Skills ↔ JD Skills (weight: 35%)
  - Resume Experience ↔ JD Responsibilities (weight: 30%)
  - Resume Projects ↔ JD Requirements (weight: 25%)
  - Resume Education ↔ JD Education (weight: 10%)
- Uses **calibrated similarity curve** to prevent score inflation:
  - Raw 0.50 → ~45% (Below Average)
  - Raw 0.75 → ~72% (Good)
  - Raw 0.90 → ~90%+ (Excellent)

### Step 3: Final Score with Gating Rules
```
Final = (55% × Semantic) + (45% × Skills)
```
**Hard Gating:**
| Condition | Effect |
|---|---|
| Required skills < 40% met | Score capped at 45% |
| Required skills < 60% met | Score capped at 65% |
| No experience section | Score capped at 50% |
| No projects section | Score capped at 55% |
| Keyword stuffing detected | 20% penalty applied |

### Verdict Scale
| Score | Verdict |
|---|---|
| 80%+ | 🟢 Strong Match |
| 65-79% | 🔵 Good Match |
| 45-64% | 🟡 Moderate Match |
| <45% | 🔴 Low Match |

---

## 🛡️ Reliability Features

- **3-Level JSON Repair:** LLM responses auto-fixed via `json.loads` → regex cleanup → `ast.literal_eval`
- **Graceful Fallbacks:** If Gemini rate-limits (429) or overloads (503), pipeline returns safe defaults instead of crashing
- **Model Preloading:** SentenceTransformer loads once at startup (~5s), then serves instant embeddings
- **Batch Encoding:** All section comparisons encoded in 2 calls instead of 8
- **Bullet Limiting:** Top 8 bullets processed to stay within API rate limits

---

## 📝 Notes

- **Gemini Free Tier:** ~15 RPM limit. The pipeline is optimized for 4-5 calls per request.
- **First Request:** Takes ~8-10 seconds (model warm-up). Subsequent requests: ~4-6 seconds.
- **PDF Support:** Works best with text-based PDFs. Scanned/image PDFs may need OCR (future enhancement).

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📜 License

This project is for educational and portfolio purposes.

---

## 👨‍💻 Author

**Chittransh** — [GitHub](https://github.com/Chittransh-89)

Built with ❤️ using FastAPI, Gemini AI & Sentence Transformers
