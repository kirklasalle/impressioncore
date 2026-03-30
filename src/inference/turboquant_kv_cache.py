"""TurboQuant-compressed KV cache for ImpressionCore B3 inference.

Provides a tensor-level KV cache that compresses keys and values using
TurboQuant (arXiv:2504.19874), achieving ~4-6x memory reduction versus FP16
with zero accuracy degradation at 3.5 bits per channel.

Designed as a drop-in replacement alongside the existing KVCacher, selectable
via the factory function in src/inference/cache.py.
"""

import logging
from dataclasses import dataclass

import torch

from src.core.quantization.turboquant import CompressedTensor, TurboQuantCompressor
from src.core.quantization.turboquant_config import TurboQuantConfig

logger = logging.getLogger(__name__)


@dataclass
class CacheStats:
    """Running statistics for KV cache memory usage."""

    total_stores: int = 0
    total_original_bytes: int = 0
    total_compressed_bytes: int = 0

    @property
    def compression_ratio(self) -> float:
        if self.total_compressed_bytes == 0:
            return 0.0
        return self.total_original_bytes / self.total_compressed_bytes

    @property
    def bytes_saved(self) -> int:
        return self.total_original_bytes - self.total_compressed_bytes


class TurboQuantKVCache:
    """TurboQuant-compressed KV cache for efficient inference.

    Stores key and value tensors in compressed form per layer, decompressing
    on demand. Transparently handles compression/decompression so the
    attention layer sees full-precision tensors.

    Args:
        config: TurboQuantConfig controlling compression parameters.
        num_layers: Number of transformer layers to cache for.
    """

    def __init__(self, config: TurboQuantConfig | None = None, num_layers: int = 32):
        self.config = config or TurboQuantConfig()
        self.num_layers = num_layers
        self.compressor = TurboQuantCompressor(self.config)
        self.stats = CacheStats()

        # Per-layer storage: list of (compressed_key, compressed_value) or None
        self._cache: list[tuple[CompressedTensor, CompressedTensor] | None] = [None] * num_layers

    def store(self, layer_idx: int, keys: torch.Tensor, values: torch.Tensor) -> None:
        """Compress and store key/value tensors for a layer.

        Args:
            layer_idx: Transformer layer index.
            keys: Key tensor, typically [batch, heads, seq, head_dim] or [batch, seq, dim].
            values: Value tensor, same shape as keys.
        """
        if layer_idx < 0 or layer_idx >= self.num_layers:
            raise IndexError(f"layer_idx {layer_idx} out of range [0, {self.num_layers})")

        compressed_k = self.compressor.compress(keys)
        compressed_v = self.compressor.compress(values)
        self._cache[layer_idx] = (compressed_k, compressed_v)

        # Update stats
        self.stats.total_stores += 1
        self.stats.total_original_bytes += compressed_k.numel_original() + compressed_v.numel_original()
        self.stats.total_compressed_bytes += compressed_k.numel_compressed() + compressed_v.numel_compressed()

    def retrieve(self, layer_idx: int) -> tuple[torch.Tensor, torch.Tensor] | None:
        """Decompress and return key/value tensors for a layer.

        Args:
            layer_idx: Transformer layer index.

        Returns:
            Tuple of (keys, values) decompressed to original dtype, or None
            if nothing is cached for this layer.
        """
        if layer_idx < 0 or layer_idx >= self.num_layers:
            raise IndexError(f"layer_idx {layer_idx} out of range [0, {self.num_layers})")

        entry = self._cache[layer_idx]
        if entry is None:
            return None

        compressed_k, compressed_v = entry
        keys = self.compressor.decompress(compressed_k)
        values = self.compressor.decompress(compressed_v)
        return keys, values

    def has_layer(self, layer_idx: int) -> bool:
        """Check if a layer has cached KV data."""
        return 0 <= layer_idx < self.num_layers and self._cache[layer_idx] is not None

    def clear(self, layer_idx: int | None = None) -> None:
        """Clear cached data.

        Args:
            layer_idx: If provided, clear only that layer. Otherwise clear all.
        """
        if layer_idx is not None:
            if 0 <= layer_idx < self.num_layers:
                self._cache[layer_idx] = None
        else:
            self._cache = [None] * self.num_layers

    def get_stats(self) -> dict:
        """Return cache statistics for monitoring."""
        cached_layers = sum(1 for entry in self._cache if entry is not None)
        return {
            "cached_layers": cached_layers,
            "total_layers": self.num_layers,
            "total_stores": self.stats.total_stores,
            "compression_ratio": self.stats.compression_ratio,
            "bytes_saved": self.stats.bytes_saved,
            "original_bytes": self.stats.total_original_bytes,
            "compressed_bytes": self.stats.total_compressed_bytes,
            "config_bits": self.config.bits_per_channel,
            "config_qjl": self.config.use_qjl_residual,
        }

    def append(self, layer_idx: int, new_keys: torch.Tensor, new_values: torch.Tensor) -> None:
        """Append new KV pairs to an existing layer cache (for autoregressive generation).

        Decompresses existing cache, concatenates new tokens, and re-compresses.

        Args:
            layer_idx: Transformer layer index.
            new_keys: New key tensor to append along the sequence dimension.
            new_values: New value tensor to append along the sequence dimension.
        """
        existing = self.retrieve(layer_idx)
        if existing is None:
            self.store(layer_idx, new_keys, new_values)
            return

        old_keys, old_values = existing
        # Concatenate along sequence dimension (dim=-2 for [batch, heads, seq, dim])
        seq_dim = -2 if old_keys.dim() >= 3 else -1
        combined_keys = torch.cat([old_keys, new_keys], dim=seq_dim)
        combined_values = torch.cat([old_values, new_values], dim=seq_dim)
        self.store(layer_idx, combined_keys, combined_values)
