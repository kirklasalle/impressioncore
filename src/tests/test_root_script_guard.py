"""Test: root script governance.

Ensures no unauthorized Python files exist directly under `src/`.
Relies on dev_tools.ci.root_script_guard logic.
"""
from __future__ import annotations

from dev_tools.ci.root_script_guard import validate_structure


def test_root_scripts_clean():
    ok, message = validate_structure(fail_on_duplicates=True)
    assert ok, f"Root script guard violations:\n{message}"
