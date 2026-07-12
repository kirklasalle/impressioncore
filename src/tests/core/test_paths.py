"""Unit tests for src.core.config.paths."""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from src.core.config.paths import PathConfig


class TestPathConfig:
    """Tests for the PathConfig module class methods."""

    def test_get_model_dir_success(self):
        """get_model_dir returns path when directory exists."""
        with patch.object(Path, "exists", return_value=True):
            model_dir = PathConfig.get_model_dir()
            assert isinstance(model_dir, Path)
            assert "models/production" in str(model_dir).replace("\\", "/")

    def test_get_model_dir_failure(self):
        """get_model_dir raises RuntimeError when directory does not exist."""
        with patch.object(Path, "exists", return_value=False):
            with pytest.raises(RuntimeError) as exc_info:
                PathConfig.get_model_dir()
            assert "Critical Path Missing" in str(exc_info.value)

    def test_validate_environment_success(self):
        """validate_environment completes without error when all paths exist."""
        with patch.object(Path, "exists", return_value=True):
            # Should not raise any exceptions
            PathConfig.validate_environment()

    def test_validate_environment_missing_drive(self):
        """validate_environment raises RuntimeError if the data drive does not exist."""
        def mock_exists(self_path: Path) -> bool:
            # Simulate drive missing
            if str(self_path).replace("\\", "/").startswith("F:/"):
                return False
            return True

        with patch.object(Path, "exists", mock_exists):
            with pytest.raises(RuntimeError) as exc_info:
                PathConfig.validate_environment()
            assert "Critical Path Missing" in str(exc_info.value)
