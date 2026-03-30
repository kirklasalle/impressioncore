"""Relocated teacher outputs converter.

Original root script retained temporarily.
"""
from __future__ import annotations

import warnings

warnings.warn(
    "Use distillation.processing.convert_teacher_outputs (root convert_teacher_outputs.py deprecated)",
    DeprecationWarning,
    stacklevel=2,
)

from convert_teacher_outputs import main  # type: ignore

__all__ = ["main"]
