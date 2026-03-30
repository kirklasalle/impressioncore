"""Shared pytest fixtures for ImpressionCore tests.

Provides lightweight, reusable fixtures that don't depend on heavy
model loading or GPU availability.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import pytest

# ---------------------------------------------------------------------------
# Path fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def project_root() -> Path:
    """Return the absolute path of the project root."""
    return Path(__file__).resolve().parents[2]


@pytest.fixture
def src_root(project_root: Path) -> Path:
    """Return the absolute path of the src/ directory."""
    return project_root / "src"


@pytest.fixture
def config_dir(project_root: Path) -> Path:
    """Return the canonical config directory."""
    return project_root / "src" / "core" / "config"


# ---------------------------------------------------------------------------
# Temp directory fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def tmp_dir(tmp_path: Path) -> Path:
    """Alias for pytest's tmp_path with a shorter name."""
    return tmp_path


@pytest.fixture
def tmp_config(tmp_path: Path) -> Path:
    """Create a minimal JSON config in a temp directory and return its path."""
    cfg = {
        "model_type": "test",
        "vocab_size": 1000,
        "hidden_dim": 64,
        "num_layers": 2,
    }
    path = tmp_path / "test_config.json"
    path.write_text(json.dumps(cfg, indent=2))
    return path


# ---------------------------------------------------------------------------
# Environment fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def no_cuda(monkeypatch: pytest.MonkeyPatch):
    """Force CUDA unavailable for deterministic CPU-only tests."""
    monkeypatch.setenv("CUDA_VISIBLE_DEVICES", "")


@pytest.fixture
def clean_env(monkeypatch: pytest.MonkeyPatch):
    """Remove ImpressionCore-specific env vars for isolated tests."""
    for key in list(os.environ):
        if key.startswith("IMPRESSIONCORE_") or key.startswith("AGENT0CORE_"):
            monkeypatch.delenv(key, raising=False)


# ---------------------------------------------------------------------------
# Sample data fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_checkpoint(tmp_path: Path) -> Path:
    """Create a minimal fake checkpoint file for testing load utilities."""
    import torch

    ckpt: dict[str, Any] = {
        "global_step": 100,
        "model_state_dict": {"layer.weight": torch.randn(4, 4)},
        "config": {"hidden_dim": 64},
        "loss_history": [1.0, 0.8, 0.6],
    }
    path = tmp_path / "test_checkpoint.pt"
    torch.save(ckpt, path)
    return path
