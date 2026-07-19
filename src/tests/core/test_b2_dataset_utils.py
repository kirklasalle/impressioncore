"""Unit tests for B2 dataset splitting and counting utilities."""

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.core.utils.auto_split_b2_dataset import assign_and_move, get_all_files, get_split_path, move_files
from src.core.utils.count_b2_dataset_files import count_and_list


def test_get_all_files():
    with patch("src.core.utils.auto_split_b2_dataset.glob", return_value=["file1.avi"]) as mock_glob:
        files = get_all_files("video")
        assert len(files) == 4  # because EXTS["video"] has 4 extensions, so glob is called 4 times
        mock_glob.assert_called()


def test_get_split_path():
    path = get_split_path("F:/b2_datasets/raw/video/sample.avi", "train", "video")
    assert path.replace("\\", "/") == "F:/b2_datasets/train/video/sample.avi"


def test_move_files():
    with patch("os.makedirs") as mock_makedirs:
        with patch("shutil.move") as mock_move:
            move_files(["F:/b2_datasets/raw/video/sample.avi"], "train", "video")
            mock_makedirs.assert_called_once()
            mock_move.assert_called_once()


def test_assign_and_move():
    # Mocking get_all_files to return some files
    files = ["F:/b2_datasets/video/1.avi", "F:/b2_datasets/video/2.avi"]
    with patch("src.core.utils.auto_split_b2_dataset.get_all_files", return_value=files):
        with patch("src.core.utils.auto_split_b2_dataset.move_files") as mock_move:
            assign_and_move("video")
            # Should have called move_files
            mock_move.assert_called()


def test_count_and_list():
    # Test count_and_list with mocked exists and rglob methods
    mock_file = MagicMock()
    mock_file.is_file.return_value = True
    mock_file.relative_to.return_value = Path("train/video/sample.avi")

    with patch.object(Path, "exists", return_value=True):
        with patch.object(Path, "rglob", return_value=[mock_file]):
            with patch("builtins.print") as mock_print:
                count_and_list()
                mock_print.assert_any_call("\n=== Split: train ===")
                mock_print.assert_any_call("  video: 1 files")


def test_main():
    from src.core.utils.auto_split_b2_dataset import MODALITIES, main
    with patch("src.core.utils.auto_split_b2_dataset.assign_and_move") as mock_assign:
        main()
        assert mock_assign.call_count == len(MODALITIES)


def test_count_and_list_missing():
    with patch.object(Path, "exists", return_value=False):
        with patch("builtins.print") as mock_print:
            count_and_list()
            # Should have printed MISSING warning
            mock_print.assert_any_call("  [MISSING] video folder: F:\\b2_datasets\\train\\video")
