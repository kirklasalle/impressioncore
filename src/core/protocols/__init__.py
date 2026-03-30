"""
ImpressionCore Core Protocols
=============================

Structural typing contracts (PEP 544 Protocols) for the five major subsystems.
Implementations are NOT required to inherit from these; any class that exposes
the correct methods satisfies the protocol at type-check time (mypy / pyright).

Subsystems covered:
  - MemoryManager: VRAM/RAM lifecycle, tensor tracking, statistics
  - ModelBackend: nn.Module contract for forward pass + config
  - TrainingPipeline: train/evaluate/checkpoint lifecycle
  - ConfigProvider: configuration loading and serialization
  - InferenceSession: prompt-in → text-out generation

Usage:
    from src.core.protocols import MemoryManagerProtocol

    def optimize(mgr: MemoryManagerProtocol) -> None:
        freed = mgr.optimize_memory()
        stats = mgr.get_stats()
        ...
"""

from src.core.protocols.config import ConfigProviderProtocol
from src.core.protocols.inference import InferenceSessionProtocol
from src.core.protocols.memory import MemoryManagerProtocol, MemoryPoolProtocol
from src.core.protocols.model import ModelBackendProtocol, ModelConfigProtocol
from src.core.protocols.training import CheckpointData, TrainingPipelineProtocol

__all__ = [
    "CheckpointData",
    "ConfigProviderProtocol",
    "InferenceSessionProtocol",
    "MemoryManagerProtocol",
    "MemoryPoolProtocol",
    "ModelBackendProtocol",
    "ModelConfigProtocol",
    "TrainingPipelineProtocol",
]
