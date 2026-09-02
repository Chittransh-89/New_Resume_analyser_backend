import re
import json
import asyncio
import pathlib
from services.llm_service import async_call_llm_json

def extract_bullets(text: str) -> list:
    """Extracts candidate bullet points from resume plain text."""
    bullets = []
    for line in text.split("\n"):
        line = line.strip()
        if not line or line.lower() in ["professional summary", "summary", "experience", "education", "skills"]:
            continue
        if "@" in line or "b.tech" in line.lower() or "m.tech" in line.lower():
            continue
        if line.count(",") > 5:
            continue
        if len(line.split()) <= 3 and line.islower():
            continue
            
        if line.startswith(("-", "•", "*", "–", "▪")):
            bullets.append(line.lstrip("-•*–▪ ").strip())
        else:
            if len(line.split()) > 4:
                bullets.append(line)
    return bullets

def _load_prompt(name: str) -> str:
    prompt_path = pathlib.Path(__file__).parent.parent.joinpath("prompts", name)
    if prompt_path.exists():
        return prompt_path.read_text(encoding="utf-8")
    
    # Inline Fallback Prompt if file is missing
    return """You are a professional resume writer.
Rewrite the following resume bullet points to make them more impactful, quantifiable (using action verbs and metrics), and aligned with the Job Description.

Job Description Context:
{jd_text}

Resume Bullets:
{bullets_text}

Return a valid JSON list of objects matching this exact structure:
[
  {{"original": "exact original bullet", "improved": "stronger rewritten bullet"}}
]
"""

async def improve_all(bullets: list, jd_text: str) -> list:
    """
    Improves resume bullets in a single batch call.
    Uses async_call_llm_json with auto-repair and fallback.
    """
    if not bullets:
        return []

    # Limit to top 8 high-impact bullets (prevents token overflow & rate limit)
    selected_bullets = bullets[:8]
    txt = "\n".join(f"{i+1}. {b}" for i, b in enumerate(selected_bullets))
    
    template = _load_prompt("improve_bullets_prompt.txt")
    prompt = template.format(jd_text=jd_text[:1500], bullets_text=txt)

    try:
        res = await async_call_llm_json(prompt, temperature=0.3, max_tokens=3000)
        
        # If response is a valid list of dicts
        if isinstance(res, list) and len(res) > 0:
            return res
        
        # If response was wrapped in a dict (e.g. {"bullets": [...]})
        if isinstance(res, dict):
            for key, val in res.items():
                if isinstance(val, list) and len(val) > 0:
                    return val

        # Fallback if structure is unknown
        return [{"original": b, "improved": b} for b in selected_bullets]

    except Exception as e:
        print(f"[bullets fallback triggered] Reason: {e}")
        # Safe fallback: Never crash the request
        return [{"original": b, "improved": b} for b in selected_bullets]