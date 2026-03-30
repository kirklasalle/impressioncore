"""TurboQuant memory benchmark for ImpressionCore B3.

Measures actual memory savings from TurboQuant KV cache compression
at various context lengths, targeting GTX 1050 Ti (4GB VRAM).

Usage:
    python src/benchmarks/turboquant_memory_benchmark.py
"""

import logging
import sys
import time

import torch

from src.core.quantization.turboquant import TurboQuantCompressor
from src.core.quantization.turboquant_config import TurboQuantConfig
from src.inference.turboquant_kv_cache import TurboQuantKVCache

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def benchmark_compression_quality(dim: int = 64, seq_lengths: list[int] | None = None):
    """Measure compression quality across different sequence lengths."""
    if seq_lengths is None:
        seq_lengths = [256, 1024, 4096, 16384]

    configs = {
        "3.5-bit (quality-neutral)": TurboQuantConfig(bits_per_channel=3.5, block_size=64),
        "2.5-bit (aggressive)": TurboQuantConfig(bits_per_channel=2.5, block_size=64),
        "3.5-bit no-QJL": TurboQuantConfig(bits_per_channel=3.5, use_qjl_residual=False, block_size=64),
    }

    logger.info("=" * 80)
    logger.info("TurboQuant Compression Quality Benchmark")
    logger.info("=" * 80)
    logger.info(f"  Head dimension: {dim}")
    logger.info(f"  Configs: {list(configs.keys())}")
    logger.info("")

    for name, config in configs.items():
        compressor = TurboQuantCompressor(config)
        logger.info(f"--- {name} ---")

        for seq_len in seq_lengths:
            x = torch.randn(1, 6, seq_len, dim)  # batch=1, heads=6

            t0 = time.perf_counter()
            compressed = compressor.compress(x)
            t_compress = time.perf_counter() - t0

            t0 = time.perf_counter()
            x_rec = compressor.decompress(compressed)
            t_decompress = time.perf_counter() - t0

            mse = (x - x_rec).pow(2).mean().item()
            cosine = torch.nn.functional.cosine_similarity(
                x.flatten().unsqueeze(0), x_rec.flatten().unsqueeze(0)
            ).item()
            ratio = compressed.compression_ratio

            logger.info(
                f"  seq={seq_len:>6d}  |  ratio={ratio:.2f}x  |  "
                f"MSE={mse:.6f}  |  cosine={cosine:.4f}  |  "
                f"compress={t_compress*1000:.1f}ms  |  decompress={t_decompress*1000:.1f}ms"
            )
        logger.info("")


def benchmark_kv_cache_memory(
    num_layers: int = 12,
    num_heads: int = 6,
    head_dim: int = 64,
    seq_lengths: list[int] | None = None,
):
    """Measure KV cache memory with and without TurboQuant."""
    if seq_lengths is None:
        seq_lengths = [256, 1024, 4096, 16384]

    logger.info("=" * 80)
    logger.info("KV Cache Memory Benchmark (B3 39M config)")
    logger.info("=" * 80)
    logger.info(f"  Layers: {num_layers}, Heads: {num_heads}, Head dim: {head_dim}")
    logger.info(f"  d_model: {num_heads * head_dim}")
    logger.info("")
    logger.info(f"  {'Seq Len':>8s}  |  {'FP16 (MB)':>10s}  |  {'TQ 3.5b (MB)':>13s}  |  "
                f"{'TQ 2.5b (MB)':>13s}  |  {'Ratio 3.5':>10s}  |  {'Ratio 2.5':>10s}  |  "
                f"{'Saved 3.5 (MB)':>15s}")
    logger.info("-" * 100)

    config_35 = TurboQuantConfig(bits_per_channel=3.5, block_size=64)
    config_25 = TurboQuantConfig(bits_per_channel=2.5, block_size=64)

    for seq_len in seq_lengths:
        # FP16 baseline: 2 (K+V) × num_layers × batch × heads × seq × dim × 2 bytes
        fp16_bytes = 2 * num_layers * 1 * num_heads * seq_len * head_dim * 2
        fp16_mb = fp16_bytes / (1024 * 1024)

        # TurboQuant 3.5-bit
        cache_35 = TurboQuantKVCache(config=config_35, num_layers=num_layers)
        for layer in range(num_layers):
            k = torch.randn(1, num_heads, seq_len, head_dim).half()
            v = torch.randn(1, num_heads, seq_len, head_dim).half()
            cache_35.store(layer, k, v)

        stats_35 = cache_35.get_stats()
        tq35_mb = stats_35["compressed_bytes"] / (1024 * 1024)
        ratio_35 = stats_35["compression_ratio"]
        saved_35_mb = (stats_35["original_bytes"] - stats_35["compressed_bytes"]) / (1024 * 1024)

        # TurboQuant 2.5-bit
        cache_25 = TurboQuantKVCache(config=config_25, num_layers=num_layers)
        for layer in range(num_layers):
            k = torch.randn(1, num_heads, seq_len, head_dim).half()
            v = torch.randn(1, num_heads, seq_len, head_dim).half()
            cache_25.store(layer, k, v)

        stats_25 = cache_25.get_stats()
        tq25_mb = stats_25["compressed_bytes"] / (1024 * 1024)
        ratio_25 = stats_25["compression_ratio"]

        logger.info(
            f"  {seq_len:>8d}  |  {fp16_mb:>10.2f}  |  {tq35_mb:>13.2f}  |  "
            f"{tq25_mb:>13.2f}  |  {ratio_35:>10.2f}x  |  {ratio_25:>10.2f}x  |  "
            f"{saved_35_mb:>15.2f}"
        )

    logger.info("")
    logger.info("GTX 1050 Ti budget: 4096 MB total VRAM")
    logger.info("  ~3500 MB available after model weights and overhead")
    logger.info("")


def benchmark_attention_speedup(
    num_heads: int = 6,
    head_dim: int = 64,
    seq_len: int = 4096,
    num_iterations: int = 20,
):
    """Benchmark attention computation time with FP16 vs compressed KV."""
    logger.info("=" * 80)
    logger.info("Attention Computation Benchmark")
    logger.info("=" * 80)

    batch = 1
    embed_dim = num_heads * head_dim

    config = TurboQuantConfig(bits_per_channel=3.5, block_size=64)
    compressor = TurboQuantCompressor(config)

    q = torch.randn(batch, num_heads, seq_len, head_dim)
    k = torch.randn(batch, num_heads, seq_len, head_dim)
    v = torch.randn(batch, num_heads, seq_len, head_dim)

    # FP16 baseline attention time
    times_fp16 = []
    for _ in range(num_iterations):
        t0 = time.perf_counter()
        attn = torch.matmul(q, k.transpose(-2, -1)) * (head_dim ** -0.5)
        attn = torch.softmax(attn, dim=-1)
        _ = torch.matmul(attn, v)
        times_fp16.append(time.perf_counter() - t0)

    # TurboQuant: compress K/V, decompress, then attention
    compressed_k = compressor.compress(k)
    compressed_v = compressor.compress(v)

    times_tq = []
    for _ in range(num_iterations):
        t0 = time.perf_counter()
        k_dec = compressor.decompress(compressed_k)
        v_dec = compressor.decompress(compressed_v)
        attn = torch.matmul(q, k_dec.transpose(-2, -1)) * (head_dim ** -0.5)
        attn = torch.softmax(attn, dim=-1)
        _ = torch.matmul(attn, v_dec)
        times_tq.append(time.perf_counter() - t0)

    avg_fp16 = sum(times_fp16[2:]) / len(times_fp16[2:]) * 1000  # skip warmup
    avg_tq = sum(times_tq[2:]) / len(times_tq[2:]) * 1000

    logger.info(f"  Seq length: {seq_len}, Heads: {num_heads}, Head dim: {head_dim}")
    logger.info(f"  FP16 attention:      {avg_fp16:.2f} ms")
    logger.info(f"  TurboQuant attention: {avg_tq:.2f} ms (includes decompress)")
    logger.info(f"  Overhead:            {avg_tq - avg_fp16:.2f} ms")
    logger.info(f"  Memory saved: {compressed_k.compression_ratio:.2f}x for K, "
                f"{compressed_v.compression_ratio:.2f}x for V")
    logger.info("")


if __name__ == "__main__":
    benchmark_compression_quality()
    benchmark_kv_cache_memory()
    benchmark_attention_speedup()
    logger.info("Benchmark complete.")
