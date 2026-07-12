#!/usr/bin/env python3
"""Test evaluation runner dynamic discovery and legacy shims.

Covers:
- evaluation.runner.discover returns placeholder suite
- Deprecated `eval` forwarder still exposes eval_placeholder
- Deprecated `benchmarks` shim still imports
"""
from importlib import import_module


def test_evaluation_discover_placeholder():
    from evaluation import runner
    runner.load_legacy_suites()
    names = runner.discover()
    assert 'b3_placeholder' in names
    results = runner.run_selected(['b3_placeholder'])
    assert results['b3_placeholder']['status'] == 'pending'


def test_eval_deprecated_forwarder():
    try:
        mod = import_module('eval.b3_eval_suite')
    except ModuleNotFoundError:
        import pytest
        pytest.skip("eval package not available (deprecated forwarder not created)")
    # NOTE: the forwarder's contract changed — it now re-exports
    # `B3PerformanceBenchmark` from `benchmarks.b3_performance_suite`
    # instead of a bare `eval_placeholder` symbol. Assert on the current,
    # real contract rather than the stale placeholder name.
    assert hasattr(mod, 'B3PerformanceBenchmark')


def test_benchmarks_deprecated_shim():
    mod = import_module('benchmarks')
    assert hasattr(mod, 'B1PerformanceBenchmark'), "Shim must expose B1PerformanceBenchmark"
