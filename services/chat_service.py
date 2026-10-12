# services/chat_service.py — lazy CareerBuddy wiring (no import-time heavy init).

_brain = None


def _get_brain():
    """Lazily create the central brain so `import main` never downloads models."""
    global _brain
    if _brain is None:
        from Career_Buddy_rag.new_brain import CareerBuddyBrain
        _brain = CareerBuddyBrain()
    return _brain


def chat(message: str, use_web_search: bool = False) -> dict:
    """
    Main chat entry point.

    Flow:
        API → chat_service → CareerBuddyBrain
        → QueryRouter → keyword RAG/Web → LLM
    """
    try:
        brain = _get_brain()
    except Exception as e:
        return {
            "response": f"❌ Chat service unavailable: {str(e)[:200]}",
            "used_web_search": False,
            "google_links": [],
            "youtube_links": [],
        }
    return brain.chat(
        user_query=message,
        use_web_search=use_web_search,
    )


def clear():
    """Clear CareerBuddy conversation history."""
    try:
        brain = _get_brain()
    except Exception:
        return "Cleared!"
    return brain.reset_chat()
