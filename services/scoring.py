# services/scoring.py — Production-Grade Fair & Strict ATS Scoring Pipeline

import re
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import config

# Import SKILLS_MAP safely
try:
    from skills_map import SKILLS_MAP
except ImportError:
    try:
        from skills_map import skills_list as SKILLS_MAP
    except ImportError:
        SKILLS_MAP = {}

# Load Sentence Transformer Embedding Model
_model = SentenceTransformer(config.EMBEDDING_MODEL)
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
    with safe regex boundary matching.
    """
    if not text:
        return []
    
    cleaned_text = clean(text)
    found = set()

    for canonical, variants in SKILLS_MAP.items():
        all_variants = variants + [canonical]
        for v in all_variants:
            v_clean = clean(v)
            if not v_clean:
                continue
            # Safe boundary check
            pattern = rf'\b{re.escape(v_clean)}\b'
            if re.search(pattern, cleaned_text):
                found.add(canonical)
                break

    return list(found)

def match_skills(resume_skills: list, jd_req: list, jd_pref: list) -> dict:
    """Delegates matching to rule_matcher.py"""
    from rule_matcher import match_skills as rule_match
    return rule_match(
        resume_skills=resume_skills,
        jd_required=jd_req,
        jd_preferred=jd_pref
    )


# ── CORRECTION 3: Mathematical Calibration Curve (Strict Separation) ──
def calibrate_similarity(sim: float) -> float:
    """
    Realistic Semantic Curve:
    - 0.50 raw sim -> ~45% (Below Average)
    - 0.75 raw sim -> ~72% (Good Candidate)
    - 0.82 raw sim -> ~80% (Great Candidate)
    - 0.90+ raw sim -> ~90%+ (God-level match / near-clone)
    """
    if sim <= 0.40:
        return round(max(0.0, sim * 50), 2)
    elif sim <= 0.75:
        # Linear progression from 20% to 70%
        score = 20.0 + ((sim - 0.40) / (0.75 - 0.40)) * 50.0
        return round(score, 2)
    else:
        # Tough upper curve: 70% to 95% between 0.75 and 0.92
        score = 70.0 + ((sim - 0.75) / (0.92 - 0.75)) * 25.0
        return round(min(score, 98.0), 2)


# ── CORRECTION 4: Anti-Keyword Stuffing / Spam Detector ──
def check_keyword_stuffing(resume_json: dict, jd_json: dict) -> float:
    """
    Detects unnatural keyword spamming or list-dumping.
    Returns a multiplier (1.0 = Clean, 0.75 = Penalty Applied).
    """
    bullets = [b for e in resume_json.get("experience", []) for b in e.get("bullets", [])]
    if not bullets:
        return 1.0

    all_jd_skills = [s.lower() for s in jd_json.get("required_skills", []) + jd_json.get("preferred_skills", [])]
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
        return 0.80  # 20% penalty on total score

    return 1.0


# ── CORRECTION 2: Targeted Section-to-Section Alignment ──
def semantic_score(resume_json: dict, jd_json: dict) -> dict:
    """
    Computes semantic similarity by comparing each resume section
    against its RELEVANT counterpart in the JD.
    """
    # 1. Prepare Targeted JD Queries
    # Har value ko to_text() se wrap kar do taaki list string ban jaye safely
    jd_skills_text = to_text(jd_json.get("required_skills", []) + jd_json.get("preferred_skills", []))

    jd_exp_parts = [
        to_text(jd_json.get("job_title", "")),
        to_text(jd_json.get("job_description", "")),
        to_text(jd_json.get("responsibilities", "")), # <-- Ab list hogi toh safely join ho jayegi
        jd_skills_text
    ]
    jd_exp_proj_text = " ".join([p for p in jd_exp_parts if p]).strip()

    jd_edu_text = jd_json.get("education_requirement", jd_json.get("job_title", "Engineering"))

    # 2. Section Texts from Resume
    sections = {
        "skills": to_text(resume_json.get("skills", [])),
        "experience": " ".join([to_text(e.get("bullets", [])) for e in resume_json.get("experience", [])]),
        "projects": " ".join([to_text(p.get("description", "")) + " " + to_text(p.get("tech_used", [])) for p in resume_json.get("projects", [])]),
        "education": " ".join([to_text(e.get("degree", "")) + " " + to_text(e.get("institution", "")) for e in resume_json.get("education", [])])
    }

    # 3. Dynamic Section Targets
    query_map = {
        "skills": "query: " + (jd_skills_text if jd_skills_text else "technical skills"),
        "experience": "query: " + (jd_exp_proj_text if jd_exp_proj_text else "software work experience"),
        "projects": "query: " + (jd_exp_proj_text if jd_exp_proj_text else "technical projects"),
        "education": "query: " + f"degree in {jd_edu_text}"
    }

    # Standard Weights
    weights = {
        "skills": 0.35,
        "experience": 0.30,
        "projects": 0.25,
        "education": 0.10
    }

    # Handle missing sections dynamically (no divide-by-zero or math collapse)
    active_weights = {}
    for k, text in sections.items():
        if text.strip():
            active_weights[k] = weights[k]
        else:
            active_weights[k] = 0.0

    total_weight = sum(active_weights.values())
    if total_weight > 0:
        active_weights = {k: v / total_weight for k, v in active_weights.items()}

    # 4. Compute Similarities — FAST: batch encode (1 call vs 8)
    # Build batch lists
    queries, passages, keys = [], [], []
    for k, text in sections.items():
        if not text.strip():
            continue
        queries.append(query_map[k])
        passages.append("passage: " + text)
        keys.append(k)
    
    scores = {k: 0.0 for k in sections}
    if queries:
        # batch encode: 2x faster on CPU
        q_embs = _model.encode(queries)
        p_embs = _model.encode(passages)
        for idx, k in enumerate(keys):
            raw_sim = float(cosine_similarity([p_embs[idx]], [q_embs[idx]])[0][0])
            scores[k] = calibrate_similarity(raw_sim)

    weighted_semantic = sum(scores[k] * active_weights[k] for k in scores if active_weights[k] > 0)
    return {
        "semantic_score": round(weighted_semantic, 2),
        "section_scores": scores
    }


# ── CORRECTION 1: Hard Skill Gating & Final Evaluation ──
def final_score(resume_json: dict, skill_res: dict, sem_res: dict, jd_json: dict = None) -> dict:
    """
    Combines rule match + semantic match with strict gating rules.
    """
    skill = skill_res.get("skill_score", 0.0)
    sem = sem_res.get("semantic_score", 0.0)
    req_score = skill_res.get("required_score", 0.0)

    # Base weighted score: 55% Semantic + 45% Hard Skills
    final = (0.55 * sem) + (0.45 * skill)

    # ── Strict Gating Rule 1: Missing Core Requirements ──
    # Agar 50% se zyada required skills gayab hain -> Candidate cannot be "Good Match"
    if req_score < 40.0:
        final = min(final, 45.0)  # Hard Reject / Low Match
    elif req_score < 60.0:
        final = min(final, 65.0)  # Moderate Cap

    # ── Strict Gating Rule 2: Missing Experience or Projects ──
    if not resume_json.get("experience"):
        final = min(final, 50.0)
    if not resume_json.get("projects"):
        final = min(final, 55.0)

    # ── Strict Gating Rule 3: Anti-Keyword Stuffing Penalty ──
    if jd_json:
        spam_multiplier = check_keyword_stuffing(resume_json, jd_json)
        final = final * spam_multiplier

    final = round(final, 2)

    # Realistic Verdicts
    if final >= 80.0:
        verdict = "Strong Match"
    elif final >= 65.0:
        verdict = "Good Match"
    elif final >= 45.0:
        verdict = "Moderate Match"
    else:
        verdict = "Low Match"

    return {
        "final_score": final,
        "verdict": verdict,
        "breakdown": {
            "skill_match": skill,
            "semantic_match": sem,
            "required_skills_met": f"{req_score}%"
        }
    }