# services/classifier.py — document type + role (uses llm_service.py Gemini)
import json
from services.llm_service import call_llm, call_llm_json

# Example: change prompt here to test different classification logic

SINGLE_PROMPT = """You are an ATS classifier.
Types: RESUME, JOB_DESCRIPTION, NOTES, OTHER
Roles: DATA_SCIENTIST, DATA_ANALYST, ML_ENGINEER, AI_ENGINEER, FRONTEND_DEVELOPER, BACKEND_DEVELOPER, FULLSTACK_DEVELOPER, SOFTWARE_ENGINEER

Return ONLY JSON: {{"type":"...","job_role":"...","confidence":0.0}}

Document:
{text}
"""

DUAL_PROMPT = """Classify Document A and B.
Types: RESUME, JOB_DESCRIPTION, NOTES, OTHER
Roles: DATA_SCIENTIST, DATA_ANALYST, ML_ENGINEER, AI_ENGINEER, FRONTEND_DEVELOPER, BACKEND_DEVELOPER, FULLSTACK_DEVELOPER, SOFTWARE_ENGINEER

Return ONLY JSON: {{"document_a":{{"type":"...","job_role":"...","confidence":0}},"document_b":{{"type":"...","job_role":"...","confidence":0}}}}

Document A:
{a}
Document B:
{b}
"""

def classify_single(text: str) -> dict:
    try:
        j = call_llm_json(SINGLE_PROMPT.format(text=text[:1500]))
        return {
            "type": j.get("type","OTHER"), 
            "job_role": j.get("job_role","UNKNOWN"), 
            "confidence": j.get("confidence",0)
        }
    except Exception as e:
        print(f"[classifier] single failed: {e}")
        return {"type":"OTHER","job_role":"UNKNOWN","confidence":0}

def classify_pair(resume_text: str, jd_text: str) -> dict:
    try:
        j = call_llm_json(DUAL_PROMPT.format(a=resume_text[:1500], b=jd_text[:1500]))
        return j
    except Exception as e:
        print(f"[classifier] pair failed: {e}")
        return {
            "document_a":{
                "type":"OTHER",
                "job_role":"UNKNOWN",
                "confidence":0
            },
            "document_b":{
                "type":"OTHER",
                "job_role":"UNKNOWN",
                "confidence":0
            }
        }
