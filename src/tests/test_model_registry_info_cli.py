#!/usr/bin/env python3
"""Test --info flag of registry CLI."""
import os
import subprocess
import sys


def test_cli_info():
    env = os.environ.copy()
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    src_dir = os.path.join(project_root, 'src')
    env['PYTHONPATH'] = src_dir + os.pathsep + env.get('PYTHONPATH', '')
    cli_path = os.path.join(src_dir, 'core', 'models', 'registry', 'cli.py')
    proc = subprocess.run([sys.executable, cli_path, '--info', 'b2_multimodal'], capture_output=True, text=True, check=True, env=env)
    assert "registered" in proc.stdout.lower()
