# services/parser.py — Resume & JD Parser (Gemini JSON Parser)
from services.llm_service import call_llm_json, async_call_llm_json

RESUME_PROMPT = """
You are an expert resume parser. Extract information from this resume and return ONLY a valid JSON object matching this structure:
{{
  "name": "",
  "email": "",
  "phone": "",
  "job_role": "",
  "skills": [],
  "experience": [{{"company": "", "role": "", "duration": "", "bullets": []}}],
  "education": [{{"degree": "", "institution": "", "year": ""}}],
  "projects": [{{"name": "", "description": "", "tech_used": []}}]
}}

Resume:
{text}
"""

JD_PROMPT = """
You are an expert job description parser. Extract requirements and split skills individually. Return ONLY a valid JSON object matching this structure:
{{
  "job_title": "",
  "company": "",
  "job_role": "",
  "required_skills": [],
  "preferred_skills": [],
  "responsibilities": [],
  "qualifications": []
}}

Job Description:
{text}
"""

# ==================== SYNC PARSERS ====================
def parse_resume(text: str) -> dict:
    """Parse resume text synchronously."""
    return call_llm_json(RESUME_PROMPT.format(text=text[:8000]))


def parse_jd(text: str) -> dict:
    """Parse JD text synchronously."""
    return call_llm_json(JD_PROMPT.format(text=text[:3000]))


# ==================== ASYNC PARSERS ====================
async def async_parse_resume(text: str) -> dict:
    """Parse resume text asynchronously (for parallel FastAPI routes)."""
    return await async_call_llm_json(RESUME_PROMPT.format(text=text[:8000]))


async def async_parse_jd(text: str) -> dict:
    """Parse JD text asynchronously (for parallel FastAPI routes)."""
    return await async_call_llm_json(JD_PROMPT.format(text=text[:3000]))