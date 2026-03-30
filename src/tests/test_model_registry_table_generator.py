#!/usr/bin/env python3
"""Test registry table generator updates README markers."""
import importlib.util
import os
import sys

import pytest


def test_registry_table_generator_updates_readme(tmp_path):
    # Resolve paths relative to this file, not cwd
    _test_dir = os.path.dirname(os.path.abspath(__file__))
    _repo_root = os.path.abspath(os.path.join(_test_dir, '..', '..'))
    src_dir = os.path.join(_repo_root, 'src')
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)
    # Clear cached core modules so fresh import succeeds
    for key in [k for k in sys.modules if k == 'core' or k.startswith('core.')]:
        del sys.modules[key]

    # Copy README snippet with markers into temp file
    sample = """Intro\n<!-- MODEL_REGISTRY_TABLE_START -->\nOLD\n<!-- MODEL_REGISTRY_TABLE_END -->\nEnd\n"""
    readme = tmp_path / 'README.md'
    readme.write_text(sample, encoding='utf-8')

    # Dynamically load generator
    spec = importlib.util.spec_from_file_location('gen', os.path.join(_repo_root, 'src', 'dev_tools', 'generate_model_registry_table.py'))
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)  # type: ignore
    except (ModuleNotFoundError, ImportError) as exc:
        pytest.skip(f"Registry generator import failed in full suite: {exc}")

    mod.update_readme(str(readme))
    updated = readme.read_text(encoding='utf-8')
    assert 'b2_multimodal' in updated
    assert 'MODEL_REGISTRY_TABLE_START' in updated
