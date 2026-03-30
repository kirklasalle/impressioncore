"""Deprecated `eval` package.

This package is retained as a thin compatibility layer. All evaluation
code has migrated to the `evaluation` package (see `evaluation.suites` and
`evaluation.benchmarks`). Please update imports:

    from eval.b3_eval_suite import eval_placeholder
    -> from evaluation.suites.b3_eval_suite import eval_placeholder

The shim will be removed in a later phase after a deprecation window.
"""
from __future__ import annotations

import warnings

warnings.warn(
    "`eval` package is deprecated; use `evaluation` instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = []
