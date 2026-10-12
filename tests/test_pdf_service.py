"""PDF extraction + upload validation tests (no LLM)."""
import tests.conftest  # noqa: F401  (ensures sys.path)
from services import pdf_service


def _make_pdf_bytes(text: str) -> bytes:
    """Build a minimal text PDF in memory via PyMuPDF (fallback: raw)."""
    try:
        import fitz
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((72, 72), text)
        data = doc.tobytes()
        doc.close()
        return data
    except Exception:
        # Minimal hand-rolled PDF with one text line (pdfplumber/fitz can read).
        esc = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        body = (
            "%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
            "2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
            "3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]/Contents 4 0 R/Resources<</Font<</F1 5 0 R>>>>>>endobj\n"
            f"4 0 obj<</Length {len(esc) + 44}>>stream\nBT /F1 12 Tf 72 720 Td ({esc}) Tj ET\nendstream\nendobj\n"
            "5 0 obj<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>endobj\n"
            "trailer<</Root 1 0 R>>\n"
        )
        return body.encode("latin-1")


def test_extract_text_simple_pdf():
    data = _make_pdf_bytes("Python FastAPI Docker")
    assert pdf_service.is_pdf_bytes(data)
    text = pdf_service.extract_text(data)
    assert "python" in text  # extract_text lowercases


def test_empty_bytes_returns_empty():
    assert pdf_service.extract_text(b"") == ""


def test_non_pdf_rejected():
    ok, err = pdf_service.validate_pdf_upload(b"not a pdf", filename="resume.pdf")
    assert not ok and "valid PDF" in err


def test_empty_upload_rejected():
    ok, err = pdf_service.validate_pdf_upload(b"", filename="resume.pdf")
    assert not ok and "Empty" in err


def test_wrong_extension_rejected():
    data = _make_pdf_bytes("hello")
    ok, err = pdf_service.validate_pdf_upload(data, filename="resume.txt")
    assert not ok and "Only PDF" in err


def test_oversize_rejected():
    data = b"%PDF-" + b"x" * 100
    ok, err = pdf_service.validate_pdf_upload(data, filename="r.pdf", max_bytes=10)
    assert not ok and "too large" in err.lower()


def test_scanned_heuristic():
    assert pdf_service.looks_scanned("") is True
    assert pdf_service.looks_scanned("Python " * 50) is False
