"""Tests for src.core.utils.safe_load — the safe torch.load wrapper."""
from __future__ import annotations

from pathlib import Path

import pytest
import torch


class TestSafeLoad:
    """Verify safe_torch_load correctly loads checkpoints with weights_only=True."""

    def test_loads_state_dict(self, tmp_path: Path):
        from src.core.utils.safe_load import safe_torch_load

        data = {"layer.weight": torch.randn(4, 4), "layer.bias": torch.zeros(4)}
        path = tmp_path / "weights.pt"
        torch.save(data, path)

        loaded = safe_torch_load(path)
        assert "layer.weight" in loaded
        assert torch.equal(loaded["layer.bias"], torch.zeros(4))

    def test_loads_to_cpu_by_default(self, tmp_path: Path):
        from src.core.utils.safe_load import safe_torch_load

        data = {"w": torch.tensor([1.0, 2.0, 3.0])}
        path = tmp_path / "cpu_test.pt"
        torch.save(data, path)

        loaded = safe_torch_load(path)
        assert loaded["w"].device.type == "cpu"

    def test_nonexistent_file_raises(self, tmp_path: Path):
        from src.core.utils.safe_load import safe_torch_load

        with pytest.raises((FileNotFoundError, RuntimeError)):
            safe_torch_load(tmp_path / "nonexistent.pt")


class TestCorsConfig:
    """Verify CORS origin configuration."""

    def test_default_origins(self, clean_env):
        from src.core.config.cors_config import get_allowed_origins

        origins = get_allowed_origins()
        assert isinstance(origins, list)
        assert len(origins) > 0
        # Defaults should include localhost variants
        assert any("localhost" in o for o in origins)

    def test_env_override(self, monkeypatch):
        monkeypatch.setenv("IMPRESSIONCORE_ALLOWED_ORIGINS", "https://example.com,https://app.example.com")

        from importlib import reload

        import src.core.config.cors_config as cors_mod
        reload(cors_mod)

        origins = cors_mod.get_allowed_origins()
        assert "https://example.com" in origins
        assert "https://app.example.com" in origins
