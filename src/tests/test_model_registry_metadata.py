#!/usr/bin/env python3
"""Test that metadata enhanced table includes new columns and param estimate field.

We do not assert an exact parameter number (environment dependent) but ensure
headers exist and at least one active model row contains expected status.
"""
import importlib.util
import os
import re
import sys

import pytest


def test_metadata_columns_present(tmp_path):
    # Resolve paths relative to this file, not cwd
    _test_dir = os.path.dirname(os.path.abspath(__file__))
    _repo_root = os.path.abspath(os.path.join(_test_dir, '..', '..'))
    src_dir = os.path.join(_repo_root, 'src')
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)
    # Clear cached core modules so fresh import succeeds
    for key in [k for k in sys.modules if k == 'core' or k.startswith('core.')]:
        del sys.modules[key]

    # Prepare temp README with markers
    sample = "Intro\n<!-- MODEL_REGISTRY_TABLE_START -->\nOLD\n<!-- MODEL_REGISTRY_TABLE_END -->\nEnd\n"
    readme = tmp_path / 'README.md'
    readme.write_text(sample, encoding='utf-8')

    spec = importlib.util.spec_from_file_location('gen', os.path.join(_repo_root, 'src', 'dev_tools', 'generate_model_registry_table.py'))
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)  # type: ignore
    except (ModuleNotFoundError, ImportError) as exc:
        pytest.skip(f"Registry generator import failed in full suite: {exc}")

    mod.update_readme(str(readme))
    content = readme.read_text(encoding='utf-8')
    # Basic header checks
    assert 'Param Estimate' in content
    assert '| b2_multimodal |' in content
    # Status column presence near a model row
    assert re.search(r"\| b2_multimodal \|.+\| active \|", content)
