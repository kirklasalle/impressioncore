"""Relocated KD demo script.

Original root demo_gpu_knowledge_distillation_revolution.py retained temporarily.
"""
from __future__ import annotations

import warnings

warnings.warn(
    "Use distillation.demos.gpu_kd_demo (root demo_gpu_knowledge_distillation_revolution.py deprecated)",
    DeprecationWarning,
    stacklevel=2,
)

try:  # if original exposes a main
    from demo_gpu_knowledge_distillation_revolution import main  # type: ignore
    __all__ = ["main"]
except Exception:  # pragma: no cover
    __all__ = []
