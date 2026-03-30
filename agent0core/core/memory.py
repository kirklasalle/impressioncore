"""
Agent0Core - Memory System

Created: January 13, 2026
Author: ImpressionCore Team

Persistent memory system using VectorDB for Agent0Core.
Stores conversation fragments, solutions, and learned patterns.
"""

import hashlib
import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger("agent0core.memory")


@dataclass
class MemoryFragment:
    """A single memory fragment stored in the system."""

    id: str
    content: str
    type: str  # "conversation", "solution", "fact", "instruction"
    agent_id: int
    timestamp: str
    metadata: dict[str, Any] = field(default_factory=dict)
    embedding: list[float] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for storage."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MemoryFragment":
        """Create from dictionary."""
        return cls(**data)


class MemoryManager:
    """
    Manages persistent memory for Agent0Core agents.

    Features:
    - Fragment-based storage
    - Solution memorization
    - Cross-session persistence
    - Integration with ImpressionCore's vector index
    """

    def __init__(
        self,
        agent_id: int = 0,
        storage_path: Path | None = None,
    ):
        """
        Initialize the memory manager.

        Args:
            agent_id: ID of the agent this memory belongs to
            storage_path: Path for persistent storage
        """
        self.agent_id = agent_id

        # Set storage path
        if storage_path:
            self.storage_path = Path(storage_path)
        else:
            self.storage_path = (
                Path(__file__).parent.parent / "memory" / f"agent_{agent_id}"
            )

        # Ensure storage directory exists
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # In-memory cache
        self._fragments: dict[str, MemoryFragment] = {}

        # Load existing memories
        self._load_memories()

        logger.info(f"MemoryManager initialized for agent {agent_id} at {self.storage_path}")

    def _generate_id(self, content: str) -> str:
        """Generate a unique ID for a memory fragment."""
        hash_input = f"{content}:{datetime.now().isoformat()}:{self.agent_id}"
        return hashlib.sha256(hash_input.encode()).hexdigest()[:16]

    def _load_memories(self):
        """Load memories from persistent storage."""
        fragments_file = self.storage_path / "fragments.json"

        if fragments_file.exists():
            try:
                with open(fragments_file, encoding="utf-8") as f:
                    data = json.load(f)
                    for item in data:
                        fragment = MemoryFragment.from_dict(item)
                        self._fragments[fragment.id] = fragment
                logger.info(f"Loaded {len(self._fragments)} memory fragments")
            except Exception as e:
                logger.error(f"Failed to load memories: {e}")

    def _save_memories(self):
        """Save memories to persistent storage."""
        fragments_file = self.storage_path / "fragments.json"

        try:
            data = [f.to_dict() for f in self._fragments.values()]
            with open(fragments_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save memories: {e}")

    def store(
        self,
        content: str,
        memory_type: str = "fact",
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """
        Store a new memory fragment.

        Args:
            content: The content to store
            memory_type: Type of memory (conversation, solution, fact, instruction)
            metadata: Additional metadata

        Returns:
            ID of the stored fragment
        """
        fragment = MemoryFragment(
            id=self._generate_id(content),
            content=content,
            type=memory_type,
            agent_id=self.agent_id,
            timestamp=datetime.now().isoformat(),
            metadata=metadata or {},
        )

        # [INTEGRATION] Intelligence Nexus Phase - Sync with Vector DB
        try:
            from agent0core.integrations.impressioncore import get_vector_provider
            provider = get_vector_provider()
            if provider is not None:
                provider.add_memory(
                    text=content,
                    metadata={
                        "fragment_id": fragment.id,
                        "type": memory_type,
                        "agent_id": self.agent_id,
                        "device_id": "SYSTEM"
                    }
                )
        except Exception as e:
            logger.warning(f"Failed to sync memory to vector DB: {e}")

        self._fragments[fragment.id] = fragment
        self._save_memories()

        logger.debug(f"Stored memory fragment {fragment.id}: {content[:50]}...")
        return fragment.id

    async def recall(
        self,
        query: str,
        memory_type: str | None = None,
        limit: int = 10,
    ) -> list[MemoryFragment]:
        """
        Recall memories relevant to a query using semantic search.
        """
        # [INTEGRATION] Intelligence Nexus Phase
        try:
            from agent0core.integrations.impressioncore import get_vector_provider
            provider = get_vector_provider()
            if provider is None:
                raise RuntimeError("VectorMemoryProvider not registered")

            # Use the provider's search method for true semantic recall
            search_results = provider.search(
                query=query,
                top_k=limit
            )


            # Map search results back to fragments if possible, or create temporary ones
            results = []
            for r in search_results:
                meta = r.get("metadata", {})
                frag_id = meta.get("fragment_id")
                if frag_id in self._fragments:
                    results.append(self._fragments[frag_id])
                else:
                    # Fallback to creating a fragment from search text if ID doesn't match
                    text = meta.get("text", "")
                    results.append(MemoryFragment(
                        id=f"vector_{hash(text) % 10000}",
                        content=text,
                        type=meta.get("type", "fact"),
                        agent_id=meta.get("agent_id", 0),
                        timestamp=meta.get("timestamp", datetime.now().isoformat()),
                        metadata=meta
                    ))

            if results:
                return results

            # Lexical Fallback (Keyword-based)
            query_parts = query.lower().split()
            results = []
            for f in self._fragments.values():
                content_lower = f.content.lower()
                if all(part in content_lower for part in query_parts):
                    results.append(f)

            results.sort(key=lambda f: f.timestamp, reverse=True)
            return results[:limit]

        except Exception as e:
            logger.warning(f"Semantic recall error: {e}. Using lexical fallback.")
            # Advanced Lexical Fallback (Keyword-based)
            query_parts = query.lower().split()
            results = []
            for f in self._fragments.values():
                content_lower = f.content.lower()
                # If all words match (in any order) or the full query is partially present
                if all(part in content_lower for part in query_parts):
                    results.append(f)

            # Sort by timestamp (most recent first)
            results.sort(key=lambda f: f.timestamp, reverse=True)
            return results[:limit]

    def store_solution(
        self,
        problem: str,
        solution: str,
        success: bool = True,
    ) -> str:
        """
        Store a problem-solution pair for future reference.

        Args:
            problem: Description of the problem
            solution: The solution that was applied
            success: Whether the solution was successful

        Returns:
            ID of the stored solution
        """
        content = f"PROBLEM: {problem}\nSOLUTION: {solution}"
        return self.store(
            content,
            memory_type="solution",
            metadata={"problem": problem, "success": success},
        )

    def delete(self, fragment_id: str) -> bool:
        """
        Delete a memory fragment.

        Args:
            fragment_id: ID of the fragment to delete

        Returns:
            True if deleted, False if not found
        """
        if fragment_id in self._fragments:
            del self._fragments[fragment_id]
            self._save_memories()
            logger.debug(f"Deleted memory fragment {fragment_id}")
            return True
        return False

    def clear(self, memory_type: str | None = None):
        """
        Clear memories.

        Args:
            memory_type: If specified, only clear this type. Otherwise clear all.
        """
        if memory_type:
            self._fragments = {
                k: v for k, v in self._fragments.items()
                if v.type != memory_type
            }
        else:
            self._fragments = {}

        self._save_memories()
        logger.info(f"Cleared {memory_type if memory_type else 'all'} memories")

    def get_stats(self) -> dict[str, Any]:
        """Get memory statistics."""
        type_counts = {}
        for fragment in self._fragments.values():
            type_counts[fragment.type] = type_counts.get(fragment.type, 0) + 1

        return {
            "total_fragments": len(self._fragments),
            "by_type": type_counts,
            "storage_path": str(self.storage_path),
        }
