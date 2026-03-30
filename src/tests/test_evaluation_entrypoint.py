#!/usr/bin/env python3
"""Test the module entrypoint interface for evaluation package.

Validates that `python -m evaluation --list` path works by invoking the
internal main function (import-level test avoids spawning subprocess for speed).
"""
from importlib import import_module


def test_evaluation_module_list():
    mod = import_module('evaluation.__main__')
    # Ensure the module exposes a main-like function
    assert hasattr(mod, 'main')
    # Call main with --list and capture returned code (should be 0)
    rc = mod.main(['--list'])
    assert rc == 0
