# services/scoring.py — final score math (plain Python, NO embeddings).
#
# FINAL SCORING FORMULA (weights add up to 100%):
#     final = 0.35 * required_skills          (deterministic text matching)
#           + 0.25 * experience      (LLM)    + 0.15 * projects (LLM)
#           + 0.10 * education       (LLM)    + 0.15 * jd_relevance (LLM)
#     if keyword stuffing is detected: final *= 0.80 (documented 20% penalty)
#
# Notes:
# - Required-skill score: full match = 1 point, partial = 0.5, missing = 0.
# - Preferred skills are shown for feedback but do NOT change the final
#   score (counting them too would reward the same skill twice).
# - A missing category simply scores 0 in its slot. There are no hidden caps.
#
# Verdicts: >=80 Strong Match, >=65 Good Match, >=45 Moderate Match, else Low Match.

import re

import rule_matcher
from skills_map import SKILLS_MAP
from services.evaluation import EVALUATION_PROMPT_TEMPLATE, validate_evaluation
from services.llm_service import call_llm_json

# Each weight is a share of the final score. They must add up to 1.0.
WEIGHTS = {
    "required_skills": 0.35,
    "experience": 0.25,
    "projects": 0.15,
    "education": 0.10,
    "jd_relevance": 0.15,
}

KEYWORD_STUFFING_PENALTY = 0.80  # documented 20% penalty, only when detected.


def clean(text: str) -> str:
    """Lowercase and simplify text so skill matching is consistent."""
    if not text:
        return ""
    text = re.sub(r"[\(\)\[\]\{\}\/\\]", " ", text.lower().replace("-", " "))
    return re.sub(r"\s+", " ", text).strip()


def extract_skills(text: str) -> list:
    """Find canonical skills from SKILLS_MAP mentioned in free text.

    Uses word-boundary matching, so 'java' does not match 'javascript'.
    """
    if not text:
        return []
    cleaned_text = clean(text)
    found = set()
    for canonical, variants in (SKILLS_MAP or {}).items():
        for variant in variants + [canonical]:
            variant_clean = clean(variant)
            if not variant_clean:
                continue
            if re.search(rf"\b{re.escape(variant_clean)}\b", cleaned_text):
                found.add(canonical)
                break
    return list(found)


def match_skills(resume_skills: list, jd_required: list, jd_preferred: list) -> dict:
    """Match resume skills against JD lists (deterministic, no embeddings)."""
    return rule_matcher.match_skills(
        resume_skills=resume_skills,
        jd_required=jd_required,
        jd_preferred=jd_preferred,
    )


def check_keyword_stuffing(resume_json: dict, jd_json: dict) -> float:
    """Return 0.80 if the resume stuffs JD keywords, else 1.0.

    A bullet counts as stuffed when over 35% of its words are JD skills,
    and the penalty applies when over 40% of bullets are stuffed.
    """
    bullets = [b for exp in (resume_json or {}).get("experience", []) for b in exp.get("bullets", [])]
    if not bullets:
        return 1.0
    jd_skills = [s.lower() for s in (jd_json or {}).get("required_skills", [])
                 + (jd_json or {}).get("preferred_skills", [])]
    if not jd_skills:
        return 1.0

    stuffed = 0
    for bullet in bullets:
        words = bullet.split()
        if len(words) < 6:
            continue
        hits = sum(1 for skill in jd_skills if skill in bullet.lower())
        if hits / len(words) > 0.35:
            stuffed += 1
    if stuffed / len(bullets) > 0.40:
        return KEYWORD_STUFFING_PENALTY
    return 1.0


def _clamp(score) -> float:
    """Force any value into the 0-100 range. Bad values become 0."""
    try:
        return max(0.0, min(100.0, float(score or 0.0)))
    except (TypeError, ValueError):
        return 0.0


def _category_score(llm_eval, name: str) -> float:
    """Read one 0-100 category score from an LLMEvaluation (or plain dict)."""
    if llm_eval is None:
        return 0.0
    if isinstance(llm_eval, dict):
        category = llm_eval.get(name, 0)
        if isinstance(category, dict):
            return _clamp(category.get("score", 0))
        return _clamp(category)
    category = getattr(llm_eval, name, 0)
    if hasattr(category, "score"):
        return _clamp(category.score)
    return _clamp(category)


def compute_weighted_score(skill_result: dict, llm_eval) -> dict:
    """Apply the documented formula. Returns each part plus the total."""
    parts = {
        "required_skills": _clamp((skill_result or {}).get("required_score", 0.0)),
        "experience": _category_score(llm_eval, "experience"),
        "projects": _category_score(llm_eval, "projects"),
        "education": _category_score(llm_eval, "education"),
        "jd_relevance": _category_score(llm_eval, "jd_relevance"),
    }
    total = sum(parts[name] * WEIGHTS[name] for name in parts)
    result = {name: round(score, 2) for name, score in parts.items()}
    result["final_before_penalty"] = round(total, 2)
    return result


def semantic_score(resume_json: dict, jd_json: dict) -> dict:
    """
    LLM-based contextual evaluation of resume vs JD (no local embeddings).
    Returns category scores and an overall semantic/relevance score.
    """
    prompt = EVALUATION_PROMPT_TEMPLATE.format(
        resume_json=str(resume_json)[:6000],
        resume_text="",
        jd_json=str(jd_json)[:4000],
        jd_text="",
    )
    raw = call_llm_json(prompt, temperature=0.2, max_tokens=2500)
    eval_obj = validate_evaluation(raw)
    return {
        "semantic_score": eval_obj.jd_relevance.score,
        "experience": eval_obj.experience.score,
        "projects": eval_obj.projects.score,
        "education": eval_obj.education.score,
        "jd_relevance": eval_obj.jd_relevance.score,
        "missing_qualifications": eval_obj.missing_qualifications,
        "section_scores": {
            "experience": eval_obj.experience.score,
            "projects": eval_obj.projects.score,
            "education": eval_obj.education.score,
            "jd_relevance": eval_obj.jd_relevance.score,
        },
        "evaluation": eval_obj,
    }


def final_score(resume_json: dict, skill_result: dict, arg3 = None, arg4 = None) -> dict:
    """
    Combine deterministic skill score + contextual evaluation into final 0-100 score:
      - 35% Required Skills
      - 25% Experience (LLM)
      - 15% Projects (LLM)
      - 10% Education (LLM)
      - 15% Job Relevance (LLM)
    Supports both signatures:
      - final_score(resume, skills, sem_res, jd)
      - final_score(resume, skills, jd, llm_eval)
    """
    # Identify which argument is evaluation data and which is jd_json
    if hasattr(arg4, "experience") or (isinstance(arg4, dict) and ("experience" in arg4 or "semantic_score" in arg4)):
        eval_data, jd_json = arg4, arg3
    elif hasattr(arg3, "experience") or (isinstance(arg3, dict) and ("experience" in arg3 or "semantic_score" in arg3)):
        eval_data, jd_json = arg3, arg4
    else:
        eval_data = arg4 if arg4 is not None else arg3
        jd_json = arg3 if eval_data is arg4 else arg4

    parts = compute_weighted_score(skill_result or {}, eval_data)
    total = parts["final_before_penalty"]

    spam_multiplier = 1.0
    if jd_json and isinstance(jd_json, dict):
        spam_multiplier = check_keyword_stuffing(resume_json or {}, jd_json)
        total = total * spam_multiplier
    total = round(max(0.0, min(100.0, total)), 2)

    if total >= 80.0:
        verdict = "Strong Match"
    elif total >= 65.0:
        verdict = "Good Match"
    elif total >= 45.0:
        verdict = "Moderate Match"
    else:
        verdict = "Low Match"

    req_score = parts["required_skills"]
    skill_score = (skill_result or {}).get("skill_score", req_score)
    sem_score = parts["jd_relevance"]
    if isinstance(eval_data, dict) and "semantic_score" in eval_data:
        sem_score = eval_data["semantic_score"]

    return {
        "final_score": total,
        "verdict": verdict,
        "breakdown": {
            "required_skills": parts["required_skills"],
            "experience": parts["experience"],
            "projects": parts["projects"],
            "education": parts["education"],
            "jd_relevance": parts["jd_relevance"],
            "skill_match": skill_score,
            "semantic_match": sem_score,
            "required_skills_met": f"{req_score}%",
            "preferred_skills_info_only": (skill_result or {}).get("preferred_score", 0.0),
            "spam_multiplier": spam_multiplier,
            "weights": dict(WEIGHTS),
            "formula": (
                "final = 0.35*required_skills + 0.25*experience(LLM) + "
                "0.15*projects(LLM) + 0.10*education(LLM) + 0.15*jd_relevance(LLM); "
                "if keyword stuffing: final *= 0.80"
            ),
        },
    }
