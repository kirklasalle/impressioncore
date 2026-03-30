"""Memory management protocols for VRAM/RAM lifecycle and tensor tracking."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

import torch
import torch.nn as nn


@runtime_checkable
class MemoryManagerProtocol(Protocol):
    """Contract for GPU/CPU memory managers.

    Implementations: MemoryManager (manager.py), UltraEfficientMemoryManager,
    DynamicMemoryOptimizer.  Any class exposing these methods satisfies the
    protocol without inheriting from it.
    """

    def get_vram_usage(self) -> float:
        """Return current VRAM usage in GB."""
        ...

    def get_ram_usage(self) -> float:
        """Return current system RAM usage in GB."""
        ...

    def get_gpu_info(self) -> dict[str, Any]:
        """Return GPU metadata: name, free, used, total (all in GB)."""
        ...

    def optimize_memory(self, required_bytes: int = 0) -> int:
        """Free caches / offload tensors.  Return bytes actually freed."""
        ...

    def cleanup(self) -> None:
        """Release all tracked resources; call gc.collect + empty_cache."""
        ...

    def get_stats(self) -> dict[str, Any]:
        """Comprehensive snapshot: vram_used, ram_used, tracked_tensors, …"""
        ...


@runtime_checkable
class MemoryPoolProtocol(Protocol):
    """Contract for tensor pool allocators (e.g. UltraEfficient MemoryPool)."""

    def allocate(self, shape: tuple[int, ...], dtype: torch.dtype) -> torch.Tensor:
        """Allocate a tensor from the pool."""
        ...

    def deallocate(self, tensor: torch.Tensor) -> None:
        """Return a tensor to the pool."""
        ...

    def get_stats(self) -> dict[str, Any]:
        """Pool utilization metrics."""
        ...


@runtime_checkable
class DynamicOffloaderProtocol(Protocol):
    """Contract for module-level CPU ↔ GPU offloading."""

    def attempt_module_offload(
        self, module_name: str, target_device: str = "cpu"
    ) -> bool:
        """Move a named sub-module to *target_device*.  Return success."""
        ...

    def reload_module_to_gpu(self, module_name: str) -> bool:
        """Move a previously offloaded module back to GPU."""
        ...

    def get_module_size_mb(self, module: nn.Module) -> float:
        """Estimate the parameter memory of *module* in MB."""
        ...
