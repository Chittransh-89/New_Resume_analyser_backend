"""LLM service argument-handling tests (regression: temperature/max_tokens).

The evaluation and bullet code call async_call_llm_json with temperature and
max_tokens. These tests prove the function accepts and forwards them, using
mocks so no real API key or network is needed.
"""
import asyncio
import tests.conftest  # noqa: F401
import services.llm_service as llm


def test_async_json_accepts_tuning_params(monkeypatch):
    seen = {}

    async def fake_to_thread(func, *args, **kwargs):
        seen["func"] = func
        seen["kwargs"] = kwargs
        return {"ok": True}

    monkeypatch.setattr(llm.asyncio, "to_thread", fake_to_thread)
    out = asyncio.run(llm.async_call_llm_json("hello", temperature=0.2, max_tokens=2500))
    assert out == {"ok": True}
    assert seen["func"] is llm.call_llm_json
    assert seen["kwargs"]["temperature"] == 0.2
    assert seen["kwargs"]["max_tokens"] == 2500


def test_sync_json_forwards_to_llm_in_json_mode(monkeypatch):
    seen = {}

    def fake_call_llm(prompt, model=None, temperature=0.05, max_tokens=8192, is_json=False):
        seen.update(temperature=temperature, max_tokens=max_tokens, is_json=is_json)
        return '{"a": 1}'

    monkeypatch.setattr(llm, "call_llm", fake_call_llm)
    out = llm.call_llm_json("hello", temperature=0.3, max_tokens=3000)
    assert out == {"a": 1}
    assert seen["temperature"] == 0.3
    assert seen["max_tokens"] == 3000
    assert seen["is_json"] is True  # JSON mode must stay on for parsing


def test_default_tuning_matches_plain_calls(monkeypatch):
    # Callers that pass no tuning (parser, classifier, review) keep old behavior.
    seen = {}

    def fake_call_llm(prompt, model=None, temperature=0.05, max_tokens=8192, is_json=False):
        seen.update(temperature=temperature, max_tokens=max_tokens)
        return "{}"

    monkeypatch.setattr(llm, "call_llm", fake_call_llm)
    llm.call_llm_json("hello")
    assert seen == {"temperature": 0.05, "max_tokens": 8192}
