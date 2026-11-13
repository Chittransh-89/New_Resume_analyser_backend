---
title: New Resume Analyser CareerBuddy
emoji: 📄
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
---

# 🚀 CareerBuddy AI – AI-Powered Resume Analyzer & Career Assistant

**CareerBuddy AI** is an AI-powered career assistance platform designed to help students and job seekers improve their resumes, identify skill gaps, and make better career decisions.

It combines intelligent resume analysis with an AI-powered career assistant to provide actionable feedback and career guidance in one platform.

🎯 **Project Type:** Individual Project  
👨‍💻 **Developer:** Chittransh Verma  
🎓 **Course:** B.Tech Computer Science Engineering  
🏫 **College:** HCST

---

## 🌟 Key Features

### 📄 1. AI Resume Analyzer
- Upload resumes in PDF format.
- Extracts and processes resume information.
- Analyzes resumes against job descriptions.
- Identifies strengths and weaknesses.
- Detects missing or relevant skills.
- Generates actionable improvement suggestions.
- Provides improved resume bullet points.

### 🎯 2. Intelligent Resume Scoring
Evaluates candidates using a weighted scoring methodology.

| Evaluation Criteria | Weight |
|---|---:|
| Required Skills | 35% |
| Experience | 25% |
| Projects | 15% |
| Education | 10% |
| Job Relevance | 15% |
| **Total** | **100%** |

Additional evaluation:
- Rule-based skill matching.
- LLM-based contextual evaluation.
- Keyword stuffing detection with a documented score penalty when triggered.
- Overall match score and verdict.

### 🤖 3. AI Career Assistant

CareerBuddy includes an AI-powered conversational assistant that helps users explore career-related topics.

It can help with:
- Career path exploration.
- Technical skill guidance.
- Learning roadmaps.
- Interview preparation resources.
- Career-related questions.
- Learning platform recommendations.

### 🧠 4. Retrieval-Augmented Generation (RAG)

The Career Assistant uses a built-in career knowledge base.

The knowledge base contains:
- Career paths.
- Technical skills.
- Learning roadmaps.
- Learning platforms.
- YouTube channels.
- Interview preparation resources.
- Developer communities.

**Retrieval implementation:**
- Keyword-based document retrieval.
- Relevant context selection.
- Context-aware Gemini responses.
- Query routing for different types of user questions.

Note: The current lightweight implementation uses deterministic keyword-based retrieval, not vector embeddings or ChromaDB.

### 🔎 5. Learning Resource Discovery

CareerBuddy can generate useful search links for:
- Google learning resources.
- YouTube tutorials.
- Programming roadmaps.
- Free courses.
- Practice questions.
- Technical projects.

---

## ⚙️ Technology Stack

| Category | Technologies |
|---|---|
| Programming Language | Python |
| Backend Framework | FastAPI |
| AI / LLM | Google Gemini API |
| Local Development LLM | Ollama |
| PDF Processing | PyMuPDF, pdfplumber |
| Data Validation | Pydantic |
| Resume Intelligence | Custom Python logic |
| Skill Matching | Rule-Based Matching |
| Resume Evaluation | Weighted Scoring + LLM |
| Career Assistant | RAG, Query Router |
| Knowledge Retrieval | Keyword-Based Retrieval |
| Web Resources | Google Search Links, YouTube Search Links |
| Containerization | Docker |
| Deployment | Hugging Face Spaces, Vercel |

---

## 🏗️ System Architecture

CareerBuddy AI consists of two primary modules.

### Module 1: Resume Analyzer

```text
       User Upload
            |
            v
    Resume PDF + Job Description
            |
            v
      PDF Text Extraction
            |
            v
    Document Processing
            |
            v
   Gemini-based Parsing
            |
            v
      Skill Extraction
            |
            v
   Skill Matching & Evaluation
            |
            v
     Weighted Scoring
            |
            v
      Final Analysis
            |
            v
  Feedback + Skill Gaps +
  Improvement Suggestions
```

### Module 2: Career Assistant

```text
       User Query
            |
            v
       Query Router
            |
     +------+------+
     |      |      |
     v      v      v
  Casual  Career  Career +
  Query   RAG     Web Search
     |      |      |
     +------+------+
            |
            v
   Relevant Context
            |
            v
       Gemini AI
            |
            v
   Context-aware Response
```

---

## 📊 Resume Evaluation Methodology

CareerBuddy evaluates resumes using multiple criteria.

**1. Required Skills – 35%**

Checks whether the candidate possesses the skills required by the job description.

**2. Experience – 25%**

Evaluates the candidate's relevant professional experience.

**3. Projects – 15%**

Considers the relevance of projects to the target role.

**4. Education – 10%**

Evaluates educational qualifications.

**5. Job Relevance – 15%**

Considers how well the candidate's profile aligns with the target job.

The evaluation combines deterministic matching logic and LLM-based contextual analysis.

---

## 🧠 Career Assistant – Query Routing

The Career Assistant uses a query router to determine how a question should be handled.

| Query Type | Function |
|---|---|
| Casual | Handles general conversational queries |
| RAG | Retrieves relevant career knowledge |
| RAG + Web | Combines career knowledge with search resources |
| Off-topic | Handles or redirects unrelated queries |

This architecture helps provide more relevant responses instead of treating every question as a resume-related query.

---

## 📁 Project Structure

The backend is organized into separate modules for API handling, resume processing, AI services, and career knowledge retrieval.

Main components include:

- `main.py` – Backend application entry point.
- `config.py` – Configuration management.
- `services/` – Resume processing and supporting services.
- `Career_Buddy_rag/` – Career Assistant and knowledge retrieval modules.
- `Career_Buddy_rag/database/` – Career, skills and learning resource knowledge base.
- `Dockerfile` – Container configuration.
- `requirements.txt` – Python dependencies.

---

## 🛠️ Installation & Local Setup

### Prerequisites

- Python 3.10 or compatible version.
- Git.
- Google Gemini API key.
- Docker (optional).

### Step 1: Clone the Repository

```bash
git clone -b mp https://github.com/Chittransh-89/New_Resume_analyser_backend.git

cd New_Resume_analyser_backend
```

### Step 2: Create a Virtual Environment

```bash
python -m venv venv
```

Activate it:

**Windows:**
```bash
venv\Scripts\activate
```

**Linux / macOS:**
```bash
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Create a `.env` file in the project root.

Add the API credentials and configuration required by the application.

Example:

```env
GEMINI_API_KEY=your_gemini_api_key
```

Use the exact environment variable names expected by the current configuration code.

⚠️ Never upload API keys or secrets to GitHub.

### Step 5: Run the Backend

Start the FastAPI application using the actual application entry point configured in the repository.

For example, if the entry point is `main.py` and the FastAPI instance is named `app`:

```bash
uvicorn main:app --reload
```

The local server will generally be available at:

```text
http://127.0.0.1:8000
```

FastAPI documentation (when enabled):

```text
http://127.0.0.1:8000/docs
```

---

## 🌐 API Overview

The backend exposes API endpoints for different application functionalities.

Core API functionality includes:

- Health monitoring.
- Resume PDF processing.
- Resume classification.
- Resume and job description analysis.
- AI Career Assistant conversations.
- Career resource discovery.

For the exact HTTP methods, endpoint paths, request schemas and response formats, refer to the FastAPI application routes and the interactive Swagger documentation at `/docs`.

---

## 🚀 Deployment

The backend uses Docker-based deployment configuration.

### Hugging Face Spaces
- Docker SDK configuration.
- Application port: 7860.
- Environment variables configured through Space settings.

### Vercel
A lightweight backend deployment is also maintained for the connected frontend.

Deployment requires the appropriate environment variables and application configuration.

---

## 🔐 Security Considerations

- API keys should be stored as environment variables.
- Sensitive credentials should never be committed to GitHub.
- Uploaded documents should be processed responsibly.
- User information should be handled carefully.
- Production deployments should use appropriate access controls and configuration.

---

## 🎯 Project Objectives

The main objectives of CareerBuddy AI are:

1. Make resume improvement more accessible.
2. Help candidates identify job-specific skill gaps.
3. Provide structured resume evaluation.
4. Reduce manual resume review effort.
5. Offer personalized career learning guidance.
6. Combine resume analysis and career assistance in one platform.

---

## 🔮 Future Scope

Potential future improvements include:

- Advanced semantic resume matching.
- More comprehensive job-role recommendations.
- Expanded career knowledge base.
- Improved personalized learning roadmaps.
- Additional resume formats.
- Enhanced evaluation and reporting.
- More integrations with job platforms.

These are future enhancements and should not be confused with currently implemented features.

---

## 👨‍💻 Developer

**Chittransh Verma**

B.Tech – Computer Science Engineering  
HCST

**Project:** CareerBuddy AI  
**Type:** Individual Project

---

## ⭐ Acknowledgement

CareerBuddy AI is developed as an individual academic project with the objective of applying Artificial Intelligence and backend engineering to practical career development challenges.

If you find this project interesting, consider giving the repository a ⭐ on GitHub.

**From Resume Analysis to Career Growth.** 🚀
