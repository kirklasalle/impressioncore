"""
RLM Context Manager - External Context Storage for NEXUS-RLM Integration

Created: January 19, 2026
Author: ImpressionCore Team
Tags: #rlm #nexus #context_management #recursive_language_model
Category: Core Infrastructure
Status: Active

This module provides external context storage and manipulation for RLM-style
operations within the NEXUS language. It enables ImpressionCore's Brain-Triad
to handle arbitrarily large contexts by storing them externally and providing
programmatic access via NEXUS commands.

Key Features:
- External context storage (not GPU-bound)
- Regex and keyword search
- Chunking and slicing
- Context statistics
- Recursion tracking
"""

import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


@dataclass
class RLMContext:
    """Represents a loaded context for RLM operations."""
    content: str
    source_path: str | None = None
    loaded_at: str = field(default_factory=lambda: datetime.now().isoformat())
    token_count_estimate: int = 0

    def __post_init__(self):
        # Estimate token count (~4 chars per token)
        self.token_count_estimate = len(self.content) // 4


@dataclass
class RecursionState:
    """Tracks recursion depth and history for RLM operations."""
    current_depth: int = 0
    max_depth: int = 20  # Prevent infinite recursion
    call_history: list[dict[str, Any]] = field(default_factory=list)

    def push_call(self, target: str, prompt_preview: str):
        """Record a new recursive call."""
        self.current_depth += 1
        self.call_history.append({
            "depth": self.current_depth,
            "target": target,
            "prompt_preview": prompt_preview[:100],
            "timestamp": datetime.now().isoformat()
        })

    def pop_call(self):
        """Return from a recursive call."""
        if self.current_depth > 0:
            self.current_depth -= 1

    def can_recurse(self) -> bool:
        """Check if we can make another recursive call."""
        return self.current_depth < self.max_depth


class RLMContextManager:
    """
    Singleton manager for RLM context operations.

    Provides:
    - Context loading from files or strings
    - Context search (regex, keyword)
    - Context chunking
    - Recursion tracking
    - Statistics and monitoring
    """

    _instance: Optional['RLMContextManager'] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        # Context storage
        self.contexts: dict[str, RLMContext] = {}
        self.active_context_id: str | None = None

        # Recursion state
        self.recursion_state = RecursionState()

        # Configuration
        self.max_context_size = 50 * 1024 * 1024  # 50MB max per context
        self.default_chunk_size = 4096  # tokens (approx)

        # Statistics
        self.stats = {
            "contexts_loaded": 0,
            "total_searches": 0,
            "total_chunks_created": 0,
            "total_llm_queries": 0
        }

        self._initialized = True

    # ===================================================================
    # Context Loading
    # ===================================================================

    def load_context_from_file(self, file_path: str, context_id: str | None = None) -> tuple[bool, str]:
        """
        Load context from a file path.

        Args:
            file_path: Path to the file to load
            context_id: Optional ID for the context (defaults to filename)

        Returns:
            (success, message)
        """
        path = Path(file_path)

        if not path.exists():
            return False, f"File not found: {file_path}"

        if path.stat().st_size > self.max_context_size:
            return False, f"File too large: {path.stat().st_size} bytes (max: {self.max_context_size})"

        try:
            with open(path, encoding="utf-8", errors="replace") as f:
                content = f.read()

            cid = context_id or path.stem
            self.contexts[cid] = RLMContext(
                content=content,
                source_path=str(path.absolute())
            )
            self.active_context_id = cid
            self.stats["contexts_loaded"] += 1

            return True, f"Loaded {len(content):,} chars as context '{cid}'"

        except Exception as e:
            return False, f"Error loading file: {e}"

    def load_context_from_string(self, content: str, context_id: str) -> tuple[bool, str]:
        """Load context directly from a string."""
        if len(content) > self.max_context_size:
            return False, f"Content too large: {len(content)} bytes"

        self.contexts[context_id] = RLMContext(content=content)
        self.active_context_id = context_id
        self.stats["contexts_loaded"] += 1

        return True, f"Loaded {len(content):,} chars as context '{context_id}'"

    def get_active_context(self) -> str | None:
        """Get the content of the currently active context."""
        if self.active_context_id and self.active_context_id in self.contexts:
            return self.contexts[self.active_context_id].content
        return None

    def set_active_context(self, context_id: str) -> bool:
        """Set the active context by ID."""
        if context_id in self.contexts:
            self.active_context_id = context_id
            return True
        return False

    # ===================================================================
    # Context Search
    # ===================================================================

    def search_context(
        self,
        pattern: str,
        is_regex: bool = False,
        context_id: str | None = None,
        max_results: int = 10,
        context_lines: int = 2
    ) -> list[dict[str, Any]]:
        """
        Search the context for a pattern.

        Args:
            pattern: Search pattern (string or regex)
            is_regex: Whether pattern is a regex
            context_id: Context to search (default: active)
            max_results: Maximum number of matches to return
            context_lines: Number of lines of context around each match

        Returns:
            List of match dictionaries with position and context
        """
        cid = context_id or self.active_context_id
        if not cid or cid not in self.contexts:
            return []

        content = self.contexts[cid].content
        self.stats["total_searches"] += 1

        results = []

        if is_regex:
            try:
                regex = re.compile(pattern, re.IGNORECASE | re.MULTILINE)
                for match in regex.finditer(content):
                    if len(results) >= max_results:
                        break

                    # Get surrounding context
                    start_pos = max(0, match.start() - 200)
                    end_pos = min(len(content), match.end() + 200)

                    results.append({
                        "match": match.group(),
                        "start": match.start(),
                        "end": match.end(),
                        "context": content[start_pos:end_pos]
                    })
            except re.error as e:
                return [{"error": f"Invalid regex: {e}"}]
        else:
            # Simple keyword search
            pattern_lower = pattern.lower()
            content_lower = content.lower()

            pos = 0
            while len(results) < max_results:
                idx = content_lower.find(pattern_lower, pos)
                if idx == -1:
                    break

                start_pos = max(0, idx - 200)
                end_pos = min(len(content), idx + len(pattern) + 200)

                results.append({
                    "match": content[idx:idx + len(pattern)],
                    "start": idx,
                    "end": idx + len(pattern),
                    "context": content[start_pos:end_pos]
                })

                pos = idx + 1

        return results

    # ===================================================================
    # Context Chunking
    # ===================================================================

    def chunk_context(
        self,
        chunk_size: int | None = None,
        overlap: int = 100,
        context_id: str | None = None,
        by: str = "chars"  # "chars", "lines", "paragraphs"
    ) -> list[str]:
        """
        Split context into chunks for processing.

        Args:
            chunk_size: Size of each chunk (defaults to self.default_chunk_size * 4)
            overlap: Number of chars/lines to overlap between chunks
            context_id: Context to chunk (default: active)
            by: Chunking method - "chars", "lines", or "paragraphs"

        Returns:
            List of chunk strings
        """
        cid = context_id or self.active_context_id
        if not cid or cid not in self.contexts:
            return []

        content = self.contexts[cid].content
        chunk_size = chunk_size or (self.default_chunk_size * 4)  # ~16k chars

        chunks = []

        if by == "paragraphs":
            # Split by double newlines
            paragraphs = re.split(r'\n\n+', content)
            current_chunk = []
            current_size = 0

            for para in paragraphs:
                if current_size + len(para) > chunk_size and current_chunk:
                    chunks.append("\n\n".join(current_chunk))
                    # Keep last paragraph for overlap
                    current_chunk = [current_chunk[-1]] if overlap > 0 else []
                    current_size = len(current_chunk[0]) if current_chunk else 0

                current_chunk.append(para)
                current_size += len(para)

            if current_chunk:
                chunks.append("\n\n".join(current_chunk))

        elif by == "lines":
            lines = content.split("\n")
            line_chunk_size = chunk_size // 80  # Assume ~80 chars per line

            for i in range(0, len(lines), line_chunk_size - overlap):
                chunk_lines = lines[i:i + line_chunk_size]
                chunks.append("\n".join(chunk_lines))

        else:  # by == "chars"
            step = chunk_size - overlap
            for i in range(0, len(content), step):
                chunks.append(content[i:i + chunk_size])

        self.stats["total_chunks_created"] += len(chunks)
        return chunks

    def get_chunk(
        self,
        start: int,
        end: int,
        context_id: str | None = None
    ) -> str:
        """Get a specific slice of the context."""
        cid = context_id or self.active_context_id
        if not cid or cid not in self.contexts:
            return ""

        content = self.contexts[cid].content
        return content[start:end]

    # ===================================================================
    # Context Statistics
    # ===================================================================

    def get_context_stats(self, context_id: str | None = None) -> dict[str, Any]:
        """Get statistics about a context."""
        cid = context_id or self.active_context_id
        if not cid or cid not in self.contexts:
            return {"error": "No context loaded"}

        ctx = self.contexts[cid]
        content = ctx.content

        return {
            "context_id": cid,
            "source_path": ctx.source_path,
            "loaded_at": ctx.loaded_at,
            "char_count": len(content),
            "token_estimate": ctx.token_count_estimate,
            "line_count": content.count("\n") + 1,
            "paragraph_count": len(re.split(r'\n\n+', content)),
            "word_count": len(content.split())
        }

    # ===================================================================
    # Recursion Management
    # ===================================================================

    def begin_recursive_call(self, target: str, prompt: str) -> tuple[bool, str]:
        """Begin a recursive LLM call, checking depth limits."""
        if not self.recursion_state.can_recurse():
            return False, f"Max recursion depth ({self.recursion_state.max_depth}) exceeded"

        self.recursion_state.push_call(target, prompt)
        self.stats["total_llm_queries"] += 1
        return True, f"Recursion depth: {self.recursion_state.current_depth}"

    def end_recursive_call(self):
        """End a recursive call."""
        self.recursion_state.pop_call()

    def get_recursion_depth(self) -> int:
        """Get current recursion depth."""
        return self.recursion_state.current_depth

    def get_call_history(self) -> list[dict[str, Any]]:
        """Get the history of recursive calls."""
        return self.recursion_state.call_history.copy()

    def reset_recursion(self):
        """Reset recursion state for a new query."""
        self.recursion_state = RecursionState()

    # ===================================================================
    # Utility
    # ===================================================================

    def get_global_stats(self) -> dict[str, Any]:
        """Get global RLM statistics."""
        return {
            **self.stats,
            "active_context": self.active_context_id,
            "loaded_contexts": list(self.contexts.keys()),
            "current_recursion_depth": self.recursion_state.current_depth
        }

    def clear_all_contexts(self):
        """Clear all loaded contexts."""
        self.contexts.clear()
        self.active_context_id = None

    def list_contexts(self) -> list[dict[str, Any]]:
        """List all loaded contexts with summary info."""
        return [
            {
                "id": cid,
                "chars": len(ctx.content),
                "tokens_est": ctx.token_count_estimate,
                "source": ctx.source_path,
                "active": cid == self.active_context_id
            }
            for cid, ctx in self.contexts.items()
        ]


# Singleton accessor
def get_rlm_context_manager() -> RLMContextManager:
    """Get the singleton RLM context manager instance."""
    return RLMContextManager()
