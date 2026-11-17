"""Unit tests for src.core.config.data_paths."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from src.core.config import data_paths


class TestDataPaths:
    """Tests for the data_paths module functions."""

    def test_verify_data_drive_present(self):
        """verify_data_drive returns True when data drive and required directories exist."""
        with patch.object(Path, "is_dir", return_value=True):
            assert data_paths.verify_data_drive() is True

    def test_verify_data_drive_missing_drive(self):
        """verify_data_drive returns False when the data drive does not exist."""
        with patch.object(Path, "is_dir", return_value=False):
            assert data_paths.verify_data_drive() is False

    def test_verify_data_drive_missing_subdir(self):
        """verify_data_drive returns False when required subdirs are missing."""
        def mock_is_dir(self_path: Path) -> bool:
            # Simulate models folder missing
            if "models" in str(self_path):
                return False
            return True

        with patch.object(Path, "is_dir", mock_is_dir):
            assert data_paths.verify_data_drive() is False

    def test_enforce_data_drive_success(self):
        """enforce_data_drive does not raise an error when drive is verified."""
        with patch("src.core.config.data_paths.verify_data_drive", return_value=True):
            # Should run without error
            data_paths.enforce_data_drive()

    def test_enforce_data_drive_failure(self):
        """enforce_data_drive raises RuntimeError when drive is missing."""
        with patch("src.core.config.data_paths.verify_data_drive", return_value=False):
            with pytest.raises(RuntimeError) as exc_info:
                data_paths.enforce_data_drive()
            assert "Critical Failure" in str(exc_info.value)
            assert "Boot aborted" in str(exc_info.value)
            assert "IMPRESSIONCORE_DATA_DRIVE" in str(exc_info.value)
            assert str(data_paths.MODELS_ROOT) in str(exc_info.value)
            assert str(data_paths.DATA_ROOT) in str(exc_info.value)

    @pytest.mark.parametrize("file_name", ["models", "data"])
    def test_verify_data_drive_rejects_files(self, tmp_path, file_name):
        """Files must not pass validation as required storage directories."""
        for name in ("models", "data"):
            path = tmp_path / name
            if name == file_name:
                path.touch()
            else:
                path.mkdir()
        with patch.multiple(
            data_paths,
            DATA_DRIVE=tmp_path,
            MODELS_ROOT=tmp_path / "models",
            DATA_ROOT=tmp_path / "data",
        ):
            assert data_paths.verify_data_drive() is False

    @pytest.mark.parametrize("storage_ready", [True, False])
    def test_storage_preflight_command(self, tmp_path, storage_ready):
        """The launcher command honors the override and reports storage failure."""
        if storage_ready:
            (tmp_path / "models").mkdir()
            (tmp_path / "data").mkdir()
        result = subprocess.run(
            [sys.executable, "-m", "src.core.config.data_paths"],
            cwd=Path(__file__).resolve().parents[3],
            env={**os.environ, "IMPRESSIONCORE_DATA_DRIVE": str(tmp_path)},
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == (0 if storage_ready else 1)
        assert str(tmp_path) in result.stderr
        if not storage_ready:
            assert "Reconnect the external drive" in result.stderr
            assert "Traceback" not in result.stderr
            assert list(tmp_path.iterdir()) == []

    def test_get_best_b3_checkpoint_found(self):
        """get_best_b3_checkpoint returns the path if it exists."""
        with patch.object(Path, "exists", return_value=True):
            best = data_paths.get_best_b3_checkpoint()
            assert best == data_paths.B3_HOPE_V1_WEIGHTS

    def test_get_best_b3_checkpoint_none(self):
        """get_best_b3_checkpoint returns None if no paths exist."""
        with patch.object(Path, "exists", return_value=False):
            best = data_paths.get_best_b3_checkpoint()
            assert best is None

    def test_get_b3_hope_config_exists(self):
        """get_b3_hope_config reads and returns config dict if it exists."""
        mock_data = '{"hidden_size": 512}'
        with patch.object(Path, "exists", return_value=True):
            with patch("builtins.open", mock_open(read_data=mock_data)):
                config = data_paths.get_b3_hope_config()
                assert config == {"hidden_size": 512}

    def test_get_b3_hope_config_none(self):
        """get_b3_hope_config returns None if config file does not exist."""
        with patch.object(Path, "exists", return_value=False):
            config = data_paths.get_b3_hope_config()
            assert config is None

    def test_get_checkpoint_inventory(self):
        """get_checkpoint_inventory returns correct dict of checkpoints."""
        mock_dir = MagicMock(spec=Path)
        mock_dir.is_dir.return_value = True
        mock_dir.name = "b3_full_training"
        
        mock_file1 = MagicMock(spec=Path)
        mock_file1.name = "checkpoint_epoch_14.pth"
        
        mock_dir.rglob.side_effect = lambda pat: [mock_file1] if pat == "*.pth" else []

        def mock_iterdir(self_path: Path):
            return [mock_dir]

        with patch.object(Path, "exists", return_value=True):
            with patch.object(Path, "iterdir", mock_iterdir):
                inventory = data_paths.get_checkpoint_inventory()
                assert inventory == {"b3_full_training": ["checkpoint_epoch_14.pth"]}

    def test_get_data_drive_summary(self):
        """get_data_drive_summary returns diagnostic dict."""
        with patch.object(Path, "exists", return_value=True):
            with patch.object(Path, "rglob", return_value=[]):
                with patch.object(Path, "iterdir", return_value=[]):
                    summary = data_paths.get_data_drive_summary()
                    assert summary["drive_available"] is True
                    assert summary["b3_hope_v1_available"] is True

from unittest.mock import MagicMock, mock_open

