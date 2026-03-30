#!/usr/bin/env python3
r"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #inference #python #source_code #src/inference/cache.py
**Category:** Source Code
**Status:** Active
"""









# Cache

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:01
# Author:** ImpressionCore Team
# Tags:** #inference #python #source_code #src/inference/cache.py
# Category:** Source Code
# Status:** Active

"""
KV cache with prefix reuse for ImpressionCore-b1.

Supports text and image modalities.
"""
from typing import Any


class KVCacher:
    """
    Key-Value cache for efficient inference with prefix reuse.
    Supports both text and image modalities.
    """
    def __init__(self):
        self.cache = {}

    def get(self, key: Any) -> Any:
        """
        Retrieve cached value by key.
        Args:
            key (Any): Cache key (e.g., tokenized prompt hash).
        Returns:
            Any: Cached value or None.
        """
        return self.cache.get(key, None)

    def set(self, key: Any, value: Any):
        """
        Set cache value for key.
        Args:
            key (Any): Cache key.
            value (Any): Value to cache.
        """
        self.cache[key] = value

    def clear(self):
        """
        Clear the cache.
        """
        self.cache.clear()


def create_kv_cache(strategy: str = "simple", **kwargs):
    """Factory function to create a KV cache backend.

    Args:
        strategy: Cache strategy selector.
            "simple" — Legacy dict-based KVCacher.
            "turboquant" — TurboQuant-compressed tensor cache.
            "turboquant_3.5bit" — Alias for turboquant at 3.5 bits.
            "turboquant_2.5bit" — Turboquant at 2.5 bits (aggressive).
            "int8" — Falls back to simple cache (INT8 not yet tensor-level).
            "none" — No caching (returns simple cache).
        **kwargs: Forwarded to the cache constructor.

    Returns:
        A cache instance (KVCacher or TurboQuantKVCache).
    """
    turboquant_strategies = {"turboquant", "turboquant_3.5bit", "turboquant_2.5bit"}

    if strategy in turboquant_strategies:
        from src.core.quantization.turboquant_config import TurboQuantConfig
        from src.inference.turboquant_kv_cache import TurboQuantKVCache

        bits = 3.5
        if strategy == "turboquant_2.5bit":
            bits = 2.5

        config = TurboQuantConfig(
            bits_per_channel=kwargs.pop("bits_per_channel", bits),
            use_qjl_residual=kwargs.pop("use_qjl_residual", True),
            rotation_type=kwargs.pop("rotation_type", "hadamard"),
        )
        return TurboQuantKVCache(config=config, **kwargs)

    # Default: simple dict-based cache
    return KVCacher()
