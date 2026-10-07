import logging
import os
import sys

logger = logging.getLogger(__name__)

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))

sys.path.append(CURRENT_DIR)
sys.path.append(ROOT_DIR)

from config import Config
from openai import OpenAI
from embeddings_store import EmbeddingsStore
from services.web_search import WebSearcher
import re
from query_router import QueryRouter
from pathlib import Path

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"

SYSTEM_PROMPT = (
    PROMPTS_DIR / "SYSTEM_PROMPT.txt"
).read_text(encoding="utf-8")

QUESTION_TYPE_DETECTION_PROMPT = (
    PROMPTS_DIR / "QUESTION_TYPE_DETECTION_PROMPT.txt"
).read_text(encoding="utf-8")

class CareerBuddyBrain:

    # dependencies initialize
    def __init__(self):
        Config.validate()  # Validate config on initialization
        # self.client = OpenAI(
        #     api_key=Config.GEMINI_API_KEY, 
        #     base_url=Config.BASE_URL
        # )
        self.client = OpenAI(
            base_url=Config.BASE_URL,
            api_key=Config.GEMINI_API_KEY
        )
        self.model = Config.LLM_MODEL
        # self.model = "gemma4:e4b"
        self.system_prompt = SYSTEM_PROMPT
        self.web_searcher = WebSearcher()
        self.embeddings_store = EmbeddingsStore()
        self.embeddings_store.initialize()

        self.router = QueryRouter()
        print(f"🤖 Model loaded: {self.model}")
        logger.info("🤖 Model loaded: %s", self.model)
        print("🧠 Initializing knowledge base...")
        logger.info("🧠 Initializing knowledge base...")
        print("✅ CareerBuddy ready!\n")
        logger.info("✅ CareerBuddy ready!\n")

        self.chat_history = []  # Initialize chat history
        self.web_triggers = [
                # High confidence - ye definitely search chahte hain
                "salary", "package", "ctc", "lpa",
                "hiring", "jobs", "openings", "vacancy",
                "trending", "demand", "market",
                "youtube", "video", "tutorial", "course",
                "free resources", "website",
                "find me", "look up", "search for",
                "companies hiring", "startups",
                "news", "update", "recent",
                "roadmap", "resources to learn",
                "how to become", "getting started",
                "playlist", "recommend", "suggest",
                "best way to learn", "free course",
                "projects for", "practice platform",
            ]

    # decide: web chahiye ya nahi?
    def needs_web_search(self, query):
        q = query.lower().strip()

        # 1. SIMPLE GREETINGS / CASUAL QUERIES
        greetings = {"hi", "hello", "hey", "hii", "hiii", "how are you", "what's up", "sup", "thanks", "thank you", "ok", "okay", "bye", "goodbye", "good morning", "good evening", "good night"}

        # Exact greeting → NEVER use web search
        if q in greetings:
            return False

        # Examples:
        # "hi bro"
        # "hello bro"
        # "hey there"
        if re.fullmatch(r"(hi|hello|hey|hii|hiii)(\s+\w+)?[!.]?",q):
            return False

        # 2. VERY SHORT QUERY
        if len(q.split()) <= 3:

            # Allow important short queries such as:
            # "AI salary"
            # "AI jobs"
            # "AI roadmap"

            important_triggers = [
                "salary",
                "jobs",
                "hiring",
                "roadmap"
            ]
            if not any(trigger in q for trigger in important_triggers):
                return False

        # 3. WEB SEARCH TRIGGERS
        for trigger in self.web_triggers:
            if trigger in q:
                return True
            
        # 4. DEFAULT → NO WEB SEARCH
        return False

    # Bring Context from RAG
    def get_rag_context(self, user_query):
        return self.embeddings_store.get_relevant_context(
            query=user_query,
            n_results=Config.MAX_SEARCH_RESULTS
        )

    # Bring Context from Web Search
    def get_web_context(self, user_query):
        try:
            results = self.web_searcher.search_career_resources(user_query) or {}

            web = (
                results.get("web") or
                results.get("organic") or
                results.get("results") or
                []
            )
            yt = (
                results.get("youtube") or
                results.get("videos") or
                []
            )

            context = ""

            if web:
                context += "\nSEARCH LINKS (use these as-is, they are valid Google/YouTube search pages):\n"
                for r in web:
                    title   = r.get("title") or r.get("name") or "Resource"
                    url     = r.get("url") or r.get("link") or r.get("href") or ""
                    snippet = r.get("snippet") or r.get("description") or r.get("body") or ""

                    if url and url.startswith("http"):
                        context += f"- {title}\n  URL: {url}\n  Info: {snippet}\n"

            if yt:
                context += "\nYOUTUBE SEARCH LINKS:\n"
                for v in yt:
                    title = v.get("title") or v.get("name") or "Video Search"
                    url   = v.get("url") or v.get("link") or v.get("href") or ""

                    if url and url.startswith("http"):
                        context += f"- {title}\n  URL: {url}\n"

            print(f"📝 Web context:\n{context[:500]}")
            logger.info("📝 Web context:\n%s", context[:500])
            return context.strip()

        except Exception as e:
            print(f"❌ Web error: {e}")
            logger.exception("❌ Web error: %s", e)
            import traceback
            traceback.print_exc()
            return ""

    def build_messages(self, user_query, rag_context, web_context=""):
        combined = f"RAG:\n{rag_context}"

        if web_context:
            combined += f"""
    ═══ AVAILABLE RESOURCES (backend only) ═══
    {web_context}
    ════════════════════════════════════════════
    
    Note: These links appear in UI sidebar. DO NOT include in response.
    """
    
        # ✅ Smart instruction - question type detect karo
        combined += QUESTION_TYPE_DETECTION_PROMPT
        messages = [{
            "role": "system",
            "content": f"{self.system_prompt}\n\nCONTEXT:\n{combined}"
        }]

        if self.chat_history:
            messages.extend(self.chat_history[-6:])

        messages.append({"role": "user", "content": user_query})
        return messages

    # MAIN ORCHESTRATOR
    def chat(self, user_query, use_web_search=None):
        try:

             # 1. Understand query first
            route = self.router.classify(user_query)
            print(f"🧭 Router: {route}")
            logger.info("🧭 Router: %s", route)

            should_use_rag = route["needs_rag"]
            should_search = route["needs_web"]

            # 2. Legacy intent fallback
            if not should_search:
                should_search = self.needs_web_search(user_query)

            # 3. Explicit frontend request can force web search
            if use_web_search is True:
                should_search = True

            print(f"🧭 Final decision → RAG: {should_use_rag}, WEB: {should_search}")
            logger.info("🧭 Final decision → RAG: %s, WEB: %s", should_use_rag, should_search)

            # 2. RAG only when router says YES
            rag_context = ""

            if should_use_rag:
                print(f"🧠 Getting RAG context...")
                logger.info("🧠 Getting RAG context...")
                rag_context = self.get_rag_context(user_query)

            # 3. Web only when router says YES
            web_context = ""

            if should_search:
                print(f"🌐 Web search Query: {user_query}")
                logger.info("🌐 Web search Query: %s", user_query)
                web_context = self.get_web_context(user_query)

            messages = self.build_messages(
                user_query, 
                rag_context, 
                web_context
            )

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=Config.TEMPERATURE,
                max_tokens=Config.MAX_TOKENS,
            )

            answer = response.choices[0].message.content

            answer = self._clean_response(answer)

            # 8. History
            self.chat_history.append({"role": "user", "content": user_query})

            self.chat_history.append({"role": "assistant", "content": answer})

            if len(self.chat_history) > Config.MAX_CHAT_HISTORY:
                self.chat_history = self.chat_history[-Config.MAX_CHAT_HISTORY:]

            # ✅ Links context se nikalo, answer se nahi
            all_links   = self._extract_web_links(web_context)
            yt_links    = self._extract_youtube_links(web_context)
            google_links = [link for link in all_links if "google.com" in link]
            
            # ✅ Debug
            print(f"🔗 Google links: {len(google_links)}")
            logger.info("🔗 Google links: %s", len(google_links))
            print(f"🎥 YT links:     {len(yt_links)}")
            logger.info("🎥 YT links:     %s", len(yt_links))

            return {
                "response"       : answer,
                "used_web_search": should_search,
                "google_links"   : google_links,   # ✅ alag key
                "youtube_links"  : yt_links        # ✅ alag key
            }

        except Exception as e:
            return {
                "response"       : f"❌ Error: {str(e)}",
                "used_web_search": False,
                "google_links"   : [],
                "youtube_links"  : []
            }
    

    # answer clean
    def _clean_response(self, text):
        """Remove undefined/null links."""

        # [Text](undefined) → Text
        text = re.sub(r'\[([^\]]+)\]\(undefined\)', r'\1', text)

        # [Text](null) → Text
        text = re.sub(r'\[([^\]]+)\]\(null\)', r'\1', text)

        # [Text]() → Text
        text = re.sub(r'\[([^\]]+)\]\(\s*\)', r'\1', text)

        # Bare undefined / null words
        text = re.sub(r'\bundefined\b', '', text)
        text = re.sub(r'\bnull\b', '', text)

        # Extra blank lines
        text = re.sub(r'\n{3,}', '\n\n', text)

        print("✅ Response cleaned")
        logger.info("✅ Response cleaned")

        return text.strip()

    # YT links
    def _extract_youtube_links(self, text):
        """YouTube links extract karo - search + direct dono"""

        if not text:
            return []

        patterns = [
            r'https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+',
            r'https?://youtu\.be/[\w-]+',
            r'https?://(?:www\.)?youtube\.com/playlist\?list=[\w-]+',
            r'https?://(?:www\.)?youtube\.com/results\?search_query=[\w%+.-]+',
        ]

        links = []

        for pattern in patterns:
            links.extend(re.findall(pattern, text))

        return list(dict.fromkeys(links))

    # web links
    def _extract_web_links(self, text):
        if not text:
            return []

        # Markdown links: [text](url)
        markdown_urls = re.findall(
            r'\[([^\]]+)\]\((https?://[^\s\)]+)\)',
            text
        )

        # Bare URLs
        bare_urls = re.findall(
            r'(?<!\()(https?://[^\s\)\]\,\'"<>]+)',
            text
        )

        all_links = [url for _, url in markdown_urls] + bare_urls

        cleaned = []

        for link in all_links:
            # trailing punctuation remove
            link = re.sub(r'[.,;:!?\)\]]+$', '', link)

            if link.startswith('http'):
                cleaned.append(link)

        return list(dict.fromkeys(cleaned))

    def reset_chat(self):
        self.chat_history = []
        return "Cleared!"

    def get_history(self):
        return self.chat_history

if __name__ == "__main__":
    brain = CareerBuddyBrain()

    print("\n🔍 Methods check:")
    logger.info("\n🔍 Methods check:")
    print(f"  get_rag_context:   {hasattr(brain, 'get_rag_context')}")
    logger.info("  get_rag_context:   %s", hasattr(brain, 'get_rag_context'))
    print(f"  get_web_context:   {hasattr(brain, 'get_web_context')}")
    logger.info("  get_web_context:   %s", hasattr(brain, 'get_web_context'))
    print(f"  needs_web_search:  {hasattr(brain, 'needs_web_search')}")
    logger.info("  needs_web_search:  %s", hasattr(brain, 'needs_web_search'))
    print(f"  _clean_response:   {hasattr(brain, '_clean_response')}")
    logger.info("  _clean_response:   %s", hasattr(brain, '_clean_response'))
    print(f"  _extract_youtube_links: {hasattr(brain, '_extract_youtube_links')}")
    logger.info("  _extract_youtube_links: %s", hasattr(brain, '_extract_youtube_links'))

    test_questions = ["free resources to learn Python"]

    for i, q in enumerate(test_questions, 1):
        print(f"\n{'='*60}\n❓ Q{i}: {q}\n{'='*60}")
        logger.info("\n%s\n❓ Q%s: %s\n%s", '='*60, i, q, '='*60)
        result = brain.chat(q)
        print(result["response"])
        logger.info("%s", result["response"])
