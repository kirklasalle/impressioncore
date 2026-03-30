"""Smoke test for model registry Phase 2 scaffold."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_root = Path(__file__).resolve().parents[2]
_src = _root / 'src'
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

pytest.importorskip("core.models", reason="core.models not available in current path layout")
from core.models import registry


def test_registry_lists_entry():
    assert 'b3_unified_bridge' in registry.list_models()


def test_b3_unified_bridge_factory_lazy():
    entry = registry.MODEL_REGISTRY['b3_unified_bridge']
    payload = entry()
    assert 'instance' in payload
    assert payload['instance'] is not None
