"""Forwarder for legacy eval imports.

Canonical location:
    benchmarks.b3_performance_suite
"""

from __future__ import annotations

import warnings

warnings.warn(
    "Import from benchmarks.b3_performance_suite instead of eval.b3_eval_suite",
    DeprecationWarning,
    stacklevel=2,
)

from src.benchmarks.b3_performance_suite import B3PerformanceBenchmark

__all__ = ["B3PerformanceBenchmark"]
