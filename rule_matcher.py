# rule_matcher.py — Deterministic skill matching (NO embeddings, NO fuzzy libs).
"""
Deterministic text matching for resume skills vs job-description skills.

- No SentenceTransformer, no torch, no sklearn, no rapidfuzz, no cosine similarity.
- Normalizes whitespace, capitalization, dashes, punctuation.
- Uses SKILLS_MAP alias map + word-boundary regex matching.
- Distinguishes FULL match vs PARTIAL support vs MISSING.
- Required vs preferred skills are evaluated separately.

Partial support: token overlap >= 50% of the JD skill tokens appears in the
resume skill set, but the full canonical/variant phrase does not match.
Partial counts as 0.5 in group scores (documented, no hidden penalties).
"""

import re

# skills_map import handling (chahe SKILLS_MAP ho ya skills_list)
try:
    from skills_map import SKILLS_MAP
except ImportError:
    try:
        from skills_map import skills_list as SKILLS_MAP  # type: ignore
    except ImportError:
        SKILLS_MAP = {}


def clean_text(text: str) -> str:
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r'[\(\)\[\]\{\}\/\\]', ' ', text)
    text = text.replace('-', ' ')
    return re.sub(r'\s+', ' ', text).strip()


def normalize_skill(skill: str) -> str:
    """Normalize a single skill string for deterministic comparison."""
    return clean_text(skill or "")


def clean_skill_string(skill: str) -> list:
    """
    Parentheses split:
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


def _build_variant_index():
    """
    Build normalized-variant -> canonical map from SKILLS_MAP.
    Example: 'py' -> 'python', 'reactjs' -> 'react'.
    """
    index = {}
    for canonical, variants in (SKILLS_MAP or {}).items():
        canon_clean = clean_text(canonical)
        if canon_clean:
            index.setdefault(canon_clean, clean_text(canonical))
        for v in variants or []:
            v_clean = clean_text(v)
            if v_clean:
                index.setdefault(v_clean, clean_text(canonical))
    return index


_VARIANT_INDEX = _build_variant_index()


def canonical_of(skill: str) -> str:
    """Return canonical form if known, else normalized skill."""
    return _VARIANT_INDEX.get(clean_text(skill), clean_text(skill))


def _phrase_in_text(phrase: str, text: str) -> bool:
    """Word-boundary regex check (avoids 'java' matching 'javascript')."""
    if not phrase or not text:
        return False
    return re.search(rf'\b{re.escape(phrase)}\b', text) is not None


def match_status(jd_skill: str, resume_text: str, resume_canonicals: set) -> str:
    """
    Return 'full', 'partial', or 'missing' for one JD skill string.

    - full: canonical or any known variant matches via word boundary,
      or the exact normalized JD phrase appears in resume text.
    - partial: >=50% of JD skill tokens overlap resume tokens but no full match.
    - missing: otherwise.
    """
    clean_jd = clean_text(jd_skill)
    if not clean_jd:
        return "missing"
    jd_canon = canonical_of(clean_jd)

    # Full: canonical-level match (handles aliases like py -> python).
    if jd_canon in resume_canonicals:
        return "full"

    # Full: any known variant of the same canonical present in resume text.
    for variant, canon in _VARIANT_INDEX.items():
        if canon == jd_canon and _phrase_in_text(variant, resume_text):
            return "full"

    # Full: exact JD phrase in resume text (covers skills absent from SKILLS_MAP).
    if _phrase_in_text(clean_jd, resume_text):
        return "full"

    # Partial: token overlap heuristic (deterministic, no embeddings).
    jd_tokens = set(clean_jd.split())
    if len(jd_tokens) >= 2:
        resume_tokens = set(resume_text.split())
        overlap = jd_tokens & resume_tokens
        if len(overlap) / len(jd_tokens) >= 0.5:
            return "partial"
    return "missing"


def is_skill_matched(jd_skill: str, resume_skills: list, resume_embs=None) -> bool:
    """
    Backwards-compatible boolean matcher (full match only).

    resume_embs is accepted but IGNORED (kept so old callers don't break).
    Deterministic: SKILLS_MAP canonical + word-boundary matching only.
    """
    if not jd_skill or not resume_skills:
        return False
    resume_text = clean_text(" ".join(resume_skills))
    resume_canonicals = {canonical_of(s) for s in resume_skills if s and s.strip()}
    return match_status(jd_skill, resume_text, resume_canonicals) == "full"


def match_skills(resume_skills: list, jd_required: list, jd_preferred: list) -> dict:
    """
    Main matching function called by scoring.py and analyze router.

    Returns matched / partial / missing splits plus deterministic scores:
      group_score = (full + 0.5 * partial) / total * 100
      skill_score = 0.7 * required_score + 0.3 * preferred_score (informational)
    """
    resume_skills = resume_skills or []
    jd_required = jd_required or []
    jd_preferred = jd_preferred or []

    resume_text = clean_text(" ".join(resume_skills))
    resume_canonicals = {canonical_of(s) for s in resume_skills if s and s.strip()}

    def evaluate_group(jd_skills: list):
        matched, partial, missing = [], [], []
        for raw_skill in jd_skills:
            sub_skills = clean_skill_string(raw_skill)
            best = "missing"
            for part in sub_skills:
                st = match_status(part, resume_text, resume_canonicals)
                if st == "full":
                    best = "full"
                    break
                if st == "partial":
                    best = "partial"
            if best == "full":
                matched.append(raw_skill)
            elif best == "partial":
                partial.append(raw_skill)
            else:
                missing.append(raw_skill)
        total = len(matched) + len(partial) + len(missing)
        score = ((len(matched) + 0.5 * len(partial)) / total * 100) if total > 0 else 0.0
        return matched, partial, missing, round(score, 2)

    matched_req, partial_req, missing_req, req_score = evaluate_group(jd_required)
    matched_pref, partial_pref, missing_pref, pref_score = evaluate_group(jd_preferred)

    # 70% Required + 30% Preferred (informational; final score uses required only).
    skill_score = round((0.7 * req_score) + (0.3 * pref_score), 2)

    return {
        "matched_required": matched_req,
        "partial_required": partial_req,
        "missing_required": missing_req,
        "matched_preferred": matched_pref,
        "partial_preferred": partial_pref,
        "missing_preferred": missing_pref,
        "required_score": req_score,
        "preferred_score": pref_score,
        "skill_score": skill_score,
    }
