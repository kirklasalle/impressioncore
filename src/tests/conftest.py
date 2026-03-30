#!/usr/bin/env python3
"""Global pytest configuration.

Responsibilities:
- Ensure `src` is on sys.path once for all tests.
- Register custom markers (slow).
- Provide optional global skipping for slow tests (IC_SKIP_SLOW env var).
- Ensure UTF-8 output on Windows to avoid cp1252 encoding errors.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Ensure UTF-8 output on Windows (avoids cp1252 UnicodeEncodeError for ✓/✗/emoji)
# ---------------------------------------------------------------------------
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = PROJECT_ROOT / 'src'
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

def pytest_configure(config):  # pragma: no cover
    config.addinivalue_line("markers", "slow: marks tests as slow (set IC_SKIP_SLOW=0 to run)")
    config.addinivalue_line("markers", "integration: marks tests that exercise multi-component flows")

def pytest_collection_modifyitems(config, items):  # pragma: no cover
    if os.getenv("IC_SKIP_SLOW", "1") == "0":
        return
    skip_slow = pytest.mark.skip(reason="IC_SKIP_SLOW not disabled")
    for item in items:
        if 'slow' in item.keywords:
            item.add_marker(skip_slow)


# ---------------------------------------------------------------------------
# Re-export shared fixtures so they are available to all tests
# ---------------------------------------------------------------------------
from src.tests.fixtures import (  # noqa: F401
    clean_env,
    config_dir,
    no_cuda,
    project_root,
    sample_checkpoint,
    src_root,
    tmp_config,
    tmp_dir,
)
