from fastapi import APIRouter
from pydantic import BaseModel
from services.chat_service import chat, clear

router = APIRouter()

class ChatReq(BaseModel):
    message: str
    use_web_search: bool = False

@router.post("/api/chat")
async def chat_route(req: ChatReq):
    return chat(req.message, req.use_web_search)

@router.post("/api/chat/clear")
async def clear_route():
    return {"status":"cleared","message": clear()}

@router.get("/api/health")
async def health():
    return {"status":"online","name":"CareerBuddy AI","brain_loaded": True}
