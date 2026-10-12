"""Deterministic skill normalization + matching tests (no embeddings, no LLM)."""
import tests.conftest  # noqa: F401
from rule_matcher import (
    clean_text, canonical_of, is_skill_matched, match_skills,
)
from services.scoring import extract_skills


def test_clean_text_normalizes():
    assert clean_text("  FastAPI (REST) ") == "fastapi rest"
    assert clean_text("scikit-learn") == "scikit learn"


def test_alias_canonical():
    assert canonical_of("py") == "python"
    assert canonical_of("ReactJS") == "react"
    assert canonical_of("Some Unknown Skill XYZ") == "some unknown skill xyz"


def test_word_boundary_no_false_positive():
    # 'java' must NOT match a resume that only has 'javascript'.
    assert is_skill_matched("java", ["javascript"]) is False
    assert is_skill_matched("java", ["java"]) is True


def test_match_splits_full_partial_missing():
    resume = ["Python", "FastAPI", "machine"]
    res = match_skills(resume, ["python", "machine learning", "docker"], ["fastapi"])
    assert "python" in res["matched_required"]
    assert "machine learning" in res["partial_required"]
    assert "docker" in res["missing_required"]
    assert "fastapi" in res["matched_preferred"]
    # partial counts as 0.5: (1 + 0.5) / 3 * 100 = 50.0
    assert res["required_score"] == 50.0


def test_extract_skills_uses_alias_map():
    text = "Experienced with py, ReactJS and docker-compose."
    found = extract_skills(text)
    assert "python" in found
    assert "react" in found
    assert "docker" in found


def test_empty_inputs_score_zero():
    res = match_skills([], [], [])
    assert res["required_score"] == 0.0
    assert res["missing_required"] == []
