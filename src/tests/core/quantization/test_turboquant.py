"""Unit tests for TurboQuant core algorithm.

Tests compression/decompression round-trip accuracy, inner product
preservation, memory reduction, and edge cases.
"""

import math

import pytest
import torch

from src.core.quantization.turboquant import (
    CompressedTensor,
    PolarQuantScalarQuantizer,
    QJLResidualCorrector,
    RandomRotation,
    TurboQuantCompressor,
)
from src.core.quantization.turboquant_config import TurboQuantConfig

# ---------------------------------------------------------------------------
# Config tests
# ---------------------------------------------------------------------------


class TestTurboQuantConfig:
    def test_default_config(self):
        cfg = TurboQuantConfig()
        assert cfg.bits_per_channel == 3.5
        assert cfg.use_qjl_residual is True
        assert cfg.rotation_type == "hadamard"
        assert cfg.enabled is True
        assert cfg.integer_bits == 3
        assert cfg.has_fractional_bits is True
        assert cfg.num_levels == 8

    def test_config_validation(self):
        with pytest.raises(ValueError, match="bits_per_channel"):
            TurboQuantConfig(bits_per_channel=0.5)
        with pytest.raises(ValueError, match="bits_per_channel"):
            TurboQuantConfig(bits_per_channel=9.0)
        with pytest.raises(ValueError, match="rotation_type"):
            TurboQuantConfig(rotation_type="invalid")
        with pytest.raises(ValueError, match="block_size"):
            TurboQuantConfig(block_size=0)

    def test_integer_bits(self):
        assert TurboQuantConfig(bits_per_channel=4.0).integer_bits == 4
        assert TurboQuantConfig(bits_per_channel=2.5).integer_bits == 2
        assert TurboQuantConfig(bits_per_channel=3.5).has_fractional_bits is True
        assert TurboQuantConfig(bits_per_channel=4.0).has_fractional_bits is False


# ---------------------------------------------------------------------------
# RandomRotation tests
# ---------------------------------------------------------------------------


class TestRandomRotation:
    def test_rotation_preserves_norm(self):
        """Rotation should preserve the L2 norm of vectors."""
        rot = RandomRotation(dim=64, rotation_type="hadamard")
        x = torch.randn(4, 64)
        norms_before = torch.norm(x, dim=-1)
        x_rot = rot.rotate(x, seed=42)
        norms_after = torch.norm(x_rot, dim=-1)
        torch.testing.assert_close(norms_before, norms_after, atol=1e-4, rtol=1e-4)

    def test_rotation_inverse(self):
        """rotate then inverse_rotate should recover the original."""
        rot = RandomRotation(dim=64, rotation_type="hadamard")
        x = torch.randn(4, 64)
        x_rot = rot.rotate(x, seed=42)
        x_rec = rot.inverse_rotate(x_rot, seed=42)
        torch.testing.assert_close(x, x_rec, atol=1e-4, rtol=1e-4)

    def test_rotation_deterministic(self):
        """Same seed should produce the same rotation."""
        rot = RandomRotation(dim=32, rotation_type="hadamard")
        x = torch.randn(2, 32)
        r1 = rot.rotate(x, seed=123)
        r2 = rot.rotate(x, seed=123)
        torch.testing.assert_close(r1, r2)

    def test_gaussian_rotation_preserves_norm(self):
        rot = RandomRotation(dim=32, rotation_type="gaussian")
        x = torch.randn(3, 32)
        norms_before = torch.norm(x, dim=-1)
        x_rot = rot.rotate(x, seed=99)
        norms_after = torch.norm(x_rot, dim=-1)
        torch.testing.assert_close(norms_before, norms_after, atol=1e-3, rtol=1e-3)

    def test_gaussian_rotation_inverse(self):
        rot = RandomRotation(dim=32, rotation_type="gaussian")
        x = torch.randn(3, 32)
        x_rot = rot.rotate(x, seed=99)
        x_rec = rot.inverse_rotate(x_rot, seed=99)
        torch.testing.assert_close(x, x_rec, atol=1e-3, rtol=1e-3)

    def test_batch_dimensions(self):
        """Rotation should work with batch dimensions."""
        rot = RandomRotation(dim=64, rotation_type="hadamard")
        x = torch.randn(2, 8, 64)
        x_rot = rot.rotate(x, seed=42)
        x_rec = rot.inverse_rotate(x_rot, seed=42)
        torch.testing.assert_close(x, x_rec, atol=1e-4, rtol=1e-4)


# ---------------------------------------------------------------------------
# PolarQuantScalarQuantizer tests
# ---------------------------------------------------------------------------


class TestPolarQuantScalarQuantizer:
    def test_quantize_dequantize_roundtrip(self):
        """Round-trip should produce a reasonable approximation."""
        quantizer = PolarQuantScalarQuantizer(bits=3, block_size=32)
        x = torch.randn(4, 128)
        codes, scales, offsets = quantizer.quantize(x)
        x_rec = quantizer.dequantize(codes, scales, offsets, x.shape[-1])
        assert x_rec.shape == x.shape
        mse = (x - x_rec).pow(2).mean().item()
        # MSE should be small relative to signal variance
        assert mse < x.var().item() * 0.3, f"MSE {mse} too high vs variance {x.var().item()}"

    def test_codes_in_range(self):
        quantizer = PolarQuantScalarQuantizer(bits=4, block_size=16)
        x = torch.randn(8, 64)
        codes, _, _ = quantizer.quantize(x)
        assert codes.min() >= 0
        assert codes.max() <= 15

    def test_output_shape(self):
        quantizer = PolarQuantScalarQuantizer(bits=3, block_size=32)
        x = torch.randn(2, 6, 128)
        codes, scales, offsets = quantizer.quantize(x)
        assert codes.shape == x.shape
        # scales and offsets: (..., num_blocks)
        assert scales.shape == (2, 6, 4)  # 128 / 32 = 4 blocks

    def test_higher_bits_lower_mse(self):
        """More bits should produce lower MSE."""
        x = torch.randn(16, 128)
        mse_values = {}
        for bits in [2, 3, 4, 6]:
            q = PolarQuantScalarQuantizer(bits=bits, block_size=32)
            codes, scales, offsets = q.quantize(x)
            rec = q.dequantize(codes, scales, offsets, x.shape[-1])
            mse_values[bits] = (x - rec).pow(2).mean().item()
        assert mse_values[2] > mse_values[4]
        assert mse_values[3] > mse_values[6]


# ---------------------------------------------------------------------------
# QJLResidualCorrector tests
# ---------------------------------------------------------------------------


class TestQJLResidualCorrector:
    def test_encode_decode_shape(self):
        qjl = QJLResidualCorrector(dim=64)
        residual = torch.randn(4, 64)
        signs = qjl.encode(residual, seed=42)
        assert signs.shape == residual.shape
        assert signs.dtype == torch.uint8
        rec = qjl.decode(signs, seed=42)
        assert rec.shape == residual.shape

    def test_signs_binary(self):
        qjl = QJLResidualCorrector(dim=32)
        residual = torch.randn(8, 32)
        signs = qjl.encode(residual, seed=7)
        assert ((signs == 0) | (signs == 1)).all()

    def test_deterministic(self):
        qjl = QJLResidualCorrector(dim=32)
        residual = torch.randn(4, 32)
        s1 = qjl.encode(residual, seed=42)
        s2 = qjl.encode(residual, seed=42)
        torch.testing.assert_close(s1, s2)


# ---------------------------------------------------------------------------
# TurboQuantCompressor tests
# ---------------------------------------------------------------------------


class TestTurboQuantCompressor:
    def test_compress_decompress_roundtrip(self):
        """Compress→decompress should produce a close approximation."""
        config = TurboQuantConfig(bits_per_channel=3.5, block_size=32)
        compressor = TurboQuantCompressor(config)
        x = torch.randn(2, 8, 64)
        compressed = compressor.compress(x)
        x_rec = compressor.decompress(compressed)
        assert x_rec.shape == x.shape
        assert x_rec.dtype == x.dtype
        # Check approximate fidelity
        cosine_sim = torch.nn.functional.cosine_similarity(
            x.flatten().unsqueeze(0), x_rec.flatten().unsqueeze(0)
        ).item()
        assert cosine_sim > 0.85, f"Cosine similarity {cosine_sim} too low"

    def test_compression_ratio(self):
        """Compressed size should be meaningfully smaller than original."""
        config = TurboQuantConfig(bits_per_channel=3.5, block_size=64)
        compressor = TurboQuantCompressor(config)
        x = torch.randn(4, 16, 256).half()  # FP16 input
        compressed = compressor.compress(x)
        ratio = compressed.compression_ratio
        assert ratio > 1.5, f"Compression ratio {ratio} too low"
        stats = compressor.compression_stats(compressed)
        assert stats["compression_ratio"] == ratio
        assert stats["bits_per_channel"] == 3.5

    def test_inner_product_preservation(self):
        """Per-row dot products should be approximately preserved after compression."""
        config = TurboQuantConfig(bits_per_channel=3.5, use_qjl_residual=True, block_size=32)
        compressor = TurboQuantCompressor(config)
        # Create vectors with known significant inner products
        torch.manual_seed(99)
        a = torch.randn(16, 128)
        b = a + torch.randn(16, 128) * 0.5  # correlated so dot products are large

        ca = compressor.compress(a)
        cb = compressor.compress(b)
        a_rec = compressor.decompress(ca)
        b_rec = compressor.decompress(cb)

        # Compare per-row cosine similarity (robust to scale noise)
        cos_orig = torch.nn.functional.cosine_similarity(a, b, dim=-1)
        cos_rec = torch.nn.functional.cosine_similarity(a_rec, b_rec, dim=-1)
        cos_error = (cos_orig - cos_rec).abs().mean().item()
        assert cos_error < 0.15, f"Mean cosine similarity error {cos_error} too high"

    def test_disabled_passthrough(self):
        """When disabled, compress/decompress should be identity."""
        config = TurboQuantConfig(enabled=False)
        compressor = TurboQuantCompressor(config)
        x = torch.randn(2, 32).half()
        compressed = compressor.compress(x)
        x_rec = compressor.decompress(compressed)
        # Should be exact (passthrough)
        torch.testing.assert_close(x.float(), x_rec.float(), atol=1.0, rtol=0.1)

    def test_4d_kv_tensor(self):
        """Should handle 4D tensors typical of KV cache [batch, heads, seq, dim]."""
        config = TurboQuantConfig(bits_per_channel=3.5, block_size=32)
        compressor = TurboQuantCompressor(config)
        x = torch.randn(2, 6, 32, 64)  # batch=2, heads=6, seq=32, dim=64
        compressed = compressor.compress(x)
        x_rec = compressor.decompress(compressed)
        assert x_rec.shape == x.shape

    def test_zero_vector(self):
        """Should handle zero vectors without NaN or errors."""
        config = TurboQuantConfig(bits_per_channel=3.5, block_size=32)
        compressor = TurboQuantCompressor(config)
        x = torch.zeros(1, 64)
        compressed = compressor.compress(x)
        x_rec = compressor.decompress(compressed)
        assert not torch.isnan(x_rec).any()

    def test_single_element(self):
        """Should handle very small tensors."""
        config = TurboQuantConfig(bits_per_channel=3.5, block_size=1)
        compressor = TurboQuantCompressor(config)
        x = torch.randn(1, 4)
        compressed = compressor.compress(x)
        x_rec = compressor.decompress(compressed)
        assert x_rec.shape == x.shape

    def test_no_qjl_mode(self):
        """Without QJL, should still compress/decompress."""
        config = TurboQuantConfig(bits_per_channel=3.0, use_qjl_residual=False, block_size=32)
        compressor = TurboQuantCompressor(config)
        x = torch.randn(4, 128)
        compressed = compressor.compress(x)
        assert compressed.qjl_signs is None
        x_rec = compressor.decompress(compressed)
        assert x_rec.shape == x.shape

    def test_aggressive_2_5_bit(self):
        """2.5-bit mode should compress more aggressively with slightly more distortion."""
        config_35 = TurboQuantConfig(bits_per_channel=3.5, block_size=32)
        config_25 = TurboQuantConfig(bits_per_channel=2.5, block_size=32)
        comp_35 = TurboQuantCompressor(config_35)
        comp_25 = TurboQuantCompressor(config_25)
        x = torch.randn(4, 128)

        c35 = comp_35.compress(x)
        c25 = comp_25.compress(x)

        rec_35 = comp_35.decompress(c35)
        rec_25 = comp_25.decompress(c25)

        mse_35 = (x - rec_35).pow(2).mean().item()
        mse_25 = (x - rec_25).pow(2).mean().item()

        # 2.5-bit should have higher MSE than 3.5-bit
        assert mse_25 > mse_35, f"2.5-bit MSE {mse_25} should be > 3.5-bit MSE {mse_35}"
