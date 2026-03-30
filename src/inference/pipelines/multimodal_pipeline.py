"""Shim Multimodal Pipeline Module

This lightweight shim forwards to the canonical implementation in
`core.ai.inference.pipelines.multimodal_pipeline` to preserve backward
compatibility during restructuring. Once Phase 2 model/inference
consolidation is complete, references should be updated to the canonical
path and this file can be removed.
"""
from __future__ import annotations

from importlib import import_module

_IMPL_PATH = 'core.ai.inference.pipelines.multimodal_pipeline'
_impl = None

try:  # Resolve underlying module lazily
    _impl = import_module(_IMPL_PATH)
except Exception as _e:  # pragma: no cover
    _impl = None  # Defer errors until symbol access


def __getattr__(name: str):  # pragma: no cover - thin forwarding layer
    if _impl is None:
        raise ImportError(f'Underlying multimodal pipeline module not available: {_IMPL_PATH}')
    return getattr(_impl, name)

__all__ = []  # Populated dynamically via __getattr__
