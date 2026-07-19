"""Tests for checkpoint browser metadata and background hashing logic.

Covers WS3 Task 3 and WS5 quality gate.
"""
import os
import time
import pytest
import shutil
import tempfile
from unittest.mock import patch, MagicMock

from src.interfaces.web.routes.builder import (
    _load_checkpoint_meta,
    _save_checkpoint_meta,
    _calculate_hash_background,
    _infer_offering_from_path,
)


@pytest.fixture
def temp_meta_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        meta_file = os.path.join(tmpdir, "meta.json")
        with patch("src.interfaces.web.routes.builder._CHECKPOINT_META_FILE", meta_file):
            yield meta_file


def test_meta_load_save(temp_meta_file):
    # Empty meta at start
    assert _load_checkpoint_meta() == {}

    # Save meta
    test_data = {"test_path": {"sha256": "fakehash", "mtime": 123, "size": 456}}
    _save_checkpoint_meta(test_data)

    # Load back
    assert _load_checkpoint_meta() == test_data


def test_infer_offering_from_path():
    assert _infer_offering_from_path("b3_hope_v1_step_1000.pt")["id"] == "b1_39m"
    assert _infer_offering_from_path("b2_50m_insight.pt")["id"] == "b2_50m"
    assert _infer_offering_from_path("kd_sft_phase2_checkpoint.pt")["id"] == "b3_504m"
    assert _infer_offering_from_path("step_5000.pt")["id"] == "b3_504m"
    assert _infer_offering_from_path("random_model.pt") is None


def test_calculate_hash_background(temp_meta_file):
    # Create a small dummy file to hash
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(b"ImpressionCore Checkpoint Test Data")
        fpath = f.name

    try:
        stat = os.stat(fpath)
        mtime = stat.st_mtime
        size = stat.st_size

        # Trigger background hashing
        _calculate_hash_background(fpath, mtime, size)

        # Wait for thread to finish (max 2 seconds)
        retries = 20
        finished = False
        while retries > 0:
            meta = _load_checkpoint_meta()
            if fpath in meta:
                finished = True
                break
            time.sleep(0.1)
            retries -= 1

        assert finished, "Background hashing thread did not complete in time"
        assert meta[fpath]["sha256"] == "5efd0e24be52877d5525d5413301cce6254a81712c6c4b4a8db499ab0cb4511a"
        assert meta[fpath]["mtime"] == mtime
        assert meta[fpath]["size"] == size

    finally:
        if os.path.exists(fpath):
            os.remove(fpath)
