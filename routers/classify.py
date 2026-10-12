from fastapi import APIRouter, UploadFile, File, HTTPException
import asyncio
from services.pdf_service import extract_text, validate_pdf_upload, looks_scanned
from services.classifier import classify_single

router = APIRouter()

MAX_UPLOAD_BYTES = 10 * 1024 * 1024


@router.post("/classify/")
async def classify(file: UploadFile = File(...)):
    pdf_bytes = await file.read()
    ok, err = validate_pdf_upload(pdf_bytes, filename=file.filename or "", max_bytes=MAX_UPLOAD_BYTES)
    if not ok:
        raise HTTPException(status_code=400, detail=err)
    text = await asyncio.to_thread(extract_text, pdf_bytes)
    if not text.strip():
        raise HTTPException(
            status_code=400,
            detail="Could not extract text from PDF. If scanned/image-only, export a text-based PDF or enable OCR.",
        )
    result = await asyncio.to_thread(classify_single, text)
    is_resume = result["type"] == "RESUME"
    response = {"validation": {**result, "resume": is_resume}}
    if looks_scanned(text):
        response["validation"]["scanned_warning"] = (
            "Very little text extracted; file may be scanned. Results may be unreliable."
        )
    return response
