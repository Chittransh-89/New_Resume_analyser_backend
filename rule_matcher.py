import re
import sys
from pathlib import Path
from rapidfuzz import fuzz
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Path setup taaki config easily import ho sake
sys.path.append(str(Path(__file__).resolve().parent))
import config

# skills_map import handling (chahe SKILLS_MAP ho ya skills_list)
try:
    from skills_map import SKILLS_MAP
except ImportError:
    try:
        from skills_map import skills_list as SKILLS_MAP
    except ImportError:
        SKILLS_MAP = {}

# Embeddings model load
_model = SentenceTransformer(config.EMBEDDING_MODEL)


def clean_text(text: str) -> str:
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r'[\(\)\[\]\{\}\/\\]', ' ', text)
    text = text.replace('-', ' ')
    return re.sub(r'\s+', ' ', text).strip()


def clean_skill_string(skill: str) -> list[str]:
    """
    Parentheses split karta hai:
    'Retrieval Augmented Generation(RAG)' -> ['RAG', 'Retrieval Augmented Generation']
    """
    if not skill:
        return []
    results = []
    inside = re.findall(r'\(([^)]+)\)', skill)
    for group in inside:
        results.extend([p.strip() for p in group.split(",") if p.strip()])
    main = re.sub(r'\(.*?\)', '', skill).strip()
    if main:
        results.extend([p.strip() for p in main.split(",") if p.strip()])
    return results if results else [skill]


def is_skill_matched(jd_skill: str, resume_skills: list[str], resume_embs=None) -> bool:
    """
    3-TIER MATCHING:
    1. SKILLS_MAP lookup
    2. RapidFuzz (Typos & spacing)
    3. Sentence Transformers Semantic Match
    """
    clean_jd = clean_text(jd_skill)
    if not clean_jd:
        return False

    clean_resume_list = [clean_text(s) for s in resume_skills if s.strip()]
    if not clean_resume_list:
        return False

    # ── Tier 1: SKILLS_MAP Canonical Match ──
    if SKILLS_MAP:
        for canonical, variants in SKILLS_MAP.items():
            all_variants = [clean_text(v) for v in variants] + [clean_text(canonical)]
            if clean_jd in all_variants:
                if any(r in all_variants for r in clean_resume_list):
                    return True

    # ── Tier 2: Fuzzy String Match (Typos, Spacing, Dashes) ──
    for r_clean in clean_resume_list:
        # Token sort ratio handles order & small variations
        if fuzz.token_sort_ratio(clean_jd, r_clean) >= 88:
            return True

    # ── Tier 3: Semantic Embedding (Vector Cosine Sim) ──
    try:
        jd_emb = _model.encode([clean_jd])
        if resume_embs is None:
            resume_embs = _model.encode(clean_resume_list)

        sims = cosine_similarity(jd_emb, resume_embs)[0]
        if sims.max() >= 0.82:  # Threshold for semantic match
            return True
    except Exception:
        pass

    return False


def match_skills(
    resume_skills: list[str],
    jd_required: list[str],
    jd_preferred: list[str]
) -> dict:
    """
    Main matching function called by scoring.py and analyze router.
    """
    # 1. Expand resume skills (brackets split karke flat list)
    expanded_resume_skills = []
    for s in resume_skills:
        expanded_resume_skills.extend(clean_skill_string(s))

    # Pre-compute resume embeddings ek hi baar taaki bar bar encode na karna pade
    clean_resume_list = [clean_text(s) for s in expanded_resume_skills if s.strip()]
    resume_embs = _model.encode(clean_resume_list) if clean_resume_list else None

    def evaluate_group(jd_skills: list[str]):
        matched = []
        missing = []

        for raw_skill in jd_skills:
            sub_skills = clean_skill_string(raw_skill)
            # Agar bracket ke andar ya bahar ka koi bhi sub-skill match ho jaye
            is_matched = False
            for part in sub_skills:
                if is_skill_matched(part, expanded_resume_skills, resume_embs):
                    is_matched = True
                    break

            if is_matched:
                matched.append(raw_skill)
            else:
                missing.append(raw_skill)

        total = len(matched) + len(missing)
        score = (len(matched) / total * 100) if total > 0 else 0.0
        return matched, missing, round(score, 2)

    matched_req, missing_req, req_score = evaluate_group(jd_required)
    matched_pref, missing_pref, pref_score = evaluate_group(jd_preferred)

    # 70% Required + 30% Preferred Weightage
    skill_score = round((0.7 * req_score) + (0.3 * pref_score), 2)

    return {
        "matched_required": matched_req,
        "missing_required": missing_req,
        "matched_preferred": matched_pref,
        "missing_preferred": missing_pref,
        "required_score": req_score,
        "preferred_score": pref_score,
        "skill_score": skill_score
    }