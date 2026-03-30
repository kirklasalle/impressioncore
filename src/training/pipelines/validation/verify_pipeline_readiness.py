"""Relocated pipeline readiness verification.

Original root verify_pipeline_readiness.py retained temporarily.
"""
from __future__ import annotations

import warnings

warnings.warn(
    "Use pipelines.validation.verify_pipeline_readiness (root verify_pipeline_readiness.py deprecated)",
    DeprecationWarning,
    stacklevel=2,
)
from verify_pipeline_readiness import main  # type: ignore

__all__ = ["main"]
