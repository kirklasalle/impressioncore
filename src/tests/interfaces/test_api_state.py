"""Unit tests for src.interfaces.api_state utilities."""

import numpy as np
import pytest
from src.interfaces.api_state import sanitize_numpy, PRIME_DIRECTIVE_LAWS, AUDIO_CONFIG


class TestSanitizeNumpy:
    def test_plain_dict_unchanged(self):
        data = {"a": 1, "b": "hello"}
        assert sanitize_numpy(data) == data

    def test_numpy_int_converted(self):
        val = np.int64(42)
        result = sanitize_numpy(val)
        assert result == 42
        assert isinstance(result, int)

    def test_numpy_float_converted(self):
        val = np.float32(3.14)
        result = sanitize_numpy(val)
        assert abs(result - 3.14) < 0.01
        assert isinstance(result, float)

    def test_numpy_array_to_list(self):
        arr = np.array([1, 2, 3])
        result = sanitize_numpy(arr)
        assert result == [1, 2, 3]
        assert isinstance(result, list)

    def test_nested_dict_with_numpy(self):
        data = {"scores": np.array([0.1, 0.9]), "count": np.int32(5)}
        result = sanitize_numpy(data)
        assert result["count"] == 5
        assert isinstance(result["scores"], list)

    def test_bytes_converted_to_none(self):
        assert sanitize_numpy(b"binary_data") is None
        assert sanitize_numpy(bytearray(b"more")) is None

    def test_list_with_numpy(self):
        data = [np.float64(1.0), np.int32(2), "text"]
        result = sanitize_numpy(data)
        assert result == [1.0, 2, "text"]

    def test_tuple_support(self):
        data = (np.int64(1), np.int64(2))
        result = sanitize_numpy(data)
        assert result == [1, 2]


class TestApiStateConstants:
    def test_prime_directive_has_10_laws(self):
        assert len(PRIME_DIRECTIVE_LAWS) == 10

    def test_each_law_has_name_and_text(self):
        for law_id, law in PRIME_DIRECTIVE_LAWS.items():
            assert "name" in law, f"Law {law_id} missing 'name'"
            assert "text" in law, f"Law {law_id} missing 'text'"
            assert len(law["text"]) > 20, f"Law {law_id} text too short"

    def test_audio_config_defaults(self):
        assert AUDIO_CONFIG["active"] is True
        assert 0 <= AUDIO_CONFIG["gain_master"] <= 1.0
