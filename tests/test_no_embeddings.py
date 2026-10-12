"""No-embedding guard: fail if the scoring pipeline can load local models."""
import pathlib
import tests.conftest  # noqa: F401

ROOT = pathlib.Path(__file__).resolve().parent.parent
WATCHED = [
    ROOT / "services" / "scoring.py",
    ROOT / "rule_matcher.py",
    ROOT / "services" / "evaluation.py",
    ROOT / "routers" / "analyze.py",
    ROOT / "requirements.txt",
]
BANNED = [
    "SentenceTransformer",
    "sentence-transformers",
    "sentence_transformers",
    "cosine_similarity",
    "sklearn",
    "chromadb",
    "torch",
]


def test_no_banned_imports_in_scoring_pipeline():
    offenders = []
    for path in WATCHED:
        text = path.read_text(encoding="utf-8")
        for term in BANNED:
            if term == "torch" and path.name == "requirements.txt":
                # 'torch' substring also matches 'pytorch' skill alias text — only
                # requirements/services matter; skills_map.py is excluded already.
                pass
            if term in text:
                # Allow deprecation comments mentioning removal.
                lines = [ln for ln in text.splitlines() if term in ln]
                # requirements.txt must have zero banned lines, no exceptions.
                if path.name == "requirements.txt":
                    offenders.append(f"{path.name}: {lines[0].strip()}")
                else:
                    # Code files: allow the word only in comments/docstrings
                    # explaining removal, not in import statements.
                    for ln in lines:
                        s = ln.strip()
                        if s.startswith(("import ", "from ")) or "= SentenceTransformer" in s or "SentenceTransformer(" in s:
                            offenders.append(f"{path.name}: {s}")
    assert not offenders, f"embedding remnants found: {offenders}"


def test_no_model_load_at_import():
    import services.scoring as scoring
    import rule_matcher
    assert not hasattr(scoring, "_model")
    assert not hasattr(rule_matcher, "_model")
    assert not hasattr(rule_matcher, "resume_embs")
