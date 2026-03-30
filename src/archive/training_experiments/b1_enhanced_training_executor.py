"""Shim: Archived B1 Enhanced Training Executor

Relocated to `archive/training/b1_enhanced_training_executor.py`.
This file will be removed after the deprecation grace period.
"""
from __future__ import annotations
import warnings

warnings.warn(
    "training.b1_enhanced_training_executor is archived; see archive.training.b1_enhanced_training_executor",
    DeprecationWarning,
    stacklevel=2,
)

__all__: list[str] = []
 # (No functional code – archived stub)
