"""
CareerBuddy Query Router

Purpose:
    Understand the user's query and decide what retrieval is required.

Possible decisions:
    - casual       -> no RAG, no web
    - rag          -> use ChromaDB RAG
    - rag_web      -> use ChromaDB + Web Search
    - off_topic    -> no retrieval

Development:
    Uses Ollama locally.

Deployment:
    Replace the Ollama client with Gemini.
"""

import json
import os
import re
import sys
from openai import OpenAI
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import Config

from pathlib import Path
PROMPTS_DIR = Path(__file__).parent.parent / "prompts"
query_router_system_prompt = (PROMPTS_DIR / "query_router_system_prompt.txt").read_text(encoding="utf-8")

class QueryRouter:

    def __init__(self):

        # ==========================================================
        # DEVELOPMENT: OLLAMA
        # ==========================================================
        # Ollama provides an OpenAI-compatible API.
        #
        # Example:
        # ollama serve
        #
        # Then:
        # http://localhost:11434/v1
        #
        # Change this model to whatever model you have installed.
        # ==========================================================

        self.client = OpenAI(
            base_url="http://localhost:11434/v1",
            api_key="ollama"
        )

        self.model_name = "gemma4:e4b"

        # ==========================================================
        # DEPLOYMENT: GEMINI
        # ==========================================================
        # When deploying, remove/comment the Ollama client above
        # and use your Gemini configuration here.
        #
        # Example approach:
        #
        # from google import genai
        #
        # self.client = genai.Client(
        #     api_key=Config.GEMINI_API_KEY
        # )
        #
        # Then replace classify() with the Gemini generate call.
        # ==========================================================

        self.system_prompt = query_router_system_prompt
    def classify(self, query):
        query = query.strip()

        if self._is_simple_greeting(query):
            return {
                "intent": "casual",
                "needs_rag": False,
                "needs_web": False,
                "reason": "Simple greeting"
            }

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": self.system_prompt
                    },
                    {
                        "role": "user",
                        "content": query
                    }
                ],
                temperature=0,
                max_tokens=200
            )

            message = response.choices[0].message

            print("🔎 Router raw content:", repr(message.content))

            raw_output = (message.content or "").strip()

            if not raw_output:
                raise ValueError(
                    "Router model returned empty response"
                )

            result = self._parse_json(raw_output)

            return self._validate_result(result)

        except Exception as e:
            print(f"❌ Query Router Error: {e}")

            return {
                "intent": "rag",
                "needs_rag": True,
                "needs_web": False,
                "reason": "Router failed; using safe RAG fallback"
            }

    # ==============================================================
    # SIMPLE GREETING CHECK
    # ==============================================================

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

        # "hi bro", "hello bro", "hey there"
        if re.fullmatch(
            r"(hi|hello|hey|hii|hiii)(\s+\w+)?[!.]?",
            q
        ):
            return True

        return False

    # ==============================================================
    # JSON PARSER
    # ==============================================================

    def _parse_json(self, text):
        text = text.strip()

        # Remove markdown code fences
        text = re.sub(
            r"^```(?:json)?\s*|\s*```$",
            "",
            text,
            flags=re.IGNORECASE
        ).strip()

        try:
            return json.loads(text)

        except json.JSONDecodeError:

            match = re.search(
                r"\{.*\}",
                text,
                re.DOTALL
            )

            if match:
                return json.loads(match.group())

            raise ValueError(
                f"Router returned invalid JSON: {text}"
            )
    # ==============================================================
    # RESULT VALIDATION
    # ==============================================================

    def _validate_result(self, result):

        valid_intents = {
            "casual",
            "rag",
            "rag_web",
            "off_topic"
        }

        intent = result.get("intent")

        if intent not in valid_intents:
            raise ValueError(
                f"Invalid router intent: {intent}"
            )

        # Don't blindly trust the model's booleans.
        # Derive them from the intent.

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

        return {
            "intent": intent,
            "needs_rag": needs_rag,
            "needs_web": needs_web,
            "reason": result.get(
                "reason",
                "No reason provided"
            )
        }
# ==============================================================
# TEST
# ==============================================================

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
        print(f"QUERY: {query}")
        print("=" * 70)

        result = router.classify(query)

        print(json.dumps(result, indent=4))