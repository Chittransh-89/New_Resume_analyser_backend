# services/chat_service.py — simplified brain
from openai import OpenAI
import config

# simple in-memory history (for real app use DB)
_history = []

client = OpenAI(api_key=config.GEMINI_API_KEY, base_url=config.BASE_URL) if config.GEMINI_API_KEY    else None
SYSTEM = "You are CareerBuddy, friendly tech career advisor. Be concise, use bullets."

def chat(message: str, use_web_search: bool = False) -> dict:
    if not client:
        return {
            "response":"❌ GEMINI_API_KEY missing",
            "used_web_search":False,
            "google_links":[],
            "youtube_links":[]
        }
    
    # TODO: add RAG (Chroma) + web_search here like old brain.py
    msgs=[{"role":"system","content":SYSTEM}]
    msgs.extend(_history[-6:])
    msgs.append({"role":"user","content":message})

    resp=client.chat.completions.create(
        model=config.LLM_MODEL, 
        messages=msgs, 
        temperature=config.TEMPERATURE, 
        max_tokens=config.MAX_TOKENS
    )
    ans=resp.choices[0].message.content

    _history.append({"role":"user","content":message})
    _history.append({"role":"assistant","content":ans})

    if len(_history)>config.MAX_CHAT_HISTORY: _history[:] = _history[-config.MAX_CHAT_HISTORY:]
    
    return {"response":ans,"used_web_search": use_web_search,"google_links":[],"youtube_links":[]}

def clear():
    _history.clear()
    return "Cleared!"
