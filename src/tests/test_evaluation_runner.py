"""Basic tests for evaluation.runner Phase 1 placeholder.

Ensures registry mechanics work and legacy suite loading doesn't raise.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Add project src/ to path for direct package imports during restructuring
_project_root = Path(__file__).resolve().parents[2]
_src_path = _project_root / "src"
if str(_src_path) not in sys.path:
    sys.path.insert(0, str(_src_path))

import pytest

from evaluation import runner


def test_registry_and_discovery():
    # GIVEN a fresh registry (module import executed earlier)
    runner.load_legacy_suites()
    names = runner.discover()
    assert isinstance(names, list)

    # WHEN we register a temporary inline suite
    @runner.register("_temp_suite")
    def _tmp():
        return {"ok": True}

    # THEN it appears in discovery and run_all returns its result
    assert "_temp_suite" in runner.discover()
    results = runner.run_all()
    assert "_temp_suite" in results
    assert results["_temp_suite"]["ok"] is True


@pytest.mark.parametrize("select", [["_nonexistent"], []])
def test_run_selected_graceful(select):
    # Should not raise; nonexistent names skipped
    out = runner.run_selected(select)
    for name in select:
        if name in out:
            assert out[name] is not None
