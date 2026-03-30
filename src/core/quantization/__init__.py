"""ImpressionCore quantization subsystem.

Provides TurboQuant (arXiv:2504.19874) for KV cache compression and vector
search quantization, alongside block-wise weight quantization utilities.
"""

from src.core.quantization.turboquant import (
    CompressedTensor,
    TurboQuantCompressor,
)
from src.core.quantization.turboquant_config import TurboQuantConfig

__all__ = [
    "CompressedTensor",
    "TurboQuantCompressor",
    "TurboQuantConfig",
]
