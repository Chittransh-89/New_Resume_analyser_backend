"""
CareerBuddy Query Router
Purpose:
    Understand the user's query and decide what retrieval is required.

Possible decisions:
    - casual      -> no RAG, no web
    - rag         -> use ChromaDB RAG
    - rag_web     -> use ChromaDB + Web Search
    - off_topic   -> no retrieval

LLM Provider:
    This router uses the centralized LLM service.
    Development:
        Ollama

    Deployment:
        Gemini
    The provider is controlled by services/llm_service.py.
"""

import json
import logging
import os
import re
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

from services.llm_service import call_llm_json

# PROMPT
PROMPTS_DIR = Path(__file__).parent.parent / "prompts"

query_router_system_prompt = (
    PROMPTS_DIR / "query_router_system_prompt.txt"
).read_text(encoding="utf-8")


# QUERY ROUTER
class QueryRouter:

    def __init__(self):

        self.system_prompt = query_router_system_prompt

    def classify(self, query):

        query = query.strip()

        # Fast path for simple greetings
        if self._is_simple_greeting(query):
            return {
                "intent": "casual",
                "needs_rag": False,
                "needs_web": False,
                "reason": "Simple greeting"
            }

        try:

            # BUILD ROUTER PROMPT
            router_prompt = f"""{self.system_prompt}
            User Query:{query}"""

            result = call_llm_json(
                prompt=router_prompt,
                model=None
            )

            print("🔎 Router result:",repr(result))
            logger.info("🔎 Router result: %s", repr(result))

            # VALIDATE RESULT
            return self._validate_result(result)

        except Exception as e:
            print(f"❌ Query Router Error: {e}")
            logger.exception("❌ Query Router Error: %s", e)

            # SAFE FALLBACK
            # If routing fails, use RAG rather than returning
            # an unsupported answer.

            return {
                "intent": "rag",
                "needs_rag": True,
                "needs_web": False,
                "reason": (
                    "Router failed; "
                    "using safe RAG fallback"
                )
            }
        
    # SIMPLE GREETING CHECK
    def _is_simple_greeting(self, query):

        q = query.lower().strip()

        greetings = {
            "hi",
            "hello",
            "hey",
            "hii",
            "hiii",
            "how are you",
            "what's up",
            "sup",
            "thanks",
            "thank you",
            "bye",
            "goodbye",
            "good morning",
            "good evening",
            "good night"
        }

        if q in greetings:
            return True

        # Examples:
        #
        # "hi bro"
        # "hello bro"
        # "hey there"

        if re.fullmatch(
            r"(hi|hello|hey|hii|hiii)(\s+\w+)?[!.]?",
            q
        ):
            return True
        return False

    # RESULT VALIDATION
    def _validate_result(self, result):
        valid_intents = {
            "casual",
            "rag",
            "rag_web",
            "off_topic"
        }

        # Make sure LLM returned a dictionary
        if not isinstance(result, dict):
            raise ValueError(
                "Router did not return a JSON object"
            )
        # Get intent
        intent = result.get("intent")

        if intent not in valid_intents:
            raise ValueError(f"Invalid router intent: {intent}")

        # DERIVE FLAGS FROM INTENT
        # Don't blindly trust the model's booleans.

        if intent == "casual":
            needs_rag = False
            needs_web = False

        elif intent == "rag":
            needs_rag = True
            needs_web = False

        elif intent == "rag_web":
            needs_rag = True
            needs_web = True

        elif intent == "off_topic":
            needs_rag = False
            needs_web = False

        # FINAL ROUTER RESULT
        return {
            "intent": intent,
            "needs_rag": needs_rag,
            "needs_web": needs_web,
            "reason": result.get(
                "reason",
                "No reason provided"
            )
        }

# TEST
if __name__ == "__main__":

    router = QueryRouter()

    test_queries = [
        "hi",
        "hello bro",
        "What is Python?",
        "What skills do I need to become an AI Engineer?",
        "What is the current AI Engineer salary in India?",
        "Which companies are hiring AI engineers?",
        "Latest AI trends",
        "free resources to learn Python",
        "Best Python courses",
        "Best Bollywood movies",
        "What is the weather today?"
    ]

    for query in test_queries:
        print("\n" + "=" * 70)
        logger.info("\n" + "=" * 70)
        print(f"QUERY: {query}")
        logger.info("QUERY: %s", query)
        print("=" * 70)
        logger.info("=" * 70)

        result = router.classify(query)
        print(
            json.dumps(
                result,
                indent=4
            )
        )
        logger.info(
            "%s",
            json.dumps(
                result,
                indent=4
            )
        )