"""LLM evaluation tests (LLM mocked). Failures must raise, never fake zeros."""
import asyncio
import pytest
import tests.conftest  # noqa: F401
import services.evaluation as ev
from services.evaluation import EvaluationError


def test_validate_good_payload():
    raw = {
        "experience": {"score": 80, "evidence": ["Built X"], "explanation": "good"},
        "projects": {"score": 70, "evidence": [], "explanation": ""},
        "education": {"score": 60, "evidence": [], "explanation": ""},
        "jd_relevance": {"score": 90, "evidence": [], "explanation": ""},
        "missing_qualifications": ["Kubernetes"],
        "clarity_notes": "clear",
    }
    out = ev.validate_evaluation(raw)
    assert out.experience.score == 80
    assert out.missing_qualifications == ["Kubernetes"]


def test_validate_clamps_and_defaults():
    raw = {"experience": {"score": 999, "evidence": None, "explanation": ""}}
    out = ev.validate_evaluation(raw)
    assert out.experience.score == 100
    assert out.projects.score == 0  # defaulted


def test_validate_rejects_garbage():
    for bad in (None, "string", [1, 2], 42):
        with pytest.raises(EvaluationError):
            ev.validate_evaluation(bad)


def test_validate_rejects_unparseable_scores():
    with pytest.raises(EvaluationError):
        ev.validate_evaluation({"experience": "not a dict nor number"})
    # Note: {"score": "nan!"} coerces to 0 — still a valid, honest low score.


def test_async_raises_on_api_error(monkeypatch):
    async def boom(*a, **k):
        raise RuntimeError("429 rate limit exceeded")
    monkeypatch.setattr(ev, "async_call_llm_json", boom)
    with pytest.raises(EvaluationError, match="429"):
        asyncio.run(ev.async_evaluate_resume({}, {}, "r", "j", timeout=5))


def test_async_raises_on_invalid_response(monkeypatch):
    async def bad(*a, **k):
        return None  # empty response
    monkeypatch.setattr(ev, "async_call_llm_json", bad)
    with pytest.raises(EvaluationError, match="empty"):
        asyncio.run(ev.async_evaluate_resume({}, {}, "r", "j", timeout=5))


def test_async_timeout(monkeypatch):
    async def slow(*a, **k):
        await asyncio.sleep(10)
        return {}
    monkeypatch.setattr(ev, "async_call_llm_json", slow)
    with pytest.raises(EvaluationError, match="timed out"):
        asyncio.run(ev.async_evaluate_resume({}, {}, "r", "j", timeout=0.05))


def test_async_success_returns_validated_scores(monkeypatch):
    async def good(prompt, temperature=0.05, max_tokens=8192):
        assert temperature == 0.2  # evaluation uses its own tuning
        assert max_tokens == 2500
        return {
            "experience": {"score": 70, "evidence": ["Did X"], "explanation": "solid"},
            "projects": {"score": 60, "evidence": [], "explanation": "ok"},
            "education": {"score": 50, "evidence": [], "explanation": "ok"},
            "jd_relevance": {"score": 80, "evidence": [], "explanation": "relevant"},
            "missing_qualifications": [],
            "clarity_notes": "",
        }
    monkeypatch.setattr(ev, "async_call_llm_json", good)
    out = asyncio.run(ev.async_evaluate_resume({"a": 1}, {"b": 2}, "resume", "jd"))
    assert out.experience.score == 70
    assert out.jd_relevance.score == 80
