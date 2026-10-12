"""CareerBuddy keyword knowledge store tests (no chroma, no embeddings)."""
import tests.conftest  # noqa: F401
from Career_Buddy_rag.embeddings_store import EmbeddingsStore


def test_initialize_without_downloads():
    store = EmbeddingsStore()
    store.initialize()
    assert len(store._documents) > 50


def test_query_returns_ranked_results():
    store = EmbeddingsStore()
    store.initialize()
    res = store.query("Python Developer", n_results=3)
    assert 1 <= len(res) <= 3
    assert "content" in res[0] and "metadata" in res[0]
    assert "title" in res[0]["metadata"]


def test_context_string():
    store = EmbeddingsStore()
    ctx = store.get_relevant_context("frontend react roadmap", n_results=2)
    assert isinstance(ctx, str) and len(ctx) > 0


def test_no_chromadb_dependency():
    import Career_Buddy_rag.embeddings_store as mod
    import inspect
    src = inspect.getsource(mod)
    assert "chromadb" not in src or "NO embeddings, NO ChromaDB" in src
    assert "PersistentClient" not in src
    assert not hasattr(mod.EmbeddingsStore, "collection")


def test_query_router_greeting():
    from Career_Buddy_rag.query_router import QueryRouter
    router = QueryRouter()
    res = router.classify("hi")
    assert res["intent"] == "casual"
    assert res["needs_rag"] is False
    assert res["needs_web"] is False


def test_query_router_llm_routing(monkeypatch):
    import Career_Buddy_rag.query_router as qr_mod
    from Career_Buddy_rag.query_router import QueryRouter

    def fake_call_llm_json(prompt, model=None, **kwargs):
        return {"intent": "rag_web", "needs_rag": True, "needs_web": True, "reason": "Salary query"}

    monkeypatch.setattr(qr_mod, "call_llm_json", fake_call_llm_json)
    router = QueryRouter()
    res = router.classify("What is AI engineer salary?")
    assert res["intent"] == "rag_web"
    assert res["needs_rag"] is True
    assert res["needs_web"] is True


def test_query_router_fallback(monkeypatch):
    import Career_Buddy_rag.query_router as qr_mod
    from Career_Buddy_rag.query_router import QueryRouter

    def boom(*args, **kwargs):
        raise RuntimeError("API fail")

    monkeypatch.setattr(qr_mod, "call_llm_json", boom)
    router = QueryRouter()
    res = router.classify("some query")
    assert res["intent"] == "rag"
    assert res["needs_rag"] is True
    assert res["needs_web"] is False
