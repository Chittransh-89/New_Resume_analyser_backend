# services/pdf_service.py — PDF -> text (FAST: PyMuPDF + pdfplumber fallback)
from io import BytesIO

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
        return "\n\n".join(parts).lower()
    except Exception as e:
        print(f"[pdf] extract error: {e}")
        return ""
