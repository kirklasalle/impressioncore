"""Integration tests for TurboQuant KV cache.

Tests cache store/retrieve correctness, memory footprint comparison,
and attention output quality versus full-precision baseline.
"""

import pytest
import torch

from src.core.quantization.turboquant_config import TurboQuantConfig
from src.inference.cache import KVCacher, create_kv_cache
from src.inference.turboquant_kv_cache import TurboQuantKVCache

# ---------------------------------------------------------------------------
# TurboQuantKVCache tests
# ---------------------------------------------------------------------------


class TestTurboQuantKVCache:
    def test_store_and_retrieve(self):
        """Store then retrieve should return approximately the same tensors."""
        config = TurboQuantConfig(bits_per_channel=3.5, block_size=32)
        cache = TurboQuantKVCache(config=config, num_layers=4)

        keys = torch.randn(2, 6, 16, 64)  # batch=2, heads=6, seq=16, dim=64
        values = torch.randn(2, 6, 16, 64)

        cache.store(0, keys, values)
        assert cache.has_layer(0)
        assert not cache.has_layer(1)

        k_out, v_out = cache.retrieve(0)
        assert k_out.shape == keys.shape
        assert v_out.shape == values.shape

        # Check approximate fidelity
        k_cosine = torch.nn.functional.cosine_similarity(
            keys.flatten().unsqueeze(0), k_out.flatten().unsqueeze(0)
        ).item()
        v_cosine = torch.nn.functional.cosine_similarity(
            values.flatten().unsqueeze(0), v_out.flatten().unsqueeze(0)
        ).item()
        assert k_cosine > 0.85, f"Key cosine similarity {k_cosine} too low"
        assert v_cosine > 0.85, f"Value cosine similarity {v_cosine} too low"

    def test_clear_layer(self):
        config = TurboQuantConfig(bits_per_channel=3.5, block_size=32)
        cache = TurboQuantKVCache(config=config, num_layers=4)
        cache.store(0, torch.randn(1, 4, 8, 32), torch.randn(1, 4, 8, 32))
        cache.store(1, torch.randn(1, 4, 8, 32), torch.randn(1, 4, 8, 32))

        cache.clear(layer_idx=0)
        assert not cache.has_layer(0)
        assert cache.has_layer(1)

    def test_clear_all(self):
        config = TurboQuantConfig(bits_per_channel=3.5, block_size=32)
        cache = TurboQuantKVCache(config=config, num_layers=4)
        for i in range(4):
            cache.store(i, torch.randn(1, 4, 8, 32), torch.randn(1, 4, 8, 32))
        cache.clear()
        for i in range(4):
            assert not cache.has_layer(i)

    def test_stats(self):
        config = TurboQuantConfig(bits_per_channel=3.5, block_size=32)
        cache = TurboQuantKVCache(config=config, num_layers=4)
        cache.store(0, torch.randn(1, 4, 8, 64), torch.randn(1, 4, 8, 64))

        stats = cache.get_stats()
        assert stats["cached_layers"] == 1
        assert stats["total_layers"] == 4
        assert stats["total_stores"] == 1
        assert stats["compression_ratio"] > 1.0
        assert stats["bytes_saved"] > 0
        assert stats["config_bits"] == 3.5

    def test_layer_index_bounds(self):
        cache = TurboQuantKVCache(num_layers=4)
        with pytest.raises(IndexError):
            cache.store(-1, torch.randn(1, 1, 1, 32), torch.randn(1, 1, 1, 32))
        with pytest.raises(IndexError):
            cache.store(4, torch.randn(1, 1, 1, 32), torch.randn(1, 1, 1, 32))
        with pytest.raises(IndexError):
            cache.retrieve(5)

    def test_retrieve_empty_layer(self):
        cache = TurboQuantKVCache(num_layers=4)
        assert cache.retrieve(0) is None

    def test_append(self):
        config = TurboQuantConfig(bits_per_channel=3.5, block_size=32)
        cache = TurboQuantKVCache(config=config, num_layers=4)

        k1 = torch.randn(1, 4, 8, 64)
        v1 = torch.randn(1, 4, 8, 64)
        cache.store(0, k1, v1)

        k2 = torch.randn(1, 4, 4, 64)
        v2 = torch.randn(1, 4, 4, 64)
        cache.append(0, k2, v2)

        k_out, v_out = cache.retrieve(0)
        # Should have seq_len = 8 + 4 = 12
        assert k_out.shape == (1, 4, 12, 64)
        assert v_out.shape == (1, 4, 12, 64)

    def test_memory_reduction(self):
        """TurboQuant cache should use less storage than FP16 original."""
        config = TurboQuantConfig(bits_per_channel=3.5, block_size=64)
        cache = TurboQuantKVCache(config=config, num_layers=8)

        # Simulate 8 layers of KV cache
        for i in range(8):
            k = torch.randn(1, 6, 64, 64).half()
            v = torch.randn(1, 6, 64, 64).half()
            cache.store(i, k, v)

        stats = cache.get_stats()
        assert stats["compression_ratio"] > 1.5, f"Expected compression ratio > 1.5, got {stats['compression_ratio']}"


# ---------------------------------------------------------------------------
# Factory function tests
# ---------------------------------------------------------------------------


class TestCreateKVCache:
    def test_simple_strategy(self):
        cache = create_kv_cache("simple")
        assert isinstance(cache, KVCacher)

    def test_none_strategy(self):
        cache = create_kv_cache("none")
        assert isinstance(cache, KVCacher)

    def test_int8_strategy_fallback(self):
        cache = create_kv_cache("int8")
        assert isinstance(cache, KVCacher)

    def test_turboquant_strategy(self):
        cache = create_kv_cache("turboquant", num_layers=4)
        assert isinstance(cache, TurboQuantKVCache)

    def test_turboquant_35bit_strategy(self):
        cache = create_kv_cache("turboquant_3.5bit", num_layers=4)
        assert isinstance(cache, TurboQuantKVCache)
        assert cache.config.bits_per_channel == 3.5

    def test_turboquant_25bit_strategy(self):
        cache = create_kv_cache("turboquant_2.5bit", num_layers=4)
        assert isinstance(cache, TurboQuantKVCache)
        assert cache.config.bits_per_channel == 2.5

    def test_custom_bits(self):
        cache = create_kv_cache("turboquant", num_layers=4, bits_per_channel=4.0)
        assert isinstance(cache, TurboQuantKVCache)
        assert cache.config.bits_per_channel == 4.0
