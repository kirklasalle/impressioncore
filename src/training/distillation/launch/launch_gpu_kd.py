"""Relocated KD launch script.

Original root launch_gpu_knowledge_distillation_revolution.py retained temporarily.
"""
from __future__ import annotations

import warnings

warnings.warn(
    "Use distillation.launch.launch_gpu_kd (root launch_gpu_knowledge_distillation_revolution.py deprecated)",
    DeprecationWarning,
    stacklevel=2,
)
try:
    from launch_gpu_knowledge_distillation_revolution import main  # type: ignore
    __all__ = ["main"]
except Exception:  # pragma: no cover
    __all__ = []
