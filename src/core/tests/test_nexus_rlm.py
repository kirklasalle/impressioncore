"""
Unit Tests for NEXUS-RLM Commands

Created: January 20, 2026
Author: ImpressionCore Team
Tags: #testing #rlm #nexus #unit_tests

Tests cover:
- RLM Context Manager functionality
- NEXUS-RLM commands (LLM-QUERY, CONTEXT-*, RLM-STATS, etc.)
- Recursion depth tracking
- Error handling
"""

import os
import sys
import tempfile
from pathlib import Path

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.orchestrator.nexus_interpreter import NexusInterpreter
from src.orchestrator.rlm_context_manager import RecursionState, RLMContext, get_rlm_context_manager


class TestRLMContextManager:
    """Tests for the RLM Context Manager singleton."""

    def setup_method(self):
        """Reset singleton state before each test."""
        # Get fresh manager and clear state
        self.rlm = get_rlm_context_manager()
        self.rlm.clear_all_contexts()
        self.rlm.reset_recursion()

    def test_singleton_pattern(self):
        """Verify singleton pattern works correctly."""
        rlm1 = get_rlm_context_manager()
        rlm2 = get_rlm_context_manager()
        assert rlm1 is rlm2, "Should return same instance"

    def test_load_context_from_string(self):
        """Test loading context from string."""
        success, msg = self.rlm.load_context_from_string(
            "Hello World! This is test content.",
            "test_context"
        )
        assert success, f"Failed to load: {msg}"
        assert "test_context" in msg
        assert self.rlm.active_context_id == "test_context"

    def test_load_context_from_file(self):
        """Test loading context from file."""
        # Create temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Test file content for RLM.\nLine 2.\nLine 3.")
            temp_path = f.name

        try:
            success, msg = self.rlm.load_context_from_file(temp_path, "file_context")
            assert success, f"Failed to load file: {msg}"
            assert self.rlm.active_context_id == "file_context"

            content = self.rlm.get_active_context()
            assert "Test file content" in content
        finally:
            os.unlink(temp_path)

    def test_load_nonexistent_file(self):
        """Test loading from nonexistent file fails gracefully."""
        success, msg = self.rlm.load_context_from_file("/nonexistent/path.txt")
        assert not success
        assert "not found" in msg.lower()

    def test_context_search_keyword(self):
        """Test keyword search in context."""
        self.rlm.load_context_from_string(
            "The quick brown fox jumps over the lazy dog. The fox is clever.",
            "search_test"
        )

        results = self.rlm.search_context("fox")
        assert len(results) == 2, "Should find 'fox' twice"
        assert all("fox" in r["match"].lower() for r in results)

    def test_context_search_regex(self):
        """Test regex search in context."""
        self.rlm.load_context_from_string(
            "def foo(): pass\ndef bar(): pass\ndef baz(): pass",
            "regex_test"
        )

        results = self.rlm.search_context(r"def \w+\(\)", is_regex=True)
        assert len(results) == 3, "Should find 3 function definitions"

    def test_context_chunking_chars(self):
        """Test chunking by characters."""
        content = "A" * 1000  # 1000 character content
        self.rlm.load_context_from_string(content, "chunk_test")

        chunks = self.rlm.chunk_context(chunk_size=200, overlap=0)
        assert len(chunks) == 5, "Should create 5 chunks of 200 chars"

    def test_context_chunking_paragraphs(self):
        """Test chunking by paragraphs."""
        content = "Para 1.\n\nPara 2.\n\nPara 3.\n\nPara 4."
        self.rlm.load_context_from_string(content, "para_test")

        chunks = self.rlm.chunk_context(chunk_size=50, by="paragraphs")
        assert len(chunks) >= 1, "Should create at least 1 chunk"

    def test_context_stats(self):
        """Test getting context statistics."""
        content = "Hello World!\n\nSecond paragraph.\n\nThird one here."
        self.rlm.load_context_from_string(content, "stats_test")

        stats = self.rlm.get_context_stats()
        assert stats["context_id"] == "stats_test"
        assert stats["char_count"] == len(content)
        assert stats["line_count"] >= 3
        assert stats["paragraph_count"] == 3

    def test_recursion_tracking(self):
        """Test recursion depth tracking."""
        assert self.rlm.get_recursion_depth() == 0

        # Begin recursive call
        can_recurse, _ = self.rlm.begin_recursive_call("left", "test prompt")
        assert can_recurse
        assert self.rlm.get_recursion_depth() == 1

        # Nested call
        self.rlm.begin_recursive_call("right", "nested prompt")
        assert self.rlm.get_recursion_depth() == 2

        # End calls
        self.rlm.end_recursive_call()
        assert self.rlm.get_recursion_depth() == 1

        self.rlm.end_recursive_call()
        assert self.rlm.get_recursion_depth() == 0

    def test_max_recursion_depth(self):
        """Test that max recursion depth is enforced."""
        # Push to max depth
        for i in range(20):
            can_recurse, _ = self.rlm.begin_recursive_call("test", f"depth {i}")
            assert can_recurse, f"Should allow recursion at depth {i}"

        # 21st call should fail
        can_recurse, msg = self.rlm.begin_recursive_call("test", "overflow")
        assert not can_recurse
        assert "exceeded" in msg.lower()

    def test_global_stats(self):
        """Test global statistics tracking."""
        # Perform some operations
        self.rlm.load_context_from_string("test", "ctx1")
        self.rlm.search_context("test")
        self.rlm.chunk_context()

        stats = self.rlm.get_global_stats()
        assert stats["contexts_loaded"] >= 1
        assert stats["total_searches"] >= 1
        assert stats["total_chunks_created"] >= 1


class TestNexusRLMCommands:
    """Tests for NEXUS-RLM commands in the interpreter."""

    def setup_method(self):
        """Create fresh interpreter for each test."""
        self.interpreter = NexusInterpreter()
        # Clear RLM state
        rlm = get_rlm_context_manager()
        rlm.clear_all_contexts()
        rlm.reset_recursion()

    def test_context_load_command(self):
        """Test CONTEXT-LOAD command."""
        # Create temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Test content for NEXUS command.")
            temp_path = f.name

        try:
            result = self.interpreter.execute(f'(CONTEXT-LOAD "{temp_path}")')
            assert "OK-CONTEXT-LOADED" in result
        finally:
            os.unlink(temp_path)

    def test_context_load_missing_file(self):
        """Test CONTEXT-LOAD with missing file."""
        result = self.interpreter.execute('(CONTEXT-LOAD "/nonexistent/file.txt")')
        assert "ERROR" in result

    def test_context_stats_command(self):
        """Test CONTEXT-STATS command."""
        # First load some content
        rlm = get_rlm_context_manager()
        rlm.load_context_from_string("Test content here.", "test")

        result = self.interpreter.execute("(CONTEXT-STATS)")
        assert "Characters:" in result or "char_count" in result.lower()

    def test_context_stats_no_context(self):
        """Test CONTEXT-STATS when no context loaded."""
        result = self.interpreter.execute("(CONTEXT-STATS)")
        assert "ERROR" in result or "No context" in result

    def test_context_search_command(self):
        """Test CONTEXT-SEARCH command."""
        rlm = get_rlm_context_manager()
        rlm.load_context_from_string("The quick brown fox.", "search")

        result = self.interpreter.execute('(CONTEXT-SEARCH "quick")')
        assert "match" in result.lower() or "quick" in result.lower()

    def test_context_search_no_matches(self):
        """Test CONTEXT-SEARCH with no matches."""
        rlm = get_rlm_context_manager()
        rlm.load_context_from_string("Hello world.", "search")

        result = self.interpreter.execute('(CONTEXT-SEARCH "xyz123")')
        assert "No matches" in result

    def test_context_chunk_command(self):
        """Test CONTEXT-CHUNK command."""
        rlm = get_rlm_context_manager()
        rlm.load_context_from_string("A" * 10000, "chunk")

        result = self.interpreter.execute("(CONTEXT-CHUNK)")
        assert "chunks" in result.lower()

    def test_context_list_command(self):
        """Test CONTEXT-LIST command."""
        rlm = get_rlm_context_manager()
        rlm.load_context_from_string("Content 1", "ctx1")
        rlm.load_context_from_string("Content 2", "ctx2")

        result = self.interpreter.execute("(CONTEXT-LIST)")
        assert "ctx1" in result
        assert "ctx2" in result

    def test_recursion_depth_command(self):
        """Test RECURSION-DEPTH command."""
        result = self.interpreter.execute("(RECURSION-DEPTH)")
        assert result == 0 or "0" in str(result)

    def test_rlm_stats_command(self):
        """Test RLM-STATS command."""
        result = self.interpreter.execute("(RLM-STATS)")
        assert "Contexts Loaded" in result or "contexts_loaded" in result.lower()

    def test_llm_query_async_mode(self):
        """Test LLM-QUERY in async mode (no triad connected)."""
        # Without triad connected, should return PENDING
        result = self.interpreter.execute('(LLM-QUERY "left" "Test prompt")')
        assert "PENDING" in result

        # Check output queue
        assert len(self.interpreter.output_queue) >= 1
        action = self.interpreter.output_queue[-1]
        assert action["action"] == "LLM_QUERY"
        assert action["target"] == "left"

    def test_llm_query_missing_args(self):
        """Test LLM-QUERY with missing arguments."""
        result = self.interpreter.execute('(LLM-QUERY "left")')
        assert "ERROR" in result

    def test_llm_query_targets(self):
        """Test LLM-QUERY with different targets."""
        for target in ["left", "right", "colossus"]:
            result = self.interpreter.execute(f'(LLM-QUERY "{target}" "Test")')
            assert target.upper() in result


class TestRecursionState:
    """Tests for the RecursionState dataclass."""

    def test_initial_state(self):
        """Test initial recursion state."""
        state = RecursionState()
        assert state.current_depth == 0
        assert state.max_depth == 20
        assert len(state.call_history) == 0

    def test_push_and_pop(self):
        """Test push and pop operations."""
        state = RecursionState()

        state.push_call("left", "prompt 1")
        assert state.current_depth == 1
        assert len(state.call_history) == 1

        state.push_call("right", "prompt 2")
        assert state.current_depth == 2

        state.pop_call()
        assert state.current_depth == 1

    def test_can_recurse(self):
        """Test recursion limit check."""
        state = RecursionState()
        state.max_depth = 5

        for _ in range(5):
            assert state.can_recurse()
            state.push_call("test", "test")

        assert not state.can_recurse()


class TestRLMContext:
    """Tests for the RLMContext dataclass."""

    def test_token_estimation(self):
        """Test token count estimation."""
        content = "A" * 400  # 400 characters
        ctx = RLMContext(content=content)

        # ~4 chars per token, so 400/4 = 100 tokens
        assert ctx.token_count_estimate == 100

    def test_metadata(self):
        """Test context metadata."""
        ctx = RLMContext(
            content="test",
            source_path="/path/to/file.txt"
        )

        assert ctx.source_path == "/path/to/file.txt"
        assert ctx.loaded_at is not None


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
