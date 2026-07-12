"""Unit tests for src.core.config.data_paths."""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from src.core.config import data_paths


class TestDataPaths:
    """Tests for the data_paths module functions."""

    def test_verify_data_drive_present(self):
        """verify_data_drive returns True when data drive and required directories exist."""
        with patch.object(Path, "exists", return_value=True):
            assert data_paths.verify_data_drive() is True

    def test_verify_data_drive_missing_drive(self):
        """verify_data_drive returns False when the data drive does not exist."""
        def mock_exists(self_path: Path) -> bool:
            # Simulate drive itself missing
            if str(self_path).replace("\\", "/").startswith("F:/"):
                return False
            return True

        with patch.object(Path, "exists", mock_exists):
            assert data_paths.verify_data_drive() is False

    def test_verify_data_drive_missing_subdir(self):
        """verify_data_drive returns False when required subdirs are missing."""
        def mock_exists(self_path: Path) -> bool:
            # Simulate models folder missing
            if "models" in str(self_path):
                return False
            return True

        with patch.object(Path, "exists", mock_exists):
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
