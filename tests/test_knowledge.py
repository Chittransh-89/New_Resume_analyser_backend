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
