"""Relocated production inference entrypoint.

Original root production_inference.py retained temporarily.
"""
from __future__ import annotations

import warnings

warnings.warn(
    "Use inference.runtime.production_inference (root production_inference.py deprecated)",
    DeprecationWarning,
    stacklevel=2,
)
from production_inference import *  # type: ignore  # re-export all for now
