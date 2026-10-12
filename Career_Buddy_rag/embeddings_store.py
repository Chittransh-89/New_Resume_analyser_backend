"""Keyword-based career knowledge store (NO embeddings, NO ChromaDB, NO torch).

Refactor note: the original ChromaDB + embedding implementation required
downloading a local SentenceTransformer model at startup, which breaks
lightweight deployment. This replacement keeps the SAME public API
(EmbeddingsStore, initialize, query, get_relevant_context) so
Career_Buddy_rag/new_brain.py and services/chat_service.py keep working,
but retrieval is deterministic keyword overlap over the bundled
database/*.py files. No network, no model download, no vector DB.
"""
import logging
import os
import re
import sys

logger = logging.getLogger(__name__)

# Add the parent directory (NEW_RESUME_ANALYSER_BACKEND) to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import Config
# ===========================================
# IMPORTS (bundled static knowledge base)
# ===========================================
try:
    from Career_Buddy_rag.database.career_database.career_data import CAREER_PATHS
except ImportError:  # fallback when imported as top-level module
    from database.career_database.career_data import CAREER_PATHS
try:
    from Career_Buddy_rag.database.skills_database.skills_data import SKILLS_DATABASE
except ImportError:
    from database.skills_database.skills_data import SKILLS_DATABASE
try:
    from Career_Buddy_rag.database.resources_database.resources_data import (
        LEARNING_PLATFORMS,
        YOUTUBE_CHANNELS,
        INTERVIEW_RESOURCES,
        COMMUNITIES,
    )
except ImportError:
    from database.resources_database.resources_data import (
        LEARNING_PLATFORMS,
        YOUTUBE_CHANNELS,
        INTERVIEW_RESOURCES,
        COMMUNITIES,
    )


def _tokens(text: str) -> set:
    return set(re.findall(r"[a-z0-9+.#]+", (text or "").lower()))


_STOPWORDS = {
    "the", "a", "an", "and", "or", "for", "to", "of", "in", "on", "with",
    "how", "what", "which", "become", "be", "is", "are", "i", "me", "my",
    "need", "needs", "want", "learn", "free", "best", "top",
}


def _score(query_tokens: set, doc_tokens: set) -> float:
    if not query_tokens or not doc_tokens:
        return 0.0
    q = query_tokens - _STOPWORDS
    if not q:
        q = query_tokens
    overlap = q & doc_tokens
    # Recall-oriented: how much of the query is covered + small precision bonus.
    recall = len(overlap) / max(1, len(q))
    precision = len(overlap) / max(1, len(doc_tokens))
    return recall + 0.1 * precision


class EmbeddingsStore:
    """Deterministic keyword store with the same interface as the old vector store."""

    def __init__(self):
        """No external client; data lives in memory."""
        self._documents: list = []
        self._initialized = False

        print("📁 Knowledge store: in-memory keyword index (no ChromaDB, no embeddings)")
        logger.info("📁 Knowledge store: in-memory keyword index (no ChromaDB, no embeddings)")

    def initialize(self):
        """Build in-memory documents from knowledge base data (idempotent)."""
        if self._initialized:
            return
        print("📚 Building keyword knowledge store...")
        logger.info("📚 Building keyword knowledge store...")

        documents = []

        # PART 1: CAREER PATHS
        print("  → Indexing careers...")
        logger.info("  → Indexing careers...")

        for career_id, career in CAREER_PATHS.items():
            doc = f"""Career: {career['title']}
                Category: {career['category']}
                Description: {career['description']}
                Difficulty: {career.get('difficulty', 'N/A')}
                Demand: {career.get('demand', 'N/A')}
                Job Titles: {', '.join(career.get('job_titles', []))}
                Salary (India): {career.get('salary_range', {}).get('india', 'N/A')}
                Salary (US): {career.get('salary_range', {}).get('us', 'N/A')}
                Salary (Remote): {career.get('salary_range', {}).get('remote', 'N/A')}
                Companies Hiring: {', '.join(career.get('companies_hiring', [])[:5])}
                Top Certifications: {', '.join(career.get('certifications', [])[:3])}
                Required Skills: {', '.join([skill for skills in career.get('required_skills', {}).values() for skill in skills])}"""
            documents.append({
                "content": doc,
                "metadata": {"type": "career", "career_id": career_id, "title": career['title'],
                             "category": career['category'], "difficulty": career.get('difficulty', 'N/A')},
            })

            skills_doc = f"Skills needed for {career['title']}:\n"
            for skill_cat, skills in career.get('required_skills', {}).items():
                skills_doc += f"  {skill_cat}: {', '.join(skills)}\n"
            documents.append({
                "content": skills_doc,
                "metadata": {"type": "career_skills", "career_id": career_id, "title": f"{career['title']} Skills"},
            })

            roadmap_doc = f"Learning Roadmap for {career['title']}:\n"
            for phase in career.get('roadmap', []):
                roadmap_doc += f"\n{phase['phase']}:\n"
                for task in phase['tasks']:
                    roadmap_doc += f"  - {task}\n"
            documents.append({
                "content": roadmap_doc,
                "metadata": {"type": "roadmap", "career_id": career_id, "title": f"{career['title']} Roadmap"},
            })

        # PART 2: SKILLS
        print("  → Indexing skills...")
        logger.info("  → Indexing skills...")

        for skill_id, skill in SKILLS_DATABASE.items():
            doc = f"""Skill: {skill['name']}
                Category: {skill['category']}
                Difficulty: {skill.get('difficulty', 'N/A')}
                Time to Learn: {skill.get('time_to_learn', 'N/A')}
                Description: {skill['description']}
                Use Cases: {', '.join(skill.get('use_cases', []))}
                Related Careers: {', '.join(skill.get('related_careers', []))}
                YouTube Channels: {', '.join(skill.get('youtube_channels', [])[:5])}
                Practice Platforms: {', '.join(skill.get('practice_platforms', []))}
            """
            for resource in skill.get('free_resources', [])[:3]:
                doc += f"\nFree Resource: {resource['title']} - {resource['url']}"
            if skill.get('prerequisites'):
                doc += f"\nPrerequisites: {', '.join(skill['prerequisites'])}"
            documents.append({
                "content": doc,
                "metadata": {"type": "skill", "skill_id": skill_id, "title": skill['name'],
                             "category": skill['category'], "difficulty": skill.get('difficulty', 'N/A')},
            })

        # PART 3: LEARNING PLATFORMS
        print("  → Indexing platforms...")
        logger.info("  → Indexing platforms...")

        for category, platforms in LEARNING_PLATFORMS.items():
            for i, platform in enumerate(platforms):
                doc = f"""Learning Platform: {platform['name']}
                    URL: {platform['url']}
                    Type: {platform['type']}
                    Category: {category}
                    Best For: {', '.join(platform['best_for'])}
                    Price: {platform.get('price_range', 'Free')}
                    Description: {platform['description']}
                """
                documents.append({
                    "content": doc,
                    "metadata": {"type": "platform", "category": category, "title": platform['name']},
                })

        # PART 4: YOUTUBE CHANNELS
        print("  → Indexing YouTube channels...")
        logger.info("  → Indexing YouTube channels...")

        for category, channels in YOUTUBE_CHANNELS.items():
            for i, channel in enumerate(channels):
                doc = f"""YouTube Channel: {channel['name']}
                    URL: {channel['url']}
                    Subscribers: {channel.get('subscribers', 'N/A')}
                    Language: {channel.get('language', 'English')}
                    Best For: {channel['best_for']}
                    Category: {category}
                """
                documents.append({
                    "content": doc,
                    "metadata": {"type": "youtube", "category": category, "title": channel['name'],
                                 "language": channel.get('language', 'English')},
                })

        # PART 5: INTERVIEW RESOURCES
        print("  → Indexing interview resources...")
        logger.info("  → Indexing interview resources...")

        for category, resources in INTERVIEW_RESOURCES.items():
            for i, resource in enumerate(resources):
                doc = f"""Interview Resource: {resource['title']}
                    URL: {resource['url']}
                    Category: {category}
                    Description: {resource['description']}"""
                documents.append({
                    "content": doc,
                    "metadata": {"type": "interview", "category": category, "title": resource['title']},
                })

        # PART 6: COMMUNITIES
        print("  → Indexing communities...")
        logger.info("  → Indexing communities...")

        for i, community in enumerate(COMMUNITIES):
            doc = f"""Community: {community['name']}
                URL: {community['url']}
                Platform: {community['platform']}
                Description: {community['description']}
    """
            documents.append({
                "content": doc,
                "metadata": {"type": "community", "platform": community['platform'], "title": community['name']},
            })

        print(f"  → Indexed {len(documents)} documents (keyword search, no ChromaDB)...")
        logger.info("  → Indexed %s documents (keyword search, no ChromaDB)...", len(documents))

        # Precompute token sets for fast deterministic ranking.
        for d in documents:
            d["tokens"] = _tokens(d["content"] + " " + str(d["metadata"].get("title", "")))

        self._documents = documents
        self._initialized = True
        print(f"✅ Successfully indexed {len(documents)} documents!")
        logger.info("✅ Successfully indexed %s documents!", len(documents))

    def query(self, query_text, n_results=None, filter_type=None):
        """Query the store with keyword overlap ranking.

        Args:
            query_text: What to search for
            n_results: How many results (default from Config)
            filter_type: Filter by metadata type
        """
        if not self._initialized:
            self.initialize()

        if n_results is None:
            try:
                n_results = Config.MAX_SEARCH_RESULTS
            except Exception:
                n_results = 5

        qtokens = _tokens(query_text or "")
        scored = []
        for d in self._documents:
            if filter_type and d["metadata"].get("type") != filter_type:
                continue
            s = _score(qtokens, d["tokens"])
            if s > 0:
                scored.append((s, d))
        scored.sort(key=lambda x: x[0], reverse=True)

        formatted = []
        for score, d in scored[: max(1, int(n_results or 5))]:
            formatted.append({
                "content": d["content"],
                "metadata": d["metadata"],
                "distance": round(1.0 - min(1.0, score), 4),
                "score": round(score, 4),
            })
        return formatted

    def get_relevant_context(self, query, n_results=None):
        """Get relevant context for LLM from the knowledge base."""
        results = self.query(query, n_results=n_results)

        if not results:
            return "No relevant information found in knowledge base."

        context_parts = [r["content"] for r in results]
        return "\n\n---\n\n".join(context_parts)


# Backwards-compat alias (old code imported KnowledgeStore-like names in places).
KnowledgeStore = EmbeddingsStore

# --- Add this at the very bottom of embeddings_store.py ---
if __name__ == "__main__":
    print("🚀 Initializing keyword knowledge store test...")
    logger.info("🚀 Initializing keyword knowledge store test...")
    store = EmbeddingsStore()
    store.initialize()

    # Test a quick search query to see output
    results = store.query("Python Developer", n_results=2)
    print("\n🔍 Sample Search Results:")
    logger.info("\n🔍 Sample Search Results:")
    for res in results:
        print(f"- Title: {res['metadata'].get('title')}")
        logger.info("- Title: %s", res['metadata'].get('title'))
        print(f"  Content preview: {res['content'][:100]}...\n")
        logger.info("  Content preview: %s...\n", res['content'][:100])
