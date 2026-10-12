# services/pdf_service.py — PDF -> text (FAST: PyMuPDF + pdfplumber fallback)
import logging
from io import BytesIO

logger = logging.getLogger(__name__)

# Safety limits (prevent OOM on hostile uploads; adjustable via callers).
MAX_PDF_BYTES = 10 * 1024 * 1024  # 10 MB
MIN_TEXT_CHARS = 20  # below this, treat as empty/scanned


def is_pdf_bytes(data: bytes) -> bool:
    """Check PDF magic bytes (%PDF) to reject non-PDF uploads early."""
    if not data or len(data) < 5:
        return False
    return data[:5] == b"%PDF-"


def looks_scanned(text: str, num_pages: int = 1) -> bool:
    """Heuristic: very little extractable text per page suggests scanned image PDF."""
    if num_pages <= 0:
        num_pages = 1
    stripped = (text or "").strip()
    if not stripped:
        return True
    return len(stripped) < MIN_TEXT_CHARS * num_pages


def extract_text(pdf_bytes: bytes) -> str:
    """Fast extract: try PyMuPDF (fitz) first, fallback to pdfplumber."""
    if not pdf_bytes:
        return ""
    # FAST PATH: PyMuPDF (2x faster, native)
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        parts = [page.get_text() for page in doc]
        doc.close()
        txt = "\n\n".join(p for p in parts if p)
        if txt.strip():
            return txt.lower()
    except ImportError:
        pass
    except Exception as e:
        print(f"[pdf] fitz failed, fallback: {e}")
        logger.exception("[pdf] fitz failed, fallback: %s", e)

    # FALLBACK: pdfplumber
    try:
        import pdfplumber
        parts = []
        with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
            for i, page in enumerate(pdf.pages):
                try:
                    t = page.extract_text()
                    if t:
                        parts.append(t)
                except Exception as e:
                    print(f"[pdf] page {i} failed: {e}")
                    logger.exception("[pdf] page %s failed: %s", i, e)
        return "\n\n".join(parts).lower()
    except Exception as e:
        print(f"[pdf] extract error: {e}")
        logger.exception("[pdf] extract error: %s", e)
        return ""


def validate_pdf_upload(data: bytes, filename: str = "", max_bytes: int = MAX_PDF_BYTES) -> tuple:
    """
    Validate an uploaded PDF before extraction.

    Returns (ok: bool, error: str). Never raises.
    Checks: non-empty, size limit, PDF magic bytes.
    Content extraction/emptiness is checked by the caller after extract_text.
    """
    if not data:
        return False, "Empty file uploaded."
    if max_bytes and len(data) > max_bytes:
        return False, f"File too large ({len(data)} bytes, max {max_bytes})."
    if filename and not filename.lower().endswith(".pdf"):
        return False, "Only PDF files are accepted."
    if not is_pdf_bytes(data):
        return False, "File is not a valid PDF (missing %PDF header)."
    return True, ""
