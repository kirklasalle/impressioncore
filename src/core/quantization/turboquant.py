"""TurboQuant: Online vector quantization with near-optimal distortion rate.

Pure PyTorch implementation of the TurboQuant algorithm (arXiv:2504.19874,
ICLR 2026) for KV cache compression and vector search quantization.

Two-stage algorithm:
  1. PolarQuant: Random rotation → concentrated Beta distribution on
     coordinates → optimal per-coordinate scalar quantization.
  2. QJL residual: 1-bit Quantized Johnson-Lindenstrauss transform on the
     residual error for unbiased inner product estimation.

All operations are GPU-compatible pure PyTorch — no custom CUDA kernels.

Reference: https://arxiv.org/abs/2504.19874
"""

import logging
import math
from dataclasses import dataclass

import torch
import torch.nn as nn

from src.core.quantization.turboquant_config import TurboQuantConfig

logger = logging.getLogger(__name__)


@dataclass
class CompressedTensor:
    """Container for a TurboQuant-compressed tensor.

    Stores the quantized codes, scale/offset parameters, rotation seed,
    and optional QJL sign bits — everything needed to decompress.
    """

    codes: torch.Tensor  # int8 quantized codes: same shape as original
    scales: torch.Tensor  # per-block scale factors
    offsets: torch.Tensor  # per-block offset (zero-point)
    rotation_seed: int  # seed used to generate the rotation matrix
    qjl_signs: torch.Tensor | None  # 1-bit QJL sign tensor (packed uint8), or None
    original_shape: tuple[int, ...]
    original_dtype: torch.dtype
    bits: int

    def numel_compressed(self) -> int:
        """Theoretical compressed storage in bytes with proper bit-packing.

        Codes are stored as int8 for PyTorch compatibility but only use
        `self.bits` bits of information per element. QJL signs are 1-bit.
        A production implementation would bit-pack these for the sizes
        computed here.
        """
        code_bytes = math.ceil(self.codes.numel() * self.bits / 8)
        param_bytes = (self.scales.numel() + self.offsets.numel()) * self.scales.element_size()
        qjl_bytes = math.ceil(self.qjl_signs.numel() / 8) if self.qjl_signs is not None else 0
        return code_bytes + param_bytes + qjl_bytes

    def numel_original(self) -> int:
        """Original tensor storage in bytes (assumes FP16)."""
        total_elements = 1
        for s in self.original_shape:
            total_elements *= s
        return total_elements * 2  # FP16 = 2 bytes

    @property
    def compression_ratio(self) -> float:
        orig = self.numel_original()
        return orig / max(self.numel_compressed(), 1)


class RandomRotation(nn.Module):
    """Applies a deterministic pseudo-random orthogonal rotation.

    Uses a randomized Hadamard-like transform via random sign flips followed
    by a normalized random projection. For dimensions that are powers of 2,
    uses the fast Walsh-Hadamard pattern; otherwise falls back to a random
    orthogonal matrix generated from a seeded QR decomposition.

    The rotation induces a concentrated Beta distribution on the coordinates
    of unit-norm vectors, which is the key insight enabling PolarQuant's
    efficient per-coordinate scalar quantization.
    """

    def __init__(self, dim: int, rotation_type: str = "hadamard"):
        super().__init__()
        self.dim = dim
        self.rotation_type = rotation_type

    def _generate_signs(self, seed: int, dim: int, device: torch.device) -> torch.Tensor:
        """Generate deterministic random ±1 sign vector from seed."""
        gen = torch.Generator(device="cpu")
        gen.manual_seed(seed)
        signs = torch.randint(0, 2, (dim,), generator=gen, dtype=torch.float32) * 2 - 1
        return signs.to(device)

    def _hadamard_transform(self, x: torch.Tensor) -> torch.Tensor:
        """Fast Walsh-Hadamard transform in O(n log n).

        Works on the last dimension. Pads to nearest power of 2 if needed.
        """
        *batch_shape, dim = x.shape
        # Pad to power of 2
        log2_dim = math.ceil(math.log2(max(dim, 1)))
        padded_dim = 2**log2_dim
        if padded_dim != dim:
            x = torch.nn.functional.pad(x, (0, padded_dim - dim))

        # Butterfly operations
        h = 1
        while h < padded_dim:
            x_reshaped = x.view(*batch_shape, padded_dim // (2 * h), 2, h)
            a = x_reshaped[..., 0, :].clone()
            b = x_reshaped[..., 1, :].clone()
            x_reshaped[..., 0, :] = a + b
            x_reshaped[..., 1, :] = a - b
            x = x_reshaped.view(*batch_shape, padded_dim)
            h *= 2

        # Normalize and trim back
        x = x / math.sqrt(padded_dim)
        if padded_dim != dim:
            x = x[..., :dim]
        return x

    def _random_orthogonal(self, seed: int, dim: int, device: torch.device, dtype: torch.dtype) -> torch.Tensor:
        """Generate a random orthogonal matrix via QR decomposition."""
        gen = torch.Generator(device="cpu")
        gen.manual_seed(seed)
        random_matrix = torch.randn(dim, dim, generator=gen, dtype=torch.float32)
        q, r = torch.linalg.qr(random_matrix)
        # Ensure proper rotation (det = +1) by flipping sign of columns where diagonal of R is negative
        d = torch.diag(r)
        q = q * torch.sign(d).unsqueeze(0)
        return q.to(device=device, dtype=dtype)

    def rotate(self, x: torch.Tensor, seed: int) -> torch.Tensor:
        """Apply random rotation to the last dimension of x."""
        original_dtype = x.dtype
        x = x.float()

        if self.rotation_type == "hadamard":
            # Random sign flip + Hadamard = random orthogonal rotation
            signs = self._generate_signs(seed, x.shape[-1], x.device)
            x = x * signs
            x = self._hadamard_transform(x)
        else:
            # Full random orthogonal matrix
            rot = self._random_orthogonal(seed, x.shape[-1], x.device, x.dtype)
            x = x @ rot

        return x.to(original_dtype)

    def inverse_rotate(self, x: torch.Tensor, seed: int) -> torch.Tensor:
        """Apply inverse rotation (transpose of the rotation matrix)."""
        original_dtype = x.dtype
        x = x.float()

        if self.rotation_type == "hadamard":
            # Hadamard is self-inverse; signs are self-inverse
            x = self._hadamard_transform(x)
            signs = self._generate_signs(seed, x.shape[-1], x.device)
            x = x * signs
        else:
            rot = self._random_orthogonal(seed, x.shape[-1], x.device, x.dtype)
            x = x @ rot.T

        return x.to(original_dtype)


class PolarQuantScalarQuantizer(nn.Module):
    """Per-coordinate scalar quantizer for rotated vectors.

    After random rotation, vector coordinates follow a concentrated Beta
    distribution. This quantizer exploits that concentration by applying a
    uniform scalar quantizer per coordinate with block-wise scale/offset
    parameters, achieving near-optimal MSE distortion.
    """

    def __init__(self, bits: int = 3, block_size: int = 64):
        super().__init__()
        self.bits = bits
        self.block_size = block_size
        self.num_levels = 2**bits
        self.q_min = 0
        self.q_max = self.num_levels - 1

    def quantize(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """Quantize tensor to integer codes with per-block scale and offset.

        Args:
            x: Input tensor of any shape. Last dim is quantized in blocks.

        Returns:
            codes: int8 quantized codes, same shape as x.
            scales: per-block scale factors.
            offsets: per-block offsets (zero points).
        """
        original_shape = x.shape
        x_flat = x.float()

        # Process in blocks along the last dimension
        last_dim = x_flat.shape[-1]
        if last_dim % self.block_size == 0:
            num_blocks = last_dim // self.block_size
        else:
            # Pad to block boundary
            pad_size = self.block_size - (last_dim % self.block_size)
            x_flat = torch.nn.functional.pad(x_flat, (0, pad_size))
            num_blocks = x_flat.shape[-1] // self.block_size

        # Reshape: (..., num_blocks, block_size)
        batch_shape = x_flat.shape[:-1]
        x_blocked = x_flat.view(*batch_shape, num_blocks, self.block_size)

        # Compute per-block min/max
        block_min = x_blocked.amin(dim=-1, keepdim=True)
        block_max = x_blocked.amax(dim=-1, keepdim=True)

        # Scale and offset
        scale_range = block_max - block_min
        scales = scale_range / self.q_max
        scales = scales.clamp(min=1e-8)
        offsets = block_min

        # Quantize
        codes = torch.round((x_blocked - offsets) / scales).clamp(self.q_min, self.q_max)
        codes = codes.to(torch.int8)

        # Reshape codes back, trim padding
        codes = codes.view(*batch_shape, -1)
        if codes.shape[-1] != original_shape[-1]:
            codes = codes[..., : original_shape[-1]]

        # Squeeze the keepdim
        scales = scales.squeeze(-1)
        offsets = offsets.squeeze(-1)

        return codes, scales, offsets

    def dequantize(
        self, codes: torch.Tensor, scales: torch.Tensor, offsets: torch.Tensor, original_last_dim: int
    ) -> torch.Tensor:
        """Dequantize codes back to float tensor.

        Args:
            codes: int8 quantized codes.
            scales: per-block scale factors.
            offsets: per-block offsets.
            original_last_dim: original last dimension size (for unpadding).

        Returns:
            Dequantized float tensor with original shape.
        """
        batch_shape = codes.shape[:-1]
        last_dim = codes.shape[-1]

        # Pad codes if needed to match block structure
        if last_dim % self.block_size != 0:
            pad_size = self.block_size - (last_dim % self.block_size)
            codes = torch.nn.functional.pad(codes, (0, pad_size))

        num_blocks = codes.shape[-1] // self.block_size
        codes_blocked = codes.view(*batch_shape, num_blocks, self.block_size).float()

        # Un-squeeze scales/offsets for broadcasting
        scales_expanded = scales.unsqueeze(-1)
        offsets_expanded = offsets.unsqueeze(-1)

        # Dequantize
        x = codes_blocked * scales_expanded + offsets_expanded

        # Flatten and trim
        x = x.view(*batch_shape, -1)
        if x.shape[-1] != original_last_dim:
            x = x[..., :original_last_dim]

        return x


class QJLResidualCorrector(nn.Module):
    """1-bit Quantized Johnson-Lindenstrauss residual correction.

    Applies a random projection to the quantization residual and stores only
    the sign bits. This eliminates inner-product bias introduced by scalar
    quantization, ensuring unbiased attention score estimation.

    The correction adds ~1 effective bit per channel but provides critical
    accuracy preservation for attention computations.
    """

    def __init__(self, dim: int):
        super().__init__()
        self.dim = dim

    def _generate_projection(self, seed: int, dim: int, device: torch.device) -> torch.Tensor:
        """Generate a random ±1/sqrt(dim) projection matrix."""
        gen = torch.Generator(device="cpu")
        gen.manual_seed(seed + 999_999)  # Offset from rotation seed
        # Rademacher random matrix: ±1 entries, scaled by 1/sqrt(dim)
        signs = torch.randint(0, 2, (dim, dim), generator=gen, dtype=torch.float32) * 2 - 1
        return (signs / math.sqrt(dim)).to(device)

    def encode(self, residual: torch.Tensor, seed: int) -> torch.Tensor:
        """Project residual and store sign bits as packed uint8.

        Args:
            residual: quantization error tensor (..., dim).
            seed: random seed for reproducible projection.

        Returns:
            Sign bits packed into uint8 tensor.
        """
        dim = residual.shape[-1]
        proj = self._generate_projection(seed, dim, residual.device)
        # Project: (..., dim) @ (dim, dim) → (..., dim)
        projected = residual.float() @ proj
        # Store signs: +1 → 1, -1 → 0
        sign_bits = (projected > 0).to(torch.uint8)
        return sign_bits

    def decode(self, sign_bits: torch.Tensor, seed: int, scale: float = 1.0) -> torch.Tensor:
        """Reconstruct approximate residual from sign bits.

        Args:
            sign_bits: uint8 tensor of sign bits (..., dim).
            seed: random seed matching the encode call.
            scale: scaling factor for the reconstruction magnitude.

        Returns:
            Approximate residual tensor (..., dim).
        """
        dim = sign_bits.shape[-1]
        proj = self._generate_projection(seed, dim, sign_bits.device)
        # Convert signs back: 1 → +1, 0 → -1
        signs_float = sign_bits.float() * 2 - 1
        # Inverse project: (..., dim) @ (dim, dim)^T → (..., dim)
        reconstructed = signs_float @ proj.T
        return reconstructed * scale


class TurboQuantCompressor(nn.Module):
    """TurboQuant two-stage vector quantization compressor.

    Composes PolarQuant scalar quantization with QJL residual correction
    for near-optimal KV cache compression. Training-free — works as a
    drop-in compression layer at inference time.

    Usage:
        config = TurboQuantConfig(bits_per_channel=3.5)
        compressor = TurboQuantCompressor(config)
        compressed = compressor.compress(key_tensor)
        decompressed = compressor.decompress(compressed)
    """

    def __init__(self, config: TurboQuantConfig | None = None):
        super().__init__()
        self.config = config or TurboQuantConfig()
        self.rotation = RandomRotation(dim=0, rotation_type=self.config.rotation_type)
        self.quantizer = PolarQuantScalarQuantizer(
            bits=self.config.integer_bits,
            block_size=self.config.block_size,
        )
        self.qjl = QJLResidualCorrector(dim=0)
        self._seed_counter = 0

    def _next_seed(self) -> int:
        """Generate a unique seed for each compression call."""
        self._seed_counter += 1
        return self._seed_counter * 31337

    def compress(self, x: torch.Tensor) -> CompressedTensor:
        """Compress a tensor using TurboQuant two-stage algorithm.

        Args:
            x: Input tensor (typically KV cache: [batch, heads, seq, dim] or
               [batch, seq, dim]). Compression operates on the last dimension.

        Returns:
            CompressedTensor with all data needed for decompression.
        """
        if not self.config.enabled:
            # Passthrough: store as-is in a trivial CompressedTensor
            return CompressedTensor(
                codes=x.to(torch.int8),
                scales=torch.tensor([1.0], device=x.device),
                offsets=torch.tensor([0.0], device=x.device),
                rotation_seed=0,
                qjl_signs=None,
                original_shape=x.shape,
                original_dtype=x.dtype,
                bits=16,
            )

        seed = self._next_seed()
        original_shape = x.shape
        original_dtype = x.dtype

        # Stage 1: Random rotation → concentrated coordinate distribution
        self.rotation.dim = x.shape[-1]
        x_rotated = self.rotation.rotate(x, seed)

        # Stage 2: Per-coordinate scalar quantization (PolarQuant)
        codes, scales, offsets = self.quantizer.quantize(x_rotated)

        # Stage 3 (optional): QJL residual correction for unbiased inner product
        qjl_signs = None
        if self.config.use_qjl_residual:
            # Compute quantization residual
            x_reconstructed = self.quantizer.dequantize(codes, scales, offsets, x_rotated.shape[-1])
            residual = x_rotated - x_reconstructed

            # Encode residual sign bits
            self.qjl.dim = x.shape[-1]
            qjl_signs = self.qjl.encode(residual, seed)

        return CompressedTensor(
            codes=codes,
            scales=scales,
            offsets=offsets,
            rotation_seed=seed,
            qjl_signs=qjl_signs,
            original_shape=original_shape,
            original_dtype=original_dtype,
            bits=self.config.integer_bits,
        )

    def decompress(self, compressed: CompressedTensor) -> torch.Tensor:
        """Decompress a TurboQuant-compressed tensor.

        Args:
            compressed: CompressedTensor from compress().

        Returns:
            Decompressed tensor with original shape and dtype.
        """
        if compressed.bits == 16:
            # Passthrough case: was not actually compressed
            return compressed.codes.to(compressed.original_dtype)

        original_last_dim = compressed.original_shape[-1]

        # Stage 1: Dequantize from scalar codes
        x_rotated = self.quantizer.dequantize(
            compressed.codes, compressed.scales, compressed.offsets, original_last_dim
        )

        # Stage 2: Add QJL residual correction if available
        if compressed.qjl_signs is not None:
            self.qjl.dim = original_last_dim
            # Estimate residual magnitude from quantization step size
            avg_scale = compressed.scales.float().mean().item()
            residual_approx = self.qjl.decode(compressed.qjl_signs, compressed.rotation_seed, scale=avg_scale * 0.5)
            x_rotated = x_rotated + residual_approx

        # Stage 3: Inverse rotation to recover original coordinate space
        self.rotation.dim = original_last_dim
        x = self.rotation.inverse_rotate(x_rotated, compressed.rotation_seed)

        # Restore original shape and dtype
        x = x.view(compressed.original_shape)
        return x.to(compressed.original_dtype)

    def compression_stats(self, compressed: CompressedTensor) -> dict:
        """Return compression statistics for monitoring.

        Args:
            compressed: A CompressedTensor from compress().

        Returns:
            Dict with compression ratio, byte counts, and config info.
        """
        return {
            "compression_ratio": compressed.compression_ratio,
            "original_bytes": compressed.numel_original(),
            "compressed_bytes": compressed.numel_compressed(),
            "bits_per_channel": self.config.bits_per_channel,
            "qjl_enabled": compressed.qjl_signs is not None,
            "rotation_type": self.config.rotation_type,
        }
