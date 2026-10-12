"""Weighted scoring tests (pure Python, no embeddings, no LLM calls)."""
import pytest
import tests.conftest  # noqa: F401
from services.scoring import (
    WEIGHTS, compute_weighted_score, final_score, check_keyword_stuffing,
)
from services.evaluation import LLMEvaluation, CategoryScore


def _eval(exp=80, proj=70, edu=60, rel=90):
    return LLMEvaluation(
        experience=CategoryScore(score=exp, evidence=["e"], explanation="x"),
        projects=CategoryScore(score=proj, evidence=[], explanation="x"),
        education=CategoryScore(score=edu, evidence=[], explanation="x"),
        jd_relevance=CategoryScore(score=rel, evidence=[], explanation="x"),
    )


def test_weights_sum_to_one():
    assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-9


def test_weighted_formula_exact():
    # 0.35*100 + 0.25*80 + 0.15*60 + 0.10*40 + 0.15*20 = 35+20+9+4+3 = 71
    skill_res = {"required_score": 100.0}
    llm = _eval(exp=80, proj=60, edu=40, rel=20)
    out = compute_weighted_score(skill_res, llm)
    assert out["final_before_penalty"] == 71.0


def test_final_score_verdicts():
    skill = {"required_score": 100.0, "preferred_score": 0.0}
    assert final_score({}, skill, None, None, llm_eval=_eval(100, 100, 100, 100))["verdict"] == "Strong Match"
    assert final_score({}, skill, None, None, llm_eval=_eval(0, 0, 0, 0))["verdict"] == "Low Match"


def test_spam_penalty_documented():
    spam_bullet = "python, docker, python, docker, aws, python"
    resume = {"experience": [{"bullets": [spam_bullet] * 5}]}
    jd = {"required_skills": ["python", "docker"], "preferred_skills": ["aws"]}
    assert check_keyword_stuffing(resume, jd) == 0.80
    clean_resume = {"experience": [{"bullets": ["Built a FastAPI service with tests and CI."]}]}
    assert check_keyword_stuffing(clean_resume, jd) == 1.0


def test_final_score_applies_spam_multiplier():
    spam_bullet = "python docker aws kubernetes terraform python"
    resume = {"experience": [{"bullets": [spam_bullet] * 5}]}
    jd = {"required_skills": ["python", "docker", "aws", "kubernetes", "terraform"],
          "preferred_skills": []}
    skill = {"required_score": 100.0, "preferred_score": 0.0}
    llm = _eval(100, 100, 100, 100)
    out = final_score(resume, skill, None, jd, llm_eval=llm)
    assert out["final_score"] == round(100.0 * 0.80, 2)
    assert out["breakdown"]["spam_multiplier"] == 0.80


def test_embedding_entrypoints_removed():
    from services import scoring
    with pytest.raises(RuntimeError):
        scoring.semantic_score({}, {})
    with pytest.raises(RuntimeError):
        scoring.calibrate_similarity(0.8)
    assert not hasattr(scoring, "_model"), "embedding model must not exist in scoring"
