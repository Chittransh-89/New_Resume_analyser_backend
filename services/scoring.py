# services/scoring.py — LLM-only ATS scoring (NO embeddings).
"""
Final scoring pipeline: deterministic Python + LLM contextual scores.

FINAL SCORING FORMULA (documented, no hidden caps):
    final = (
        0.35 * required_skills_score
        + 0.25 * experience_score (LLM)
        + 0.15 * projects_score (LLM)
        + 0.10 * education_score (LLM)
        + 0.15 * jd_relevance_score (LLM)
    )
    if keyword stuffing detected: final *= 0.80  (documented 20% penalty)

- required_skills_score: deterministic 0-100 from rule_matcher
  (full=1.0, partial=0.5, missing=0).
- experience/projects/education/jd_relevance: validated LLM 0-100 scores.
- Preferred skills are informational only (do NOT affect final) to avoid
  double-counting; they appear in the response for feedback.
- Missing sections score 0 naturally via the weights (no hidden caps).
- No SentenceTransformer, no torch, no sklearn, no cosine similarity.

Verdicts (on final 0-100):
  >=80 Strong Match, >=65 Good Match, >=45 Moderate Match, else Low Match.
"""

import re

# Import SKILLS_MAP safely
try:
    from skills_map import SKILLS_MAP
except ImportError:
    try:
        from skills_map import skills_list as SKILLS_MAP  # type: ignore
    except ImportError:
        SKILLS_MAP = {}

# Documented weights (must sum to 1.0).
WEIGHTS = {
    "required_skills": 0.35,
    "experience": 0.25,
    "projects": 0.15,
    "education": 0.10,
    "jd_relevance": 0.15,
}

KEYWORD_STUFFING_PENALTY = 0.80  # 20% penalty, applied only when detected.


def to_text(val) -> str:
    if val is None:
        return ""
    if isinstance(val, list):
        return " ".join([to_text(item) for item in val if item]).strip()
    if isinstance(val, dict):
        return " ".join([to_text(v) for v in val.values() if v]).strip()
    return str(val).strip()


def clean(t: str) -> str:
    """Basic text cleaner for scoring module."""
    if not t:
        return ""
    text = re.sub(r'[\(\)\[\]\{\}\/\\]', ' ', t.lower().replace('-', ' '))
    return re.sub(r'\s+', ' ', text).strip()


# ── EXTRACT SKILLS (Required by Router / Parser) ──
def extract_skills(text: str) -> list:
    """
    Extracts canonical skills from raw text using SKILLS_MAP
    with safe regex boundary matching (deterministic, no embeddings).
    """
    if not text:
        return []

    cleaned_text = clean(text)
    found = set()

    for canonical, variants in (SKILLS_MAP or {}).items():
        all_variants = variants + [canonical]
        for v in all_variants:
            v_clean = clean(v)
            if not v_clean:
                continue
            # Safe boundary check (avoids 'java' matching 'javascript' etc.
            # for multi-word variants; single-char skills still need care).
            pattern = rf'\b{re.escape(v_clean)}\b'
            if re.search(pattern, cleaned_text):
                found.add(canonical)
                break

    return list(found)


def match_skills(resume_skills: list, jd_req: list, jd_pref: list) -> dict:
    """Delegates matching to rule_matcher.py (deterministic, no embeddings)."""
    from rule_matcher import match_skills as rule_match
    return rule_match(
        resume_skills=resume_skills,
        jd_required=jd_req,
        jd_preferred=jd_pref,
    )


def check_keyword_stuffing(resume_json: dict, jd_json: dict) -> float:
    """
    Detects unnatural keyword spamming or list-dumping.
    Returns a multiplier (1.0 = Clean, 0.80 = Penalty Applied).
    Deterministic; no embeddings.
    """
    bullets = [b for e in (resume_json or {}).get("experience", []) for b in e.get("bullets", [])]
    if not bullets:
        return 1.0

    all_jd_skills = [s.lower() for s in (jd_json or {}).get("required_skills", []) + (jd_json or {}).get("preferred_skills", [])]
    if not all_jd_skills:
        return 1.0

    stuffed_bullets = 0
    for bullet in bullets:
        words = bullet.split()
        if len(words) < 6:
            continue
        # Check skill frequency inside a single bullet
        skill_hits = sum(1 for s in all_jd_skills if s in bullet.lower())
        density = skill_hits / len(words)

        # If > 35% of bullet is just comma-separated JD skills -> Spam
        if density > 0.35:
            stuffed_bullets += 1

    # If more than 40% of bullets are spammy
    if (stuffed_bullets / len(bullets)) > 0.40:
        return KEYWORD_STUFFING_PENALTY  # 20% penalty on total score

    return 1.0


def _category_score(llm_eval, name: str) -> float:
    """Safely extract 0-100 category score from LLMEvaluation or dict."""
    try:
        if llm_eval is None:
            return 0.0
        if isinstance(llm_eval, dict):
            cat = llm_eval.get(name, 0)
            if isinstance(cat, dict):
                return float(cat.get("score", 0))
            return float(cat or 0)
        cat = getattr(llm_eval, name, 0)
        if hasattr(cat, "score"):
            return float(cat.score)
        return float(cat or 0)
    except (TypeError, ValueError):
        return 0.0


def compute_weighted_score(skill_res: dict, llm_eval) -> dict:
    """
    Pure deterministic weighted aggregation.

    Returns component scores + final_before_penalty for transparency.
    """
    req_score = float((skill_res or {}).get("required_score", 0.0) or 0.0)
    exp_score = _category_score(llm_eval, "experience")
    proj_score = _category_score(llm_eval, "projects")
    edu_score = _category_score(llm_eval, "education")
    rel_score = _category_score(llm_eval, "jd_relevance")

    def clamp(v):
        return max(0.0, min(100.0, float(v or 0.0)))

    req_score, exp_score, proj_score, edu_score, rel_score = (
        clamp(req_score), clamp(exp_score), clamp(proj_score), clamp(edu_score), clamp(rel_score)
    )

    final = (
        WEIGHTS["required_skills"] * req_score
        + WEIGHTS["experience"] * exp_score
        + WEIGHTS["projects"] * proj_score
        + WEIGHTS["education"] * edu_score
        + WEIGHTS["jd_relevance"] * rel_score
    )
    return {
        "required_skills": round(req_score, 2),
        "experience": round(exp_score, 2),
        "projects": round(proj_score, 2),
        "education": round(edu_score, 2),
        "jd_relevance": round(rel_score, 2),
        "final_before_penalty": round(final, 2),
    }


def final_score(resume_json: dict, skill_res: dict, sem_res: dict = None, jd_json: dict = None, llm_eval=None) -> dict:
    """
    Combines deterministic skill match + LLM contextual scores.

    Backwards-compatible signature: old callers passed sem_res (embedding
    semantic result). sem_res is now IGNORED — kept only so existing imports
    don't break. New callers should pass llm_eval=LLMEvaluation.

    If llm_eval is None and sem_res looks like an LLM eval dict with
    experience/projects keys, it is used as llm_eval (migration helper).
    """
    # Migration helper: allow passing LLMEvaluation as 3rd positional arg.
    if llm_eval is None and isinstance(sem_res, dict):
        if any(k in sem_res for k in ("experience", "projects", "education", "jd_relevance")):
            llm_eval, sem_res = sem_res, None

    components = compute_weighted_score(skill_res or {}, llm_eval)
    final = components["final_before_penalty"]

    # ── Documented anti-spam penalty (no hidden caps) ──
    spam_multiplier = 1.0
    if jd_json:
        spam_multiplier = check_keyword_stuffing(resume_json or {}, jd_json)
        final = final * spam_multiplier

    final = round(max(0.0, min(100.0, final)), 2)

    # Realistic Verdicts
    if final >= 80.0:
        verdict = "Strong Match"
    elif final >= 65.0:
        verdict = "Good Match"
    elif final >= 45.0:
        verdict = "Moderate Match"
    else:
        verdict = "Low Match"

    req_score = (skill_res or {}).get("required_score", 0.0)
    return {
        "final_score": final,
        "verdict": verdict,
        "breakdown": {
            "required_skills": components["required_skills"],
            "experience": components["experience"],
            "projects": components["projects"],
            "education": components["education"],
            "jd_relevance": components["jd_relevance"],
            "preferred_skills_info_only": (skill_res or {}).get("preferred_score", 0.0),
            "spam_multiplier": spam_multiplier,
            "weights": dict(WEIGHTS),
            "formula": (
                "final = 0.35*required_skills + 0.25*experience(LLM) + "
                "0.15*projects(LLM) + 0.10*education(LLM) + 0.15*jd_relevance(LLM); "
                "if keyword stuffing: final *= 0.80"
            ),
        },
    }


# ── Deprecated stub: kept to fail loudly if old embedding path is used ──
def semantic_score(resume_json: dict, jd_json: dict) -> dict:
    """
    DEPRECATED: embedding-based semantic scoring was removed.

    Raises to prevent silent use of the old embedding pipeline.
    Use services.evaluation.async_evaluate_resume instead.
    """
    raise RuntimeError(
        "semantic_score (embedding similarity) was removed. "
        "Use services.evaluation.async_evaluate_resume for LLM-based evaluation."
    )


def calibrate_similarity(sim: float) -> float:
    """DEPRECATED: embedding calibration curve removed with embeddings."""
    raise RuntimeError("calibrate_similarity was removed with the embedding pipeline.")
