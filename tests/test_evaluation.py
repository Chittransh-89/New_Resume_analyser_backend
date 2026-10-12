"""LLM evaluation validation + failure-handling tests (LLM mocked)."""
import asyncio
import tests.conftest  # noqa: F401
import services.evaluation as ev


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
        try:
            ev.validate_evaluation(bad)
        except ValueError:
            pass
        else:
            raise AssertionError(f"should reject {bad!r}")


def test_async_fallback_on_api_error(monkeypatch):
    async def boom(*a, **k):
        raise RuntimeError("429 rate limit exceeded")
    monkeypatch.setattr(ev, "async_call_llm_json", boom)
    out = asyncio.run(ev.async_evaluate_resume({}, {}, "r", "j", timeout=5))
    assert out.experience.score == 0
    assert "LLM" in out.experience.explanation


def test_async_fallback_on_invalid_json(monkeypatch):
    async def bad(*a, **k):
        return {"not": "the schema", "experience": {"score": "nan!"}}
    monkeypatch.setattr(ev, "async_call_llm_json", bad)
    out = asyncio.run(ev.async_evaluate_resume({}, {}, "r", "j", timeout=5))
    # "nan!" coerces to 0 via validator; still a valid object, no crash
    assert isinstance(out, ev.LLMEvaluation)


def test_async_timeout(monkeypatch):
    async def slow(*a, **k):
        await asyncio.sleep(10)
        return {}
    monkeypatch.setattr(ev, "async_call_llm_json", slow)
    out = asyncio.run(ev.async_evaluate_resume({}, {}, "r", "j", timeout=0.05))
    assert out.jd_relevance.score == 0
