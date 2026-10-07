"""ChromaDB-based RAG embeddings store for career knowledge."""
import logging
import os
import sys

logger = logging.getLogger(__name__)

# Add the parent directory (NEW_RESUME_ANALYSER_BACKEND) to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import chromadb
from config import Config
# ===========================================
# IMPORTS (Apne folder structure ke hisaab se adjust karein)
# ===========================================
from database.career_database.career_data import CAREER_PATHS
from database.skills_database.skills_data import SKILLS_DATABASE
from database.resources_database.resources_data import (
    LEARNING_PLATFORMS,
    YOUTUBE_CHANNELS,
    INTERVIEW_RESOURCES,
    COMMUNITIES
)


class EmbeddingsStore:
    """Vector store for career knowledge using ChromaDB."""
    def __init__(self):
        """Initialize ChromaDB client using Config settings."""
        
        # Config se path lo
        persist_dir = Config.CHROMA_PERSIST_DIR
        
        # Folder create karo
        os.makedirs(persist_dir, exist_ok=True)
        
        # Persistent client
        self.client = chromadb.PersistentClient(path=persist_dir)
        
        # Collection
        self.collection = self.client.get_or_create_collection(
            name="career_knowledge",
            metadata={"description": "Career guidance knowledge base"}
        )
        
        self._initialized = False
        
        print(f"📁 ChromaDB Path: {persist_dir}")
        logger.info("📁 ChromaDB Path: %s", persist_dir)

    def initialize(self):
        """Build embeddings from knowledge base data."""
        
        if self.collection.count() > 0:
            print(f"✅ Already initialized ({self.collection.count()} documents)")
            logger.info("✅ Already initialized (%s documents)", self.collection.count())
            self._initialized = True
            return

        print("📚 Building embeddings store...")
        logger.info("📚 Building embeddings store...")

        documents = []
        metadatas = []
        ids = []

        # ============================================
        # PART 1: CAREER PATHS
        # ============================================
        print("  → Indexing careers...")
        logger.info("  → Indexing careers...")
        
        for career_id, career in CAREER_PATHS.items():
            # doubt that (agar interviewer ne pucha ki doc banana kaise sikha then??)
            # Main career document
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

            documents.append(doc)

            #doubt(variables ka issue what are metadata kaise pata ki hai meta hai ya nahi)
            metadatas.append({
                "type": "career",
                "career_id": career_id,
                "title": career['title'],
                "category": career['category'],
                "difficulty": career.get('difficulty', 'N/A')
            })
            ids.append(f"career_{career_id}")

            # Skills doc
            skills_doc = f"Skills needed for {career['title']}:\n"
            for skill_cat, skills in career.get('required_skills', {}).items():
                skills_doc += f"  {skill_cat}: {', '.join(skills)}\n"

            documents.append(skills_doc)
            metadatas.append({
                "type": "career_skills",
                "career_id": career_id,
                "title": f"{career['title']} Skills"
            })
            ids.append(f"skills_{career_id}")

            # Roadmap doc
            roadmap_doc = f"Learning Roadmap for {career['title']}:\n"
            for phase in career.get('roadmap', []):
                roadmap_doc += f"\n{phase['phase']}:\n"
                for task in phase['tasks']:
                    roadmap_doc += f"  - {task}\n"

            documents.append(roadmap_doc)
            metadatas.append({
                "type": "roadmap",
                "career_id": career_id,
                "title": f"{career['title']} Roadmap"
            })
            ids.append(f"roadmap_{career_id}")
        
        
        # ============================================
        # PART 2: SKILLS
        # ============================================
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

            documents.append(doc)
            metadatas.append({
                "type": "skill",
                "skill_id": skill_id,
                "title": skill['name'],
                "category": skill['category'],
                "difficulty": skill.get('difficulty', 'N/A')
            })
            ids.append(f"skill_{skill_id}")
        
        
        # ============================================
        # PART 3: LEARNING PLATFORMS
        # ============================================
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

                documents.append(doc)
                metadatas.append({
                    "type": "platform",
                    "category": category,
                    "title": platform['name']
                })
                ids.append(f"platform_{category}_{i}")
        
        
        # ============================================
        # PART 4: YOUTUBE CHANNELS
        # ============================================
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

                documents.append(doc)
                metadatas.append({
                    "type": "youtube",
                    "category": category,
                    "title": channel['name'],
                    "language": channel.get('language', 'English')
                })
                ids.append(f"youtube_{category}_{i}")
        
        
        # ============================================
        # PART 5: INTERVIEW RESOURCES
        # ============================================
        print("  → Indexing interview resources...")
        logger.info("  → Indexing interview resources...")
        
        for category, resources in INTERVIEW_RESOURCES.items():
            for i, resource in enumerate(resources):
                doc = f"""Interview Resource: {resource['title']}
                    URL: {resource['url']}
                    Category: {category}
                    Description: {resource['description']}"""

                documents.append(doc)
                metadatas.append({
                    "type": "interview",
                    "category": category,
                    "title": resource['title']
                })
                ids.append(f"interview_{category}_{i}")
        
        
        # ============================================
        # PART 6: COMMUNITIES
        # ============================================
        print("  → Indexing communities...")
        logger.info("  → Indexing communities...")
        
        for i, community in enumerate(COMMUNITIES):
            doc = f"""Community: {community['name']}
                URL: {community['url']}
                Platform: {community['platform']}
                Description: {community['description']}
    """

            documents.append(doc)
            metadatas.append({
                "type": "community",
                "platform": community['platform'],
                "title": community['name']
            })
            ids.append(f"community_{i}")
        
        
        # ============================================
        # BATCH ADD
        # ============================================
        print(f"  → Adding {len(documents)} documents to ChromaDB...")
        logger.info("  → Adding %s documents to ChromaDB...", len(documents))
        
        batch_size = 100
        for i in range(0, len(documents), batch_size):
            end = min(i + batch_size, len(documents))
            self.collection.add(
                documents=documents[i:end],
                metadatas=metadatas[i:end],
                ids=ids[i:end]
            )

        self._initialized = True
        print(f"✅ Successfully indexed {len(documents)} documents!")
        logger.info("✅ Successfully indexed %s documents!", len(documents))

    def query(self, query_text, n_results=None, filter_type=None):
        """Query the embeddings store.
        
        Args:
            query_text: What to search for
            n_results: How many results (default from Config)
            filter_type: Filter by type
        """
        if not self._initialized:
            self.initialize()
        
        # Default from config
        if n_results is None:
            n_results = Config.MAX_SEARCH_RESULTS

        where_filter = None
        if filter_type:
            where_filter = {"type": filter_type}

        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results,
            where=where_filter
        )

        formatted_results = []
        if results and results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                formatted_results.append({
                    "content": doc,
                    "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                    "distance": results['distances'][0][i] if results['distances'] else 0
                })

        return formatted_results

    def get_relevant_context(self, query, n_results=None):
        """Get relevant context for LLM from the knowledge base."""
        results = self.query(query, n_results=n_results)
        
        if not results:
            return "No relevant information found in knowledge base."
        
        context_parts = [r["content"] for r in results]
        return "\n\n---\n\n".join(context_parts)

# --- Add this at the very bottom of embeddings_store.py ---
if __name__ == "__main__":
    print("🚀 Initializing EmbeddingsStore test...")
    logger.info("🚀 Initializing EmbeddingsStore test...")
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