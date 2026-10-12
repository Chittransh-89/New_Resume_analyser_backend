"""API schema tests with LLM fully mocked (no network, no keys)."""
import io
import tests.conftest  # noqa: F401
from fastapi.testclient import TestClient

import services.evaluation as evaluation_mod
from services.evaluation import LLMEvaluation, CategoryScore


def _fake_eval():
    return LLMEvaluation(
        experience=CategoryScore(score=70, evidence=["Did X"], explanation="solid"),
        projects=CategoryScore(score=60, evidence=[], explanation="ok"),
        education=CategoryScore(score=50, evidence=[], explanation="ok"),
        jd_relevance=CategoryScore(score=80, evidence=[], explanation="relevant"),
        missing_qualifications=["Kubernetes"],
        clarity_notes="clear",
    )


def _client_with_mocks(monkeypatch):
    import routers.analyze as analyze_mod

    async def fake_parse_resume(text):
        return {"name": "Test", "email": "t@example.com", "experience_years": 2,
                "skills": ["Python"], "experience": [], "education": [], "projects": [{"name": "P"}]}

    async def fake_parse_jd(text):
        return {"job_title": "Backend Dev", "required_skills": ["Python"],
                "preferred_skills": ["Docker"], "responsibilities": [], "qualifications": []}

    def fake_classify_pair(a, b):
        return {"document_a": {"type": "RESUME", "job_role": "BACKEND_DEVELOPER"},
                "document_b": {"type": "JOB_DESCRIPTION", "job_role": "BACKEND_DEVELOPER"}}

    async def fake_review(prompt, **kw):
        return {"verdict": "Good Match", "strengths": ["s"], "weaknesses": ["w"], "reason": "r"}

    async def fake_improve(bullets, jd):
        return [{"original": b, "improved": b + " (improved)"} for b in bullets]

    monkeypatch.setattr(analyze_mod, "async_parse_resume", fake_parse_resume)
    monkeypatch.setattr(analyze_mod, "async_parse_jd", fake_parse_jd)
    monkeypatch.setattr(analyze_mod, "classify_pair", fake_classify_pair)
    monkeypatch.setattr(analyze_mod, "async_call_llm_json", fake_review)
    monkeypatch.setattr(analyze_mod, "improve_all", fake_improve)
    monkeypatch.setattr(evaluation_mod, "async_call_llm_json", fake_review)

    from main import app
    return TestClient(app)


def _pdf_bytes(text="Python developer with FastAPI experience. Docker and CI pipelines. " * 10):
    # Reuse the fixture builder proven in test_pdf_service (works with or
    # without PyMuPDF installed).
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
    from test_pdf_service import _make_pdf_bytes
    data = _make_pdf_bytes(text)
    from services.pdf_service import extract_text
    assert extract_text(data).strip(), "test PDF fixture not extractable"
    return data


def test_health_endpoints():
    from main import app
    c = TestClient(app)
    assert c.get("/health").json() == {"status": "ok"}
    assert c.get("/api/health").json()["status"] == "online"
    assert c.get("/").status_code == 200


def test_analyze_rejects_non_pdf():
    from main import app
    c = TestClient(app)
    r = c.post("/analyze/", files={"resume": ("r.pdf", b"nope", "application/pdf"),
                                   "jd": ("j.pdf", b"nope", "application/pdf")})
    assert r.status_code == 400


def test_analyze_rejects_empty_pdf():
    from main import app
    c = TestClient(app)
    empty = b"%PDF-1.4\n%EOF"
    r = c.post("/analyze/", files={"resume": ("r.pdf", empty, "application/pdf"),
                                   "jd": ("j.pdf", empty, "application/pdf")})
    assert r.status_code in (400, 500)


def test_analyze_e2e_mocked(monkeypatch):
    c = _client_with_mocks(monkeypatch)
    pdf = _pdf_bytes()
    r = c.post("/analyze/", files={"resume": ("resume.pdf", pdf, "application/pdf"),
                                   "jd": ("jd.pdf", pdf, "application/pdf")})
    assert r.status_code == 200, r.text
    body = r.json()
    for key in ("document_validation", "candidate", "job_needs", "analysis", "score", "review", "improvements"):
        assert key in body, f"missing {key}"
    assert 0 <= body["score"]["final_score"] <= 100
    assert "matched_skills" in body["analysis"] and "missing_skills" in body["analysis"]
    assert body["score"]["breakdown"]["formula"].startswith("final = 0.35")


def test_classify_rejects_non_pdf():
    from main import app
    c = TestClient(app)
    r = c.post("/classify/", files={"file": ("x.pdf", b"hello", "application/pdf")})
    assert r.status_code == 400


def test_chat_health_without_brain():
    from main import app
    c = TestClient(app)
    # Health must work even if GEMINI key missing / brain unloaded.
    assert c.get("/api/health").status_code == 200
