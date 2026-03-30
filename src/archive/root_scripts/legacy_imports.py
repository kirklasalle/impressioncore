"""Legacy Import Shim (Phase 0)

Created: August 23, 2025
Status: Active (Temporary)

Purpose:
  Provide backward-compatible import paths during the multi-phase directory migration.
  This file will be removed once all references are updated to the new structure.

Usage:
  Instead of editing every older file immediately, selectively update imports to:

      from legacy_imports import *  # not recommended long-term

  Prefer targeted refactors; this is a stopgap for modules that would otherwise break.

IMPORTANT:
  Currently only defines symbolic re-exports AFTER actual moves occur. For now it is
  mostly a placeholder scaffolding to fill in as directories are migrated.
"""
from importlib import import_module
from typing import Any, Callable

# Phase 1 minimal re-exports (evaluation metrics)
symbols: dict[str, Any] = {}

def _attempt(name: str, attr: str):  # helper
  try:  # pragma: no cover
    mod = import_module(name)
    obj = getattr(mod, attr)
    symbols[attr] = obj
  except Exception:  # noqa: BLE001
    pass

_attempt('evaluation.metrics', 'BestModelTracker')
_attempt('evaluation.suites.b3_eval_suite', 'eval_placeholder')
_attempt('evaluation.benchmarks.b1_performance_suite', 'B1PerformanceBenchmark')

globals().update(symbols)
__all__ = list(symbols.keys())

# Dynamic fallback registry for legacy symbol lookups that may disappear.
_DYNAMIC_FALLBACKS: dict[str, Callable[..., Any]] = {}

def _fallback_get_embedding_dataloaders(*_args, **_kwargs):  # pragma: no cover
    """Return an empty dict as safe placeholder.

    Allows legacy import tests expecting symbol presence to proceed without
    raising ImportError when underlying data pipeline not yet wired.
    """
    return {}

_DYNAMIC_FALLBACKS['training.datasets.data_loading.get_embedding_dataloaders'] = _fallback_get_embedding_dataloaders

def resolve_legacy(name: str) -> Any:
  """Attempt to dynamically import a legacy symbol, falling back if needed."""
  try:
    module_path, attr = name.rsplit('.', 1)
    mod = import_module(module_path)
    return getattr(mod, attr)
  except Exception:  # noqa: BLE001
    if name in _DYNAMIC_FALLBACKS:
      return _DYNAMIC_FALLBACKS[name]
    raise



