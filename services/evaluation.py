# services/evaluation.py — LLM-only contextual resume evaluation (no embeddings).
"""
LLM-based contextual evaluation for the resume scoring pipeline.

Design (per refactor spec):
- No local embedding model, no sentence-transformers, no cosine similarity.
- The LLM (Gemini via services.llm_service) evaluates contextual categories.
- Ordinary Python code computes the final weighted score (see services/scoring.py).
- The LLM must return structured JSON; validated with Pydantic.
- The LLM must NOT invent qualifications not supported by the resume.
- Failures (invalid JSON, empty response, API error, timeout, rate limit)
  degrade gracefully to a zero-score fallback so the API never crashes.
"""

import asyncio
import logging

from pydantic import BaseModel, Field, field_validator

from services.llm_service import async_call_llm_json

logger = logging.getLogger(__name__)

EVALUATION_TIMEOUT_SECONDS = 60


class CategoryScore(BaseModel):
    """Score + evidence for a single contextual category (0-100)."""

    score: int = Field(default=0, ge=0, le=100, description="Category score 0-100")
    evidence: list[str] = Field(default_factory=list)
    explanation: str = Field(default="")

    @field_validator("score", mode="before")
    @classmethod
    def _coerce_score(cls, v):
        try:
            v = int(float(v))
        except (TypeError, ValueError):
            return 0
        return max(0, min(100, v))

    @field_validator("evidence", mode="before")
    @classmethod
    def _coerce_evidence(cls, v):
        if v is None:
            return []
        if isinstance(v, str):
            return [v]
        try:
            return [str(x) for x in list(v)][:5]
        except TypeError:
            return [str(v)]


class LLMEvaluation(BaseModel):
    """Validated LLM evaluation covering contextual categories."""

    experience: CategoryScore = Field(default_factory=CategoryScore)
    projects: CategoryScore = Field(default_factory=CategoryScore)
    education: CategoryScore = Field(default_factory=CategoryScore)
    jd_relevance: CategoryScore = Field(default_factory=CategoryScore)
    missing_qualifications: list[str] = Field(default_factory=list)
    clarity_notes: str = Field(default="")

    @field_validator("missing_qualifications", mode="before")
    @classmethod
    def _coerce_missing(cls, v):
        if v is None:
            return []
        if isinstance(v, str):
            return [v]
        try:
            return [str(x) for x in list(v)][:10]
        except TypeError:
            return [str(v)]


EVALUATION_PROMPT_TEMPLATE = """You are a strict, fair technical recruiter evaluating a resume against a job description.

STRICT RULES:
1. Evaluate ONLY what is explicitly present in the resume. Do NOT invent skills, experience, projects, education, companies, or achievements.
2. If evidence is weak or missing, give a LOW score with an explanation — never inflate.
3. Distinguish clearly between present, missing, and weakly demonstrated qualifications.
4. Do NOT consider age, gender, ethnicity, religion, disability, or any protected attribute.
5. Score each category 0-100 based on document fit, not candidate worth.
6. Return ONLY valid JSON matching the schema below. No markdown fences, no prose.

Categories:
- experience: relevant experience and responsibilities, technical and domain knowledge.
- projects: project relevance, practical evidence, achievement quality and measurable impact.
- education: education and certifications where relevant.
- jd_relevance: overall job-description relevance, required and preferred skills coverage in context, resume clarity and relevance to the target role.

Return JSON with EXACTLY this structure:
{{
  "experience": {{"score": 0, "evidence": ["quote or paraphrase from resume"], "explanation": "why this score"}},
  "projects": {{"score": 0, "evidence": [], "explanation": ""}},
  "education": {{"score": 0, "evidence": [], "explanation": ""}},
  "jd_relevance": {{"score": 0, "evidence": [], "explanation": ""}},
  "missing_qualifications": ["qualification 1"],
  "clarity_notes": "brief note on resume clarity and relevance"
}}

Resume (structured):
{resume_json}

Resume (raw text, truncated):
{resume_text}

Job description (structured):
{jd_json}

Job description (raw text, truncated):
{jd_text}
"""


def fallback_evaluation(reason: str) -> LLMEvaluation:
    """Deterministic fallback used when the LLM call fails or validates badly."""
    return LLMEvaluation(
        experience=CategoryScore(score=0, evidence=[], explanation=f"LLM unavailable: {reason}"),
        projects=CategoryScore(score=0, evidence=[], explanation=f"LLM unavailable: {reason}"),
        education=CategoryScore(score=0, evidence=[], explanation=f"LLM unavailable: {reason}"),
        jd_relevance=CategoryScore(score=0, evidence=[], explanation=f"LLM unavailable: {reason}"),
        missing_qualifications=[],
        clarity_notes=f"Evaluation fallback: {reason}",
    )


def validate_evaluation(raw: object) -> LLMEvaluation:
    """Validate raw LLM output into LLMEvaluation, raising on failure."""
    if raw is None:
        raise ValueError("Empty LLM response")
    if isinstance(raw, str):
        raise ValueError("LLM returned string instead of JSON object")
    if not isinstance(raw, dict):
        raise ValueError(f"LLM returned non-object: {type(raw).__name__}")
    return LLMEvaluation.model_validate(raw)


async def async_evaluate_resume(
    resume_json: dict,
    jd_json: dict,
    resume_text: str = "",
    jd_text: str = "",
    timeout: float = EVALUATION_TIMEOUT_SECONDS,
) -> LLMEvaluation:
    """
    Evaluate resume vs JD with the LLM and return a validated LLMEvaluation.

    Never raises: on any failure returns fallback_evaluation() so the
    scoring pipeline can still produce a deterministic result.
    """
    prompt = EVALUATION_PROMPT_TEMPLATE.format(
        resume_json=str(resume_json)[:6000],
        resume_text=(resume_text or "")[:4000],
        jd_json=str(jd_json)[:4000],
        jd_text=(jd_text or "")[:3000],
    )
    try:
        raw = await asyncio.wait_for(
            async_call_llm_json(prompt, temperature=0.2, max_tokens=2500),
            timeout=timeout,
        )
        try:
            return validate_evaluation(raw)
        except Exception as e:
            print(f"[evaluation] validation failed: {e}")
            logger.exception("[evaluation] validation failed: %s", e)
            return fallback_evaluation(f"invalid LLM response ({e})")
    except asyncio.TimeoutError as e:
        print(f"[evaluation] LLM timeout: {e}")
        logger.exception("[evaluation] LLM timeout: %s", e)
        return fallback_evaluation("LLM timeout")
    except Exception as e:
        msg = str(e)
        # Rate-limit / quota / auth errors are common; keep message short, no secrets.
        print(f"[evaluation] LLM error: {msg[:200]}")
        logger.exception("[evaluation] LLM error: %s", msg[:200])
        return fallback_evaluation(f"LLM error ({msg[:120]})")
