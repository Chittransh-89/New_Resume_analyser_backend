from fastapi import APIRouter, UploadFile, File
import asyncio
from services.pdf_service import extract_text
from services.classifier import classify_single

router = APIRouter()

@router.post("/classify/")
async def classify(file: UploadFile = File(...)):
    pdf_bytes = await file.read()
    text = await asyncio.to_thread(extract_text, pdf_bytes)
    result = await asyncio.to_thread(classify_single, text)
    is_resume = result["type"] == "RESUME"
    return {"validation": {**result, "resume": is_resume}}
