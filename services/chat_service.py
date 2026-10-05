# services/chat_service.py

from Career_Buddy_rag.new_brain import CareerBuddyBrain


# Central CareerBuddy brain
brain = CareerBuddyBrain()

def chat(message: str, use_web_search: bool = False) -> dict:
    """
    Main chat entry point.

    Flow:
        API → chat_service → CareerBuddyBrain
        → QueryRouter → RAG/Web → LLM
    """

    return brain.chat(
        user_query=message,
        use_web_search=use_web_search
    )


def clear():
    """
    Clear CareerBuddy conversation history.
    """

    return brain.reset_chat()