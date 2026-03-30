"""Deprecated B3 evaluation suite stub.

Migrated to `evaluation.suites.b3_eval_suite`. This module remains only as a
compatibility forwarder and will be removed in a future cleanup phase.
"""
from __future__ import annotations

import warnings

warnings.warn(
    "Import from evaluation.suites.b3_eval_suite instead of eval.b3_eval_suite",
    DeprecationWarning,
    stacklevel=2,
)

from evaluation.suites.b3_eval_suite import eval_placeholder  # type: ignore

__all__ = ["eval_placeholder"]
