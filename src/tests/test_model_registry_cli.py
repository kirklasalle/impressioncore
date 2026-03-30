#!/usr/bin/env python3
"""Basic smoke test for registry CLI listing."""
import os
import subprocess
import sys


def test_cli_list_models():
    env = os.environ.copy()
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    src_dir = os.path.join(project_root, 'src')
    existing = env.get('PYTHONPATH', '')
    env['PYTHONPATH'] = src_dir + (os.pathsep + existing if existing else '')
    cli_path = os.path.join(src_dir, 'core', 'models', 'registry', 'cli.py')
    proc = subprocess.run([sys.executable, cli_path, '--list'], capture_output=True, text=True, check=True, env=env)
    out = proc.stdout.strip().splitlines()
    assert any(name in out for name in ('b2_multimodal', 'b3_unified_bridge'))
