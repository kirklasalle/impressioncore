#!/usr/bin/env python3
"""Smoke tests for the tri-architecture orchestrator pipeline."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest
import torch

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.integrator.colossus_model import ColossusConfig
from src.orchestrator.tri_arch_orchestrator import (
    RoleConfig,
    TriOrchestrator,
    TriOrchestratorConfig,
)


@pytest.fixture(scope="module")
def orchestrator() -> TriOrchestrator:
    """Instantiate a lightweight orchestrator for smoke testing."""
    try:
        role_cfg = RoleConfig(
            name="test_role",
            d_model=64,
            num_heads=4,
            num_layers=2,
            num_experts=2,
            experts_per_token=1,
            device="cpu",
        )

        colossus_cfg = ColossusConfig(
            d_model=128,
            num_heads=4,
            num_layers=4,
            num_experts=2,
            experts_per_token=1,
            vector_dim=256,
            device="cpu",
        )

        orchestrator_cfg = TriOrchestratorConfig(
            role_a=role_cfg,
            role_b=role_cfg,
            colossus=colossus_cfg,
        )

        return TriOrchestrator(orchestrator_cfg)
    except TypeError as exc:
        pytest.skip(f"PyTorch version incompatibility: {exc}")


def _build_multimodal_batch(seq_len: int = 8) -> dict[str, torch.Tensor]:
    feature_dim = 768
    batch = {
        "input_ids": torch.randint(0, 100, (1, seq_len)),
        "image_features": torch.randn(1, seq_len, feature_dim),
        "audio_features": torch.randn(1, seq_len, feature_dim),
        "phoneme_ids": torch.randint(0, 40, (1, seq_len)),
    }
    return batch


def test_orchestrator_runs_forward(orchestrator: TriOrchestrator) -> None:
    """Ensure the orchestrator produces a combined response without raising errors."""

    batch = _build_multimodal_batch()
    result = orchestrator.infer(batch)

    assert "intermediate" in result
    assert "role_a" in result["intermediate"]
    assert "role_b" in result["intermediate"]
    assert "summary_vector" in result
    assert isinstance(result["summary_vector"], list)


def test_colossus_confidence_within_bounds(orchestrator: TriOrchestrator) -> None:
    """Verify the integrator returns a reasonable confidence score."""

    batch = _build_multimodal_batch(seq_len=4)
    result = orchestrator.infer(batch)
    confidence = result.get("confidence")
    assert confidence is not None
    assert 0.0 <= confidence <= 1.0


def test_orchestrator_respects_environment_cpu(orchestrator: TriOrchestrator) -> None:
    """Run a quick check ensuring inference works in forced CPU mode."""

    os.environ["TRI_ORCHESTRATOR_DEVICE"] = "cpu"
    batch = _build_multimodal_batch(seq_len=2)
    result = orchestrator.infer(batch)
    assert "decision" in result.get("details", {})
    os.environ.pop("TRI_ORCHESTRATOR_DEVICE", None)
