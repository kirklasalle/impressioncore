"""Relocated KD dataset build entrypoint.

Original: project root build_kd_dataset.py (kept temporarily as source).
After grace period, logic should move here fully and root file removed.
"""
from __future__ import annotations

import warnings

warnings.warn(
    "Use distillation.datasets.build_kd_dataset (root build_kd_dataset.py deprecated)",
    DeprecationWarning,
    stacklevel=2,
)


# Re-import functions from original module for now
from build_kd_dataset import build_kd_records, write_manifest  # type: ignore

__all__ = ["build_kd_records", "write_manifest"]
