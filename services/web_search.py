"""Web search module – Generates multiple clickable search links (No scraping)"""

from urllib.parse import quote


class WebSearcher:

    def __init__(self):
        pass

    def google_search(self, query, num_results=5):
        """Single query -> multiple useful Google search links"""
        variations = [
            query,
            f"{query} roadmap",
            f"{query} beginner guide",
            f"{query} free resources",
            f"{query} best websites",
            f"{query} projects",
            f"{query} practice questions",
        ]

        # duplicates remove karke limit laga do
        seen = set()
        final_queries = []
        for q in variations:
            if q.lower() not in seen:
                seen.add(q.lower())
                final_queries.append(q)

        final_queries = final_queries[:num_results]

        results = []
        for q in final_queries:
            results.append({
                "title": f"🔍 Search Google: {q}",
                "url": f"https://www.google.com/search?q={quote(q)}",
                "snippet": f"Click to see latest results for '{q}'",
                "source": "Web",
            })

        return results

    def youtube_search(self, query, num_results=5):
        """Single query -> multiple useful YouTube search links"""
        variations = [
            f"{query} tutorial",
            f"{query} full course",
            f"{query} beginners",
            f"{query} playlist",
            f"{query} projects",
            f"{query} crash course",
            f"{query} explained",
        ]

        seen = set()
        final_queries = []
        for q in variations:
            if q.lower() not in seen:
                seen.add(q.lower())
                final_queries.append(q)

        final_queries = final_queries[:num_results]

        results = []
        for q in final_queries:
            results.append({
                "title": f"📺 Search YouTube: {q}",
                "url": f"https://www.youtube.com/results?search_query={quote(q)}",
                "channel": "YouTube",
                "source": "YouTube",
            })

        return results

    def search_career_resources(self, query):
        """Frontend se 1 query aayegi, backend multiple links dega"""
        try:
            web_results = self.google_search(query, num_results=5)
            yt_results = self.youtube_search(query, num_results=5)

            return {
                "web": web_results,
                "youtube": yt_results
            }
        except Exception as e:
            print(f"Search error: {e}")
            return {"web": [], "youtube": []}


if __name__ == "__main__":
    ws = WebSearcher()
    result = ws.search_career_resources("free resources to learn Python")

    print("=== WEB ===")
    for r in result["web"]:
        print(f"- {r['title']}\n  {r['url']}\n")

    print("=== YOUTUBE ===")
    for r in result["youtube"]:
        print(f"- {r['title']}\n  {r['url']}\n")
