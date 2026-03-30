"""Relocated media reorganization pipeline.

Original root reorganize_media_to_raw_pipeline.py retained temporarily.
"""
from __future__ import annotations

import warnings

warnings.warn(
    "Use pipelines.media.reorganize_media_to_raw_pipeline (root reorganize_media_to_raw_pipeline.py deprecated)",
    DeprecationWarning,
    stacklevel=2,
)
from reorganize_media_to_raw_pipeline import main  # type: ignore

__all__ = ["main"]
