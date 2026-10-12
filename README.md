# 🚀 AI Resume Analyzer & CareerBuddy 

An AI-powered resume analysis backend built with **FastAPI, Python, and Google Gemini**. Compare a resume against a job description, identify skill gaps, evaluate job fit, and get actionable suggestions to improve resume bullet points.

🎯 **Goal:** Make resume evaluation smarter, faster, and easier to understand.

## ✨ Features

- 📄 **Resume & Job Description Analysis** — Upload PDF files and evaluate how well the candidate matches the target role.
- 🧠 **AI-Powered Evaluation** — Uses Google Gemini to assess experience, projects, education, and job-description relevance.
- 🛠️ **Skill Matching** — Identifies matched and missing required skills using Python-based keyword and alias matching.
- 📊 **Weighted Resume Score** — Combines skill matching and contextual AI evaluation into a score out of 100.
- 📝 **Resume Bullet Improvement** — Suggests improved versions of resume bullet points.
- 🎯 **Candidate & Role Validation** — Checks document types and compares detected job roles.
- 💬 **CareerBuddy Chat API** — Provides a career assistant backed by a bundled knowledge base and keyword-based retrieval.
- ⚡ **Embedding-Free Scoring** — No local sentence-transformer model or embedding download is needed for the resume-scoring pipeline.
- 🔒 **PDF Validation** — Checks uploaded files and handles invalid or unreadable PDFs.
- 🐳 **Docker Ready** — Includes a Dockerfile configured for deployment on Hugging Face Spaces.
- 🧪 **Automated Tests** — Includes tests for API endpoints, PDF handling, scoring, and embedding-free behavior.

## 🏗️ Tech Stack

| Technology | Purpose |
|---|---|
| 🐍 Python | Backend logic |
| ⚡ FastAPI | REST API framework |
| 🤖 Google Gemini | AI-based evaluation and generation |
| 📄 PyMuPDF & pdfplumber | PDF text extraction |
| ✅ Pydantic | Validation of structured AI evaluation |
| 🧪 pytest | Automated testing |
| 🐳 Docker | Containerization and deployment |
| 🔎 Python keyword matching | Deterministic skill matching and knowledge retrieval |

## 🧮 How Resume Scoring Works

The final score combines deterministic required-skill matching with AI evaluation.

| Category | Weight |
|---|---:|
| 🛠️ Required Skills | 35% |
| 💼 Experience | 25% |
| 🚀 Projects | 15% |
| 🎓 Education | 10% |
| 🎯 Job Description Relevance | 15% |
| **Total** | **100%** |

The scoring formula is:

```text
Final Score =
    0.35 × Required Skills
  + 0.25 × Experience
  + 0.15 × Projects
  + 0.10 × Education
  + 0.15 × Job Relevance
```

If keyword stuffing is detected, the implementation applies a 20% penalty to the calculated score.

### 🏆 Match Categories

- 🟢 **Strong Match:** 80–100
- 🔵 **Good Match:** 65–79.99
- 🟡 **Moderate Match:** 45–64.99
- 🔴 **Low Match:** Below 45

Required skills are matched using Python rules, while experience, projects, education, and job relevance are evaluated by Gemini. Preferred skills are provided as feedback but do not directly contribute to the weighted score.

*Note: The AI-generated evaluation is an automated aid, not a guarantee of hiring success or a substitute for human review.*

## 🔄 How It Works

1. 📤 Upload a resume PDF and a job-description PDF.
2. 📄 Extract text from both documents.
3. 🔍 Validate the documents and identify their types.
4. 🧠 Parse relevant candidate and job information.
5. 🛠️ Match required and preferred skills.
6. 📊 Calculate the weighted score using skill matching and AI evaluation.
7. ✍️ Generate a review and resume bullet-point suggestions.
8. 📦 Return the results as a JSON response.

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | API status and useful links |
| `GET` | `/health` | Basic health check |
| `GET` | `/api/health` | CareerBuddy health information |
| `POST` | `/classify/` | Classify a PDF document |
| `POST` | `/analyze/` | Analyze a resume against a job description |
| `POST` | `/api/chat` | Send a message to CareerBuddy |
| `POST` | `/api/chat/clear` | Clear chat history |

📚 **Interactive API documentation:** Open `/docs` after starting the server.

### 📤 Resume Analysis Request

The `/analyze/` endpoint expects two PDF files as multipart form data:

- `resume` — The candidate's resume PDF
- `jd` — The job description PDF
- `debug` — Optional boolean parameter

Example response structure:

```json
{
  "document_validation": {},
  "candidate": {},
  "job_needs": {},
  "analysis": {},
  "score": {},
  "review": {},
  "improvements": []
}
```

The actual response contains the extracted information, skill matches, score breakdown, review, and available improvement suggestions.

### 💬 CareerBuddy Chat Request

Endpoint: `POST /api/chat`

```json
{
  "message": "How can I improve my backend development skills?",
  "use_web_search": false
}
```

## 🛠️ Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/Chittransh-89/New_Resume_analyser_backend.git
cd New_Resume_analyser_backend
```

### 2. Create a Virtual Environment

**Windows PowerShell**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux / macOS**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root using `.env.example` as a template.

```env
GEMINI_API_KEY=your_gemini_api_key
LLM_MODEL=gemini-3.5-flash-lite
BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
PORT=8000
CORS_ORIGINS=*
```

🔑 Get your Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey).

**Important:** Replace the example API key with your own. Never commit your real API key or `.env` file to GitHub.

For production, configure `CORS_ORIGINS` to allow only your trusted frontend origins instead of using `*`.

### 5. Start the Server

```bash
uvicorn main:app --reload --port 8000
```

The API should now be available at:

- 🏠 API root: `http://127.0.0.1:8000/`
- ❤️ Health check: `http://127.0.0.1:8000/health`
- 📚 Swagger documentation: `http://127.0.0.1:8000/docs`

## 🧪 Running Tests

Run the automated test suite from the project root:

```bash
pytest -q
```

Tests cover important API behavior, PDF validation, mocked resume-analysis flows, scoring behavior, and checks against embedding-model dependencies in the scoring pipeline.

AI calls are mocked in relevant tests, so passing unit tests does not necessarily verify live Gemini API access. Configure your API key and perform a real analysis to check the full integration.

## 🐳 Docker Deployment

### Build the Image

```bash
docker build -t resume-analyzer-backend .
```

### Run the Container

Make sure your `.env` file is configured, then run:

```bash
docker run --env-file .env -p 7860:7860 resume-analyzer-backend
```

Open `http://127.0.0.1:7860/health` to check the health endpoint.

## ☁️ Deploy on Hugging Face Spaces

This repository includes a Dockerfile configured to use port `7860`.

1. 🚀 Create a new Space on [Hugging Face](https://huggingface.co/spaces).
2. 🐳 Select **Docker** as the Space SDK.
3. 📤 Push the repository code to the Space.
4. 🔑 Add `GEMINI_API_KEY` under the Space's Secrets settings.
5. ⚙️ Add other required environment variables if needed.
6. 📋 Check the Space build logs and runtime logs.
7. ❤️ Verify the `/health` endpoint.
8. 📄 Test `/docs` and upload sample PDFs through `/analyze/`.

**Deployment note:** A successful health check confirms that the application responds. It does not, by itself, prove that Gemini credentials or the full resume-analysis flow are working.

## 📁 Project Structure

```text
New_Resume_analyser_backend/
│
├── Career_Buddy_rag/       # CareerBuddy knowledge retrieval
├── routers/                # FastAPI route handlers
├── services/               # Analysis, scoring, PDF and LLM logic
├── prompts/                # AI prompt templates
├── tests/                  # Automated tests
├── database/               # Bundled knowledge-base data
├── main.py                 # FastAPI application entry point
├── config.py               # Application configuration
├── rule_matcher.py         # Rule-based skill matching
├── skills_map.py           # Skill names and aliases
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker configuration
├── .env.example            # Environment template
└── README.md               # Project documentation
```

## ⚠️ Limitations

- 📷 Scanned or image-only PDFs may not produce usable text. OCR is not bundled.
- 🤖 AI evaluation depends on Gemini availability, quotas, response quality, and API configuration.
- 🔎 Skill matching uses defined keywords and aliases, so context and unfamiliar skill names may affect results.
- 📚 CareerBuddy retrieval uses the bundled knowledge base and keyword-based search rather than semantic embeddings.
- 🧑‍⚖️ Resume scores are estimates and should not be treated as the sole basis for hiring decisions.

## 🔐 Security Notes

- Keep API keys in environment variables or your deployment provider's secret manager.
- Never upload real secrets to a public repository.
- Configure CORS carefully before exposing the API publicly.
- Use appropriate upload limits and monitor API usage and logs in production.

## 🎯 Project Goals

This project explores how a practical resume-analysis system can combine:

- 🧠 Large language models for contextual evaluation
- 🐍 Fundamental Python logic for deterministic scoring
- ⚡ FastAPI for clean API integration
- 🔎 Keyword-based retrieval without local embedding models
- 🐳 Docker for portable deployment

## 👨‍💻 Author

**Chittransh Verma**

GitHub: [@Chittransh-89](https://github.com/Chittransh-89)

⭐ If you find this project useful, consider giving the repository a star!

---

💡 **Built with Python, FastAPI, and Gemini — helping turn resumes into actionable insights.**