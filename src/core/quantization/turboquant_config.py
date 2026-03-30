"""TurboQuant configuration for KV cache and vector quantization.

Implements configuration for the TurboQuant two-stage compression algorithm
(arXiv:2504.19874, ICLR 2026) which achieves near-optimal vector quantization
with zero accuracy loss at 3.5 bits per channel.

Reference: https://arxiv.org/abs/2504.19874
"""

from dataclasses import dataclass, field


@dataclass
class TurboQuantConfig:
    """Configuration for TurboQuant vector quantization.

    Args:
        bits_per_channel: Target bits per dimension. 3.5 = quality-neutral,
            2.5 = aggressive with marginal degradation. Range: [1.0, 8.0].
        use_qjl_residual: Enable 1-bit QJL residual correction for unbiased
            inner product estimation. Adds ~1 bit overhead but eliminates
            systematic bias in attention scores.
        rotation_type: Random rotation method. "hadamard" is O(n log n) and
            deterministic; "gaussian" is O(n^2) but simpler.
        block_size: Number of elements per quantization block. Larger blocks
            amortize overhead better but reduce granularity.
        target_tensors: Which KV cache tensors to compress.
        enabled: Master switch. When False, passthrough without compression.
    """

    bits_per_channel: float = 3.5
    use_qjl_residual: bool = True
    rotation_type: str = "hadamard"
    block_size: int = 64
    target_tensors: list[str] = field(default_factory=lambda: ["keys", "values"])
    enabled: bool = True

    def __post_init__(self):
        if not 1.0 <= self.bits_per_channel <= 8.0:
            raise ValueError(f"bits_per_channel must be in [1.0, 8.0], got {self.bits_per_channel}")
        if self.rotation_type not in ("hadamard", "gaussian"):
            raise ValueError(f"rotation_type must be 'hadamard' or 'gaussian', got {self.rotation_type}")
        if self.block_size < 1:
            raise ValueError(f"block_size must be >= 1, got {self.block_size}")

    @property
    def integer_bits(self) -> int:
        """Integer part of bits used for PolarQuant scalar quantizer."""
        return int(self.bits_per_channel)

    @property
    def has_fractional_bits(self) -> bool:
        """Whether fractional bits require QJL residual correction."""
        return (self.bits_per_channel % 1.0) > 0.0

    @property
    def num_levels(self) -> int:
        """Number of quantization levels for the scalar quantizer."""
        return 2**self.integer_bits
