"""Deprecated forwarder for legacy eval imports.

Canonical location:
    evaluation.suites.b3_eval_suite
"""

from __future__ import annotations

import warnings

warnings.warn(
    "Import from evaluation.suites.b3_eval_suite instead of eval.b3_eval_suite",
    DeprecationWarning,
    stacklevel=2,
)

from evaluation.suites.b3_eval_suite import eval_placeholder

__all__ = ["eval_placeholder"]
