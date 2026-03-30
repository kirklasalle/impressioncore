#!/usr/bin/env python3
"""Launcher to run training wrapper with correct PYTHONPATH when executed from repo root.

Usage: .venv310\Scripts\python.exe run_wrapper.py --resume <path> --steps 200
"""
import os
import sys

# Ensure project root (this file's dir) is first on sys.path
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.training.scripts.run_stable_short import main

if __name__ == '__main__':
    main()
