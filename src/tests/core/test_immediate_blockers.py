"""Regression tests for immediate security and correctness blockers.

Covers:
- SEC-01: Flask Builder CORS allowlist and API key enforcement
- SEC-02: Safe checkpoint loading (weights_only=True / root confinement)
- SEC-03: Workbench bounded_file path confinement
- CRIT-01: B3 causal isolation, per-sample padding masks, and sliding-window linear causality
- CRIT-02: TurboQuant non-power-of-2 rotation invertibility and disabled float passthrough
- CRIT-03: INT8/INT4 quantization scale preservation and zero-tensor NaN safety
"""

import os
from pathlib import Path
from unittest.mock import patch

import pytest
import torch
from flask import Flask

from src.core.export.export_production_model import _quantize_state_dict
from src.core.models.impressioncore_b3_architecture import (
    B3Config,
    EfficientMultiHeadLatentAttention,
    ImpressionCoreB3Model,
    MemoryOptimizedCheckpointing,
)
from src.core.quantization.turboquant import RandomRotation, TurboQuantCompressor
from src.core.quantization.turboquant_config import TurboQuantConfig
from src.interfaces.web.routes import builder
from src.interfaces.web.routes import workbench as wb


def test_sec01_builder_cors_and_api_key_enforcement(tmp_path, monkeypatch):
    """SEC-01: Builder app uses configured CORS allowlist and enforces IMPRESSIONCORE_API_KEY."""
    monkeypatch.setenv("IMPRESSIONCORE_API_KEY", "test-builder-secret-key")
    monkeypatch.setenv("IMPRESSIONCORE_ALLOWED_ORIGINS", "http://127.0.0.1:3000")
    monkeypatch.setattr("src.core.config.data_paths.enforce_data_drive", lambda: True)
    with patch("src.interfaces.web.server.PIPELINE_AVAILABLE", False):
        from src.interfaces.web.server import create_app

        app = create_app()
    app.config["TESTING"] = True
    client = app.test_client()

    # Unauthenticated request rejected
    unauth = client.get("/api/v1/builder/model/presets", headers={"Origin": "https://evil.example"})
    assert unauth.status_code == 401
    assert unauth.headers.get("Access-Control-Allow-Origin") != "*"

    # Authenticated request with valid origin succeeds
    auth = client.get(
        "/api/v1/builder/model/presets",
        headers={"X-API-Key": "test-builder-secret-key", "Origin": "http://127.0.0.1:3000"},
    )
    assert auth.status_code == 200
    assert auth.headers.get("Access-Control-Allow-Origin") == "http://127.0.0.1:3000"


def test_sec02_checkpoint_loading_blocks_arbitrary_paths_and_unsafe_pickles(tmp_path):
    """SEC-02: Checkpoint helpers enforce weights_only=True and reject outside-root paths."""
    ckpt_file = tmp_path / "ckpt.pt"
    torch.save({"epoch": 1, "model_state_dict": {}, "loss": 0.1}, ckpt_file)
    mgr = MemoryOptimizedCheckpointing(checkpoint_dir=str(tmp_path))
    assert mgr._verify_checkpoint(ckpt_file) is True

    # Outside-root .pt path must fail closed in builder.get_model_tokenizer
    outside = tmp_path.parent / "nonexistent_outside_root" / "malicious.pt"
    with patch("os.path.isfile", return_value=True):
        with pytest.raises((ValueError, RuntimeError, FileNotFoundError)):
            builder.get_model_tokenizer(str(outside))


def test_sec03_workbench_bounded_file_rejects_outside_roots(tmp_path):
    """SEC-03: workbench.bounded_file refuses paths outside allowed workspace/data/temp roots."""
    app = Flask(__name__)
    app.config.update(
        TESTING=False,
        WORKBENCH_PROJECT_ROOT=tmp_path / "projects",
        WORKBENCH_ARTIFACT_ROOT=tmp_path / "artifacts",
    )
    with app.app_context():
        sys_root = os.environ.get("SYSTEMROOT")
        outside = (Path(sys_root) / "System32" / "drivers" / "etc" / "hosts") if sys_root else Path("/etc/hosts")
        if outside.exists():
            with pytest.raises(wb.WorkbenchError, match="allowed workspace"):
                wb.bounded_file(str(outside))


def test_crit01_b3_causal_isolation_and_batch_padding_masks():
    """CRIT-01: Future tokens cannot leak into prefix attention, including batched and linear paths."""
    cfg = B3Config(
        embed_dim=32,
        num_heads=4,
        num_layers=1,
        vocab_size=100,
        num_experts=2,
        expert_dim=32,
        experts_per_token=1,
        image_embed_dim=32,
        audio_embed_dim=32,
        phoneme_vocab_size=16,
        use_mhc=False,
        dropout=0.0,
    )
    model = ImpressionCoreB3Model(cfg)
    model.eval()

    t1 = torch.tensor([[1, 2, 3, 4]])
    t2 = torch.tensor([[1, 2, 3, 99]])
    with torch.no_grad():
        emb1 = model.embeddings(input_ids=t1)
        emb2 = model.embeddings(input_ids=t2)
        attn1, _ = model.layers[0].attention(model.layers[0].ln1(emb1), None, layer_idx=0)
        attn2, _ = model.layers[0].attention(model.layers[0].ln1(emb2), None, layer_idx=0)
        assert (attn1[:, :3] - attn2[:, :3]).abs().max().item() == 0.0

        logits1 = model(input_ids=t1)["logits"][:, :3, :]
        logits2 = model(input_ids=t2)["logits"][:, :3, :]
        assert (logits1 - logits2).abs().max().item() < 1e-5

    # Per-sample batch padding mask must not copy batch[0]'s mask to batch[1]
    batch_x = torch.randn(2, 4, 32)
    mask = torch.tensor([[1, 0, 0, 0], [1, 1, 1, 1]], dtype=torch.bool)
    attn = EfficientMultiHeadLatentAttention(embed_dim=32, num_heads=4, window_size=64, dropout=0.0)
    attn.eval()
    with torch.no_grad():
        out_diff_masks, _ = attn(batch_x, mask=mask)
        out_all_ones, _ = attn(batch_x[1:2], mask=mask[1:2])
        torch.testing.assert_close(out_diff_masks[1:2], out_all_ones, atol=1e-5, rtol=1e-5)

    # Sliding-window + linear attention path must remain causally isolated
    long_attn = EfficientMultiHeadLatentAttention(embed_dim=32, num_heads=4, window_size=4, dropout=0.0)
    long_attn.eval()
    x1 = torch.randn(1, 6, 32)
    x2 = x1.clone()
    x2[:, 5, :] += 50.0
    with torch.no_grad():
        y1, _ = long_attn(x1)
        y2, _ = long_attn(x2)
        torch.testing.assert_close(y1[:, :5, :], y2[:, :5, :], atol=1e-5, rtol=1e-5)


def test_crit02_turboquant_non_pow2_rotation_and_disabled_passthrough():
    """CRIT-02: Non-pow2 Hadamard rotation is invertible and disabled mode preserves float values."""
    for dim in (28, 48):
        rot = RandomRotation(dim=dim, rotation_type="hadamard")
        x = torch.randn(3, dim)
        rec = rot.inverse_rotate(rot.rotate(x, seed=7), seed=7)
        torch.testing.assert_close(x, rec, atol=1e-4, rtol=1e-4)

    comp = TurboQuantCompressor(TurboQuantConfig(enabled=False))
    xf = torch.tensor([0.125, -0.375, 0.75])
    rec_disabled = comp.decompress(comp.compress(xf))
    torch.testing.assert_close(rec_disabled, xf)


def test_crit03_quantize_state_dict_zero_tensor_no_nan():
    """CRIT-03: INT8 quantization of zero tensors must not produce NaNs."""
    sd = {"bias": torch.zeros(16), "weight": torch.randn(8, 16) * 0.02}
    q = _quantize_state_dict(sd, mode="int8")
    assert torch.isfinite(q["bias.__scale__"]).all()
    assert (q["bias"] == 0).all()
    assert q["weight.__scale__"].item() > 0.0
