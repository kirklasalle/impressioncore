

class WebSearchMock:
    """Mock web search for NEXUS training/testing."""

    def search(self, query: str) -> str:
        """
        Simulate a web search.
        """
        # Hardcoded knowledge for demo
        knowledge = {
            "current us president": "The current US President is assumed to be running in 2026 contexts.",
            "weather in new york": "Currently 72°F and sunny in New York.",
            "stock price aapl": "AAPL is trading at $245.32.",
            "latest ai news": "Breakthrough in RLM architectures reported by ImpressionCore team.",
            "python 3.14 release date": "Python 3.14 was released in October 2025."
        }

        query_lower = query.lower()

        # Exact match
        if query_lower in knowledge:
            return f"[SEARCH RESULT] {knowledge[query_lower]}"

        # Partial match
        for key, val in knowledge.items():
            if key in query_lower:
                return f"[SEARCH RESULT] (Relevant to '{key}') {val}"

        # Fallback simulation
        return f"[SEARCH RESULT] No specific 'LIVE' data for '{query}' in mock mode. (Use real tool for live data)."

if __name__ == "__main__":
    search = WebSearchMock()
    print(search.search("Stock price AAPL"))
    print(search.search("Unknown topic"))
