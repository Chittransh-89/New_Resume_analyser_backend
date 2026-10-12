# services/evaluation.py — LLM contextual resume evaluation (no embeddings).
#
# The LLM scores four categories (experience, projects, education,
# job-description relevance). Plain Python in services/scoring.py then
# combines those with deterministic skill matching into the final score.
#
# If the LLM call fails, this module RAISES EvaluationError — it never
# returns fake zero scores that look like a real evaluation.

import asyncio
import logging

from pydantic import BaseModel, Field, field_validator

from services.llm_service import async_call_llm_json

logger = logging.getLogger(__name__)

EVALUATION_TIMEOUT_SECONDS = 60
CATEGORIES = ("experience", "projects", "education", "jd_relevance")


class EvaluationError(Exception):
    """Raised when contextual LLM evaluation fails (API error, timeout,
    empty response, or invalid JSON). Callers must surface this clearly."""


def _to_score(value) -> int:
    """Convert anything to a 0-100 int. Unparseable values become 0."""
    try:
        return max(0, min(100, int(float(value))))
    except (TypeError, ValueError):
        return 0


def _to_str_list(value, limit: int) -> list:
    """Convert anything to a short list of strings."""
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    try:
        return [str(item) for item in list(value)][:limit]
    except TypeError:
        return [str(value)]


class CategoryScore(BaseModel):
    """One category: score 0-100 plus the resume evidence behind it."""

    score: int = Field(default=0, ge=0, le=100)
    evidence: list = Field(default_factory=list)
    explanation: str = Field(default="")

    @field_validator("score", mode="before")
    @classmethod
    def _coerce_score(cls, v):
        return _to_score(v)

    @field_validator("evidence", mode="before")
    @classmethod
    def _coerce_evidence(cls, v):
        return _to_str_list(v, 5)


class LLMEvaluation(BaseModel):
    """Validated LLM judgement for all four contextual categories."""

    experience: CategoryScore = Field(default_factory=CategoryScore)
    projects: CategoryScore = Field(default_factory=CategoryScore)
    education: CategoryScore = Field(default_factory=CategoryScore)
    jd_relevance: CategoryScore = Field(default_factory=CategoryScore)
    missing_qualifications: list = Field(default_factory=list)
    clarity_notes: str = Field(default="")

    @field_validator("missing_qualifications", mode="before")
    @classmethod
    def _coerce_missing(cls, v):
        return _to_str_list(v, 10)


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


def validate_evaluation(raw: object) -> LLMEvaluation:
    """Check raw LLM output and return a validated LLMEvaluation.

    Raises EvaluationError (never returns fake scores) when the response
    is empty, not a dict, or fails schema validation.
    """
    if raw is None:
        raise EvaluationError("LLM returned an empty response.")
    if isinstance(raw, str):
        raise EvaluationError("LLM returned text instead of a JSON object.")
    if not isinstance(raw, dict):
        raise EvaluationError(f"LLM returned {type(raw).__name__} instead of a JSON object.")
    try:
        return LLMEvaluation.model_validate(raw)
    except Exception as e:
        raise EvaluationError(f"LLM response failed validation: {e}")


async def async_evaluate_resume(resume_json: dict, jd_json: dict, resume_text: str = "",
                                jd_text: str = "", timeout: float = EVALUATION_TIMEOUT_SECONDS,
                                ) -> LLMEvaluation:
    """Score resume vs JD with the LLM. Raises EvaluationError on any failure."""
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
    except asyncio.TimeoutError:
        print("[evaluation] LLM timed out.")
        logger.exception("[evaluation] LLM timed out.")
        raise EvaluationError("LLM evaluation timed out.")
    except Exception as e:
        print(f"[evaluation] LLM call failed: {str(e)[:200]}")
        logger.exception("[evaluation] LLM call failed: %s", str(e)[:200])
        raise EvaluationError(f"LLM evaluation failed: {str(e)[:200]}")
    return validate_evaluation(raw)
