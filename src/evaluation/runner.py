"""Unified Evaluation Runner (Phase 1 Placeholder)

Goal: Provide a single entrypoint to orchestrate evaluation suites post-migration.
Current State: Scans for registered evaluation modules; future phases will
integrate benchmark discovery and reporting.
"""
from __future__ import annotations

import pkgutil
from collections.abc import Callable
from importlib import import_module
from typing import Any

REGISTRY: dict[str, Callable[[], Any]] = {}


def register(name: str):  # Decorator for future evaluation suites
    def _wrap(fn: Callable[[], Any]):
        REGISTRY[name] = fn
        return fn
    return _wrap


def discover() -> list[str]:  # Phase 2: dynamic discovery via pkgutil
    # Dynamically import modules under evaluation.suites.* to allow
    # their @register decorators to populate REGISTRY.
    pkg_name = 'evaluation.suites'
    try:
        pkg = import_module(pkg_name)
        for m in pkgutil.iter_modules(pkg.__path__, prefix=f"{pkg_name}."):
            try:
                import_module(m.name)
            except Exception:  # pragma: no cover - best effort
                continue
    except Exception:  # pragma: no cover
        pass
    return sorted(REGISTRY.keys())


def run_all() -> dict[str, Any]:
    results: dict[str, Any] = {}
    for name, fn in REGISTRY.items():
        try:
            results[name] = fn()
        except Exception as e:
            results[name] = {"error": str(e)}
    return results


def run_selected(names: list[str]) -> dict[str, Any]:
    return {n: REGISTRY[n]() for n in names if n in REGISTRY}


def load_legacy_suites():  # Load migrated suites & archived benchmarks
    # Focus on evaluation.* canonical paths; deprecated 'eval' kept as shim
    for mod in (
        'evaluation.suites.b3_eval_suite',
        'evaluation.benchmarks.b1_performance_suite',
    ):
        try:  # pragma: no cover
            import_module(mod)
        except Exception:
            continue


__all__ = ["discover", "load_legacy_suites", "register", "run_all", "run_selected"]

