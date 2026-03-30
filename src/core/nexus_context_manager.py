import logging
from typing import Any

logger = logging.getLogger("NEXUS.ContextManager")

class NexusContextManager:
    """
    Manages global context state for the NEXUS RLM system.
    Tracks statistics, recursion depth, and active context chunks.
    """

    def __init__(self):
        self.stats = {
            "total_chars": 0,
            "total_tokens_estimate": 0,
            "contexts_loaded": 0,
            "current_recursion_depth": 0,
            "total_searches": 0,
            "total_llm_queries": 0
        }
        self.active_context = ""

    def update_stats(self, key: str, increment: int = 1):
        if key in self.stats:
            self.stats[key] += increment

    def set_active_context(self, text: str):
        self.active_context = text
        self.stats["total_chars"] = len(text)
        self.stats["total_tokens_estimate"] = len(text) // 4
        self.stats["contexts_loaded"] += 1

    def get_global_stats(self) -> dict[str, Any]:
        return self.stats.copy()

    def get_active_context(self) -> str:
        return self.active_context

if __name__ == "__main__":
    cm = NexusContextManager()
    cm.set_active_context("Hello world")
    logger.info("Global stats: %s", cm.get_global_stats())
