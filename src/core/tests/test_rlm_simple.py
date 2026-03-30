"""
Simple Test Runner for NEXUS Extended (No pytest required)

Created: January 20, 2026
Run: python src/core/tests/test_rlm_simple.py
"""

import os
import sys
import traceback

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from src.orchestrator.nexus_context_manager import get_rlm_context_manager
from src.orchestrator.nexus_interpreter import NexusInterpreter


class TestRunner:
    """Simple test runner without pytest."""

    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []

    def run_test(self, name, test_func):
        """Run a single test."""
        try:
            test_func()
            self.passed += 1
            print(f"  PASS {name}")
        except AssertionError as e:
            self.failed += 1
            self.errors.append((name, str(e)))
            print(f"  FAIL {name}: {e}")
        except Exception as e:
            self.failed += 1
            self.errors.append((name, traceback.format_exc()))
            print(f"  ERROR {name}: {e}")

    def summary(self):
        """Print test summary."""
        total = self.passed + self.failed
        print(f"\n{'='*50}")
        print(f"Results: {self.passed}/{total} passed")
        if self.failed:
            print("\nFailed tests:")
            for name, _error in self.errors:
                print(f"  - {name}")
        print(f"{'='*50}")
        return self.failed == 0


def run_all_tests():
    """Run all NEXUS tests."""
    runner = TestRunner()

    # Reset state
    rlm = get_rlm_context_manager()
    rlm.clear_all_contexts()
    rlm.reset_recursion()

    print("\nNEXUS Extended Test Suite\n")

    # === Context Manager Tests ===
    print("Context Manager Tests:")

    def test_singleton():
        rlm1 = get_rlm_context_manager()
        rlm2 = get_rlm_context_manager()
        assert rlm1 is rlm2, "Singleton pattern failed"
    runner.run_test("Singleton pattern", test_singleton)

    def test_load_string():
        rlm = get_rlm_context_manager()
        rlm.clear_all_contexts()
        success, msg = rlm.load_context_from_string("Hello World!", "test")
        assert success, f"Failed to load: {msg}"
        assert rlm.active_context_id == "test"
    runner.run_test("Load context from string", test_load_string)

    def test_search():
        rlm = get_rlm_context_manager()
        rlm.clear_all_contexts()
        rlm.load_context_from_string("The quick brown fox jumps.", "search")
        results = rlm.search_context("fox")
        assert len(results) >= 1, "Should find at least one match"
    runner.run_test("Context search", test_search)

    def test_chunking():
        rlm = get_rlm_context_manager()
        rlm.clear_all_contexts()
        rlm.load_context_from_string("A" * 1000, "chunk")
        chunks = rlm.chunk_context(chunk_size=200, overlap=0)
        assert len(chunks) == 5, f"Expected 5 chunks, got {len(chunks)}"
    runner.run_test("Context chunking", test_chunking)

    def test_stats():
        rlm = get_rlm_context_manager()
        rlm.clear_all_contexts()
        rlm.load_context_from_string("Hello World!", "stats")
        stats = rlm.get_context_stats()
        assert stats["context_id"] == "stats"
        assert stats["char_count"] == 12
    runner.run_test("Context statistics", test_stats)

    def test_recursion():
        rlm = get_rlm_context_manager()
        rlm.reset_recursion()
        assert rlm.get_recursion_depth() == 0
        rlm.begin_recursive_call("left", "test")
        assert rlm.get_recursion_depth() == 1
        rlm.end_recursive_call()
        assert rlm.get_recursion_depth() == 0
    runner.run_test("Recursion tracking", test_recursion)

    def test_max_recursion():
        rlm = get_rlm_context_manager()
        rlm.reset_recursion()
        for i in range(20):
            can, _ = rlm.begin_recursive_call("test", f"depth {i}")
            assert can, f"Should allow depth {i}"
        can, msg = rlm.begin_recursive_call("test", "overflow")
        assert not can, "Should block at depth 20"
        rlm.reset_recursion()
    runner.run_test("Max recursion enforcement", test_max_recursion)

    # === NEXUS Command Tests ===
    print("\nNEXUS Command Tests:")

    def test_context_list():
        interpreter = NexusInterpreter()
        rlm = get_rlm_context_manager()
        rlm.clear_all_contexts()
        rlm.load_context_from_string("Test", "ctx1")
        result = interpreter.execute("(CONTEXT-LIST)")
        assert "ctx1" in result
    runner.run_test("CONTEXT-LIST command", test_context_list)

    def test_context_stats_cmd():
        interpreter = NexusInterpreter()
        rlm = get_rlm_context_manager()
        rlm.clear_all_contexts()
        rlm.load_context_from_string("Test content", "test")
        result = interpreter.execute("(CONTEXT-STATS)")
        assert "Characters" in result or "char" in result.lower()
    runner.run_test("CONTEXT-STATS command", test_context_stats_cmd)

    def test_rlm_stats():
        interpreter = NexusInterpreter()
        result = interpreter.execute("(RLM-STATS)")
        assert "Contexts" in result or "contexts" in result.lower()
    runner.run_test("RLM-STATS command", test_rlm_stats)

    def test_recursion_depth_cmd():
        interpreter = NexusInterpreter()
        rlm = get_rlm_context_manager()
        rlm.reset_recursion()
        result = interpreter.execute("(RECURSION-DEPTH)")
        assert result == 0 or str(result) == "0"
    runner.run_test("RECURSION-DEPTH command", test_recursion_depth_cmd)

    def test_llm_query_async():
        interpreter = NexusInterpreter()
        rlm = get_rlm_context_manager()
        rlm.reset_recursion()
        result = interpreter.execute('(LLM-QUERY "left" "Test prompt")')
        assert "PENDING" in result, f"Expected PENDING, got: {result}"
    runner.run_test("LLM-QUERY async mode", test_llm_query_async)

    def test_llm_query_queue():
        interpreter = NexusInterpreter()
        interpreter.output_queue.clear()
        rlm = get_rlm_context_manager()
        rlm.reset_recursion()
        interpreter.execute('(LLM-QUERY "right" "Creative test")')
        assert len(interpreter.output_queue) >= 1
        assert interpreter.output_queue[-1]["target"] == "right"
    runner.run_test("LLM-QUERY output queue", test_llm_query_queue)

    # === Parallel Execution Tests ===
    print("\nParallel Execution Tests:")

    def test_async_command():
        interpreter = NexusInterpreter()
        result = interpreter.execute('(ASYNC (RECURSION-DEPTH))')
        assert result.startswith("async_"), f"Expected async ID, got: {result}"
    runner.run_test("ASYNC command", test_async_command)

    def test_await_command():
        interpreter = NexusInterpreter()
        rlm = get_rlm_context_manager()
        rlm.reset_recursion()
        # Start async task with RECURSION-DEPTH
        async_id = interpreter.execute('(ASYNC (RECURSION-DEPTH))')
        # Wait for result
        import time
        time.sleep(0.1)  # Brief delay for thread to complete
        result = interpreter.execute(f'(AWAIT "{async_id}" 1000)')
        assert result == 0, f"Expected 0, got: {result}"
    runner.run_test("AWAIT command", test_await_command)

    def test_parallel_command():
        interpreter = NexusInterpreter()
        rlm = get_rlm_context_manager()
        rlm.reset_recursion()
        result = interpreter.execute('(PARALLEL (RECURSION-DEPTH) (RECURSION-DEPTH) (RECURSION-DEPTH))')
        assert result == [0, 0, 0], f"Expected [0, 0, 0], got: {result}"
    runner.run_test("PARALLEL command", test_parallel_command)

    # === v1.4 Utility Tests ===
    print("\nUtility Command Tests (v1.4):")

    def test_arithmetic_add():
        interpreter = NexusInterpreter()
        result = interpreter.execute('(+ 10 20 30)')
        assert result == 60, f"Expected 60, got: {result}"
    runner.run_test("+ (addition)", test_arithmetic_add)

    def test_arithmetic_sub():
        interpreter = NexusInterpreter()
        result = interpreter.execute('(- 100 30 20)')
        assert result == 50, f"Expected 50, got: {result}"
    runner.run_test("- (subtraction)", test_arithmetic_sub)

    def test_arithmetic_mul():
        interpreter = NexusInterpreter()
        result = interpreter.execute('(* 5 4 3)')
        assert result == 60, f"Expected 60, got: {result}"
    runner.run_test("* (multiplication)", test_arithmetic_mul)

    def test_arithmetic_div():
        interpreter = NexusInterpreter()
        result = interpreter.execute('(/ 100 5 2)')
        assert result == 10, f"Expected 10, got: {result}"
    runner.run_test("/ (division)", test_arithmetic_div)

    def test_concat():
        interpreter = NexusInterpreter()
        result = interpreter.execute('(CONCAT "Hello" " " "World")')
        assert result == "Hello World", f"Expected 'Hello World', got: {result}"
    runner.run_test("CONCAT command", test_concat)

    def test_list():
        interpreter = NexusInterpreter()
        result = interpreter.execute('(LIST 1 2 3)')
        assert result == [1, 2, 3], f"Expected [1, 2, 3], got: {result}"
    runner.run_test("LIST command", test_list)

    def test_pipeline():
        interpreter = NexusInterpreter()
        rlm = get_rlm_context_manager()
        rlm.reset_recursion()
        # Simple pipeline test
        result = interpreter.execute('(PIPELINE (+ 1 2) (+ _ 10))')
        assert result == 13, f"Expected 13 (3 + 10), got: {result}"
    runner.run_test("PIPELINE command", test_pipeline)

    # Print summary
    return runner.summary()


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
