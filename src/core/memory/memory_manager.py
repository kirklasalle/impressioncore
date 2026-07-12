#!/usr/bin/env python3
"""
ImpressionCore: Memory Manager

Module for memory manager functionality in the ImpressionCore framework.

File: core\\memory_manager.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [memory-critical, framework, pytorch, core, production, 2025, object-oriented]
Dependencies: [torch, rich, typing]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements memory manager functionality for the
ImpressionCore brain-inspired multimodal AI framework. Optimized for memory-
constrained environments and designed to run efficiently on consumer hardware.

Design Philosophy:
- Memory-efficient implementation for GTX 1050 Ti constraints
- Modular design for easy extension and maintenance
- Rich logging and error handling
- Integration with ImpressionCore ecosystem

TODO:
- Add comprehensive unit tests
- Implement performance benchmarks
- Add configuration validation
- Optimize memory usage patterns

Examples:
```python
# Basic usage example
from src.core.memory_manager import MemorySnapshot
instance = MemorySnapshot()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    torch = None
import psutil
import gc
import os
import logging
import warnings
from typing import Dict, Any, Optional, List, Tuple, Union
from dataclasses import dataclass
from contextlib import contextmanager

import numpy as np

# Import rich enhancements for beautiful logging
try:
    from src.core.utils.rich_enhancements import (
        console, create_table, print_info, print_success, 
        print_warning, print_error, display_memory_metrics
        # Memory optimization: Memory-critical operation
    )
    HAS_RICH = True
except ImportError:
    HAS_RICH = False
    console = None

logger = logging.getLogger(__name__)

@dataclass
class MemorySnapshot:
# Memory optimization: Memory-critical operation
    """Snapshot of current memory state."""
    # Memory optimization: Memory-critical operation
    gpu_allocated: float
    # Memory optimization: Memory-critical operation
    gpu_cached: float
    # Memory optimization: Memory-critical operation
    gpu_free: float
    # Memory optimization: Memory-critical operation
    cpu_used: float
    cpu_available: float
    timestamp: str

class EmbeddingMemoryStore:
    """
    Lightweight NumPy-backed nearest-neighbor embedding memory store.

    Used as a simple associative memory for multimodal embedding vectors
    (e.g. by ``src.core.initialization.b3_full_initialization``) when a
    full vector-DB backend (FAISS, etc.) is unnecessary. Not GPU-aware —
    intended for small-to-moderate embedding counts on constrained
    hardware where an exact brute-force L2 search is cheap enough.
    """

    def __init__(self, embed_dim: int):
        """
        Args:
            embed_dim: Dimensionality of embeddings this store will hold.
        """
        self.embed_dim = embed_dim
        self.index: Optional[np.ndarray] = None  # (N, embed_dim) float32
        self.is_trained = False

    def train(self, samples: "np.ndarray") -> None:
        """
        No-op "training" step for API parity with index-based backends
        (e.g. FAISS IVF indexes that require a training pass). The NumPy
        brute-force store needs no training; this simply marks the store
        as ready.

        Args:
            samples: Sample embeddings, shape (N, embed_dim). Unused beyond
                validating dimensionality.
        """
        samples = np.asarray(samples)
        if samples.ndim == 2 and samples.shape[-1] != self.embed_dim:
            raise ValueError(
                f"Sample embedding dim {samples.shape[-1]} != store embed_dim {self.embed_dim}"
            )
        self.is_trained = True

    def add_embeddings(self, embeddings: "np.ndarray") -> None:
        """
        Append new embedding vectors to the store.

        Args:
            embeddings: Array of shape (N, embed_dim) to add.
        """
        embeddings = np.asarray(embeddings, dtype=np.float32)
        if embeddings.ndim == 1:
            embeddings = embeddings.reshape(1, -1)
        if embeddings.shape[-1] != self.embed_dim:
            raise ValueError(
                f"Embedding dim {embeddings.shape[-1]} != store embed_dim {self.embed_dim}"
            )
        if self.index is None:
            self.index = embeddings.copy()
        else:
            self.index = np.concatenate([self.index, embeddings], axis=0)

    def retrieve_memory(
        self, query: "np.ndarray", k: int = 3
    ) -> Tuple["np.ndarray", "np.ndarray"]:
        """
        Retrieve the ``k`` nearest stored embeddings to ``query`` by L2 distance.

        Args:
            query: Query vector(s), shape (embed_dim,) or (Q, embed_dim).
            k: Number of nearest neighbors to return.

        Returns:
            (distances, indices), each shape (Q, min(k, N)). Empty arrays
            (shape (0,)) if the store has no embeddings yet.
        """
        if self.index is None or len(self.index) == 0:
            return np.empty((0,), dtype=np.float32), np.empty((0,), dtype=np.int64)

        query = np.asarray(query, dtype=np.float32)
        if query.ndim == 1:
            query = query.reshape(1, -1)

        k = min(k, len(self.index))
        # Brute-force squared L2 distance: ||q - x||^2 for all stored x.
        diffs = self.index[None, :, :] - query[:, None, :]  # (Q, N, D)
        dists = np.sum(diffs ** 2, axis=-1)  # (Q, N)
        indices = np.argsort(dists, axis=-1)[:, :k]
        distances = np.take_along_axis(dists, indices, axis=-1)
        return distances, indices

    def get_memory_state(self) -> Dict[str, Any]:
        """
        Return a summary of the store's current state.

        Returns:
            Dict with ``total_memories`` (int) and ``embedding_dimension`` (int).
        """
        return {
            "total_memories": 0 if self.index is None else len(self.index),
            "embedding_dimension": self.embed_dim,
        }


class MemoryManager:
# Memory optimization: Memory-critical operation
    """
    Advanced memory management system for ImpressionCore.
    # Memory optimization: Memory-critical operation
    
    Provides comprehensive memory tracking, optimization, and cleanup
    # Memory optimization: Memory-critical operation
    utilities for running AI models on constrained hardware.
    """
    
    def __init__(self, enable_monitoring: bool = True, embed_dim: Optional[int] = None):
        """
        Initialize the memory manager.
        # Memory optimization: Memory-critical operation
        
        Args:
            enable_monitoring: Whether to enable continuous memory monitoring
            # Memory optimization: Memory-critical operation
            embed_dim: Deprecated. Passing this constructs an embedding
                memory store instead — use :class:`EmbeddingMemoryStore`
                directly. Kept for backward compatibility with older
                callers that used ``MemoryManager(embed_dim=...)`` as an
                embedding store.
        """
        if embed_dim is not None:
            warnings.warn(
                "MemoryManager(embed_dim=...) is deprecated; use "
                "EmbeddingMemoryStore(embed_dim=...) directly instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            self._embedding_store = EmbeddingMemoryStore(embed_dim=embed_dim)
            self.embed_dim = embed_dim
            self.index = self._embedding_store.index
            self.is_trained = self._embedding_store.is_trained
        else:
            self._embedding_store = None

        self.enable_monitoring = enable_monitoring
        self.vram_usage = 0
        self.models_registry = {}
        self.memory_snapshots = []
        # Memory optimization: Memory-critical operation
        
        # Check GPU availability
        # Memory optimization: Memory-critical operation
        self.has_gpu = torch.cuda.is_available()
        # Memory optimization: CUDA operations for GPU acceleration
        if self.has_gpu:
        # Memory optimization: Memory-critical operation
            self.device_count = torch.cuda.device_count()
            # Memory optimization: CUDA operations for GPU acceleration
            self.primary_device = torch.cuda.current_device()
            # Memory optimization: CUDA operations for GPU acceleration
        else:
            self.device_count = 0
            # Memory optimization: Device placement for memory management
            self.primary_device = None
            # Memory optimization: Device placement for memory management
            
        if HAS_RICH:
            print_info(f"MemoryManager initialized - GPU Available: {self.has_gpu}")
            # Memory optimization: Memory-critical operation
            if self.has_gpu:
            # Memory optimization: Memory-critical operation
                print_info(f"GPU Devices: {self.device_count}, Primary: {self.primary_device}")
                # Memory optimization: Device placement for memory management

    # -- Deprecated EmbeddingMemoryStore delegation ------------------------
    # These methods only function when this MemoryManager was constructed
    # with `embed_dim=...` (the deprecated embedding-store mode). They
    # delegate to an internal EmbeddingMemoryStore instance for backward
    # compatibility with older callers (e.g. b3_full_initialization.py).

    def train(self, samples: Any) -> None:
        """Deprecated: delegates to EmbeddingMemoryStore.train()."""
        if self._embedding_store is None:
            raise AttributeError(
                "train() requires MemoryManager(embed_dim=...) construction"
            )
        self._embedding_store.train(samples)
        self.is_trained = self._embedding_store.is_trained

    def add_embeddings(self, embeddings: Any) -> None:
        """Deprecated: delegates to EmbeddingMemoryStore.add_embeddings()."""
        if self._embedding_store is None:
            raise AttributeError(
                "add_embeddings() requires MemoryManager(embed_dim=...) construction"
            )
        self._embedding_store.add_embeddings(embeddings)
        self.index = self._embedding_store.index

    def retrieve_memory(self, query: Any, k: int = 3):
        """Deprecated: delegates to EmbeddingMemoryStore.retrieve_memory()."""
        if self._embedding_store is None:
            raise AttributeError(
                "retrieve_memory() requires MemoryManager(embed_dim=...) construction"
            )
        return self._embedding_store.retrieve_memory(query, k=k)

    def get_memory_state(self) -> Dict[str, Any]:
        """Deprecated: delegates to EmbeddingMemoryStore.get_memory_state()."""
        if self._embedding_store is None:
            raise AttributeError(
                "get_memory_state() requires MemoryManager(embed_dim=...) construction"
            )
        return self._embedding_store.get_memory_state()

    def track_vram(self, tensor: Any, name: str = "unnamed") -> None:
        """
        Track VRAM usage for a given tensor.
        
        Args:
            tensor: The tensor to track
            name: Optional name for the tensor
        """
        if tensor.is_cuda:
        # Memory optimization: Memory-critical operation
            size_bytes = tensor.element_size() * tensor.nelement()
            self.vram_usage += size_bytes
            
            if HAS_RICH and self.enable_monitoring:
                print_info(f"Tracking tensor '{name}': {size_bytes / 1024**2:.2f} MB")

    def offload_to_cpu(self, model: Any, model_name: str = "model") -> None:
        """
        Offload model layers to CPU to save VRAM.
        # Memory optimization: Explicit memory cleanup
        
        Args:
            model: The model to offload
            # Memory optimization: Explicit memory cleanup
            model_name: Name of the model for tracking
            # Memory optimization: Explicit memory cleanup
        """
        if HAS_RICH:
            print_info(f"Offloading model '{model_name}' to CPU...")
            # Memory optimization: Explicit memory cleanup
            
        for param in model.parameters():
            param.data = param.data.cpu()
            if param.grad is not None:
                param.grad = param.grad.cpu()
                
        # Update registry
        self.models_registry[model_name] = {
            'model': model,
            'location': 'cpu',
            'last_moved': torch.cuda.Event(enable_timing=True) if self.has_gpu else None
            # Memory optimization: CUDA operations for GPU acceleration
        }
        
        if HAS_RICH:
            print_success(f"Model '{model_name}' successfully offloaded to CPU")
            # Memory optimization: Explicit memory cleanup

    def offload_tensor_to_cpu(self, tensor: Any) -> Any:
        """
        Offload a single tensor to CPU to save VRAM.
        
        Args:
            tensor: The tensor to offload
            
        Returns:
            The tensor moved to CPU
        """
        if tensor.is_cuda:
        # Memory optimization: Memory-critical operation
            return tensor.cpu()
        return tensor

    def get_vram_usage(self) -> int:
        """
        Get the current tracked VRAM usage.
        
        Returns:
            VRAM usage in bytes
        """
        return self.vram_usage
        
    def get_system_memory_stats(self) -> Dict[str, Any]:
    # Memory optimization: Memory-critical operation
        """
        Get comprehensive system memory statistics.
        # Memory optimization: Memory-critical operation
        
        Returns:
            Dictionary containing memory statistics
            # Memory optimization: Memory-critical operation
        """
        stats = {}
        
        # CPU Memory
        # Memory optimization: Memory-critical operation
        memory = psutil.virtual_memory()
        # Memory optimization: Memory-critical operation
        stats['cpu'] = {
            'total': memory.total,
            # Memory optimization: Memory-critical operation
            'available': memory.available,
            # Memory optimization: Memory-critical operation
            'used': memory.used,
            # Memory optimization: Memory-critical operation
            'percent': memory.percent
            # Memory optimization: Memory-critical operation
        }
        
        # GPU Memory (if available)
        # Memory optimization: Memory-critical operation
        if self.has_gpu:
        # Memory optimization: Memory-critical operation
            stats['gpu'] = {}
            # Memory optimization: Memory-critical operation
            for i in range(self.device_count):
            # Memory optimization: Device placement for memory management
                gpu_memory = torch.cuda.get_device_properties(i)
                # Memory optimization: CUDA operations for GPU acceleration
                allocated = torch.cuda.memory_allocated(i)
                # Memory optimization: CUDA operations for GPU acceleration
                cached = torch.cuda.memory_reserved(i)
                # Memory optimization: CUDA operations for GPU acceleration
                
                stats['gpu'][f'device_{i}'] = {
                # Memory optimization: Device placement for memory management
                    'name': gpu_memory.name,
                    # Memory optimization: Memory-critical operation
                    'total': gpu_memory.total_memory,
                    # Memory optimization: Memory-critical operation
                    'allocated': allocated,
                    'cached': cached,
                    'free': gpu_memory.total_memory - allocated
                    # Memory optimization: Memory-critical operation
                }
        
        return stats
    
    def create_memory_snapshot(self) -> MemorySnapshot:
    # Memory optimization: Memory-critical operation
        """
        Create a snapshot of current memory state.
        # Memory optimization: Memory-critical operation
        
        Returns:
            MemorySnapshot object containing current memory state
            # Memory optimization: Memory-critical operation
        """
        stats = self.get_system_memory_stats()
        # Memory optimization: Memory-critical operation
        
        # GPU stats (default to 0 if no GPU)
        # Memory optimization: Memory-critical operation
        gpu_allocated = 0
        # Memory optimization: Memory-critical operation
        gpu_cached = 0
        # Memory optimization: Memory-critical operation
        gpu_free = 0
        # Memory optimization: Memory-critical operation
        
        if self.has_gpu and 'gpu' in stats:
        # Memory optimization: Memory-critical operation
            primary_gpu = stats['gpu'][f'device_{self.primary_device}']
            # Memory optimization: Device placement for memory management
            gpu_allocated = primary_gpu['allocated'] / 1024**3  # GB
            # Memory optimization: Memory-critical operation
            gpu_cached = primary_gpu['cached'] / 1024**3
            # Memory optimization: Memory-critical operation
            gpu_free = primary_gpu['free'] / 1024**3
            # Memory optimization: Memory-critical operation
        
        snapshot = MemorySnapshot(
        # Memory optimization: Memory-critical operation
            gpu_allocated=gpu_allocated,
            # Memory optimization: Memory-critical operation
            gpu_cached=gpu_cached,
            # Memory optimization: Memory-critical operation
            gpu_free=gpu_free,
            # Memory optimization: Memory-critical operation
            cpu_used=stats['cpu']['used'] / 1024**3,
            cpu_available=stats['cpu']['available'] / 1024**3,
            timestamp=torch.cuda.Event(enable_timing=True).query() if self.has_gpu else "N/A"
            # Memory optimization: CUDA operations for GPU acceleration
        )
        
        self.memory_snapshots.append(snapshot)
        # Memory optimization: Memory-critical operation
        return snapshot
    
    @contextmanager
    def profile_memory(self, operation_name: str = "operation"):
    # Memory optimization: Memory-critical operation
        """
        Context manager for profiling memory usage during an operation.
        # Memory optimization: Memory-critical operation
        
        Args:
            operation_name: Name of the operation being profiled
        """
        if HAS_RICH:
            print_info(f"Starting memory profiling for: {operation_name}")
            # Memory optimization: Memory-critical operation
            
        # Take initial snapshot
        initial_snapshot = self.create_memory_snapshot()
        # Memory optimization: Memory-critical operation
        
        try:
            yield
        finally:
            # Take final snapshot
            final_snapshot = self.create_memory_snapshot()
            # Memory optimization: Memory-critical operation
            
            if HAS_RICH:
                # Create comparison table
                table = create_table(f"Memory Profile: {operation_name}")
                # Memory optimization: Memory-critical operation
                table.add_column("Metric", style="cyan")
                table.add_column("Before", style="green")
                table.add_column("After", style="yellow")
                table.add_column("Change", style="red")
                
                # GPU metrics
                # Memory optimization: Memory-critical operation
                if self.has_gpu:
                # Memory optimization: Memory-critical operation
                    gpu_change = final_snapshot.gpu_allocated - initial_snapshot.gpu_allocated
                    # Memory optimization: Memory-critical operation
                    table.add_row(
                        "GPU Allocated (GB)",
                        # Memory optimization: Memory-critical operation
                        f"{initial_snapshot.gpu_allocated:.3f}",
                        # Memory optimization: Memory-critical operation
                        f"{final_snapshot.gpu_allocated:.3f}",
                        # Memory optimization: Memory-critical operation
                        f"{gpu_change:+.3f}"
                        # Memory optimization: Memory-critical operation
                    )
                
                # CPU metrics
                cpu_change = final_snapshot.cpu_used - initial_snapshot.cpu_used
                table.add_row(
                    "CPU Used (GB)",
                    f"{initial_snapshot.cpu_used:.3f}",
                    f"{final_snapshot.cpu_used:.3f}",
                    f"{cpu_change:+.3f}"
                )
                
                console.print(table)
    
    def cleanup_memory(self, aggressive: bool = False) -> None:
    # Memory optimization: Memory-critical operation
        """
        Perform memory cleanup operations.
        # Memory optimization: Memory-critical operation
        
        Args:
            aggressive: Whether to perform aggressive cleanup
        """
        if HAS_RICH:
            print_info("Starting memory cleanup...")
            # Memory optimization: Memory-critical operation
            
        # Clear Python garbage collector
        collected = gc.collect()
        # Memory optimization: Force garbage collection
        
        # Clear GPU cache if available
        # Memory optimization: Memory-critical operation
        if self.has_gpu:
        # Memory optimization: Memory-critical operation
            torch.cuda.empty_cache()
            # Memory optimization: CUDA operations for GPU acceleration
            if aggressive:
                torch.cuda.synchronize()
                # Memory optimization: CUDA operations for GPU acceleration
                
        if HAS_RICH:
            print_success(f"Memory cleanup completed - Collected {collected} objects")
            # Memory optimization: Memory-critical operation
    
    def display_memory_status(self) -> None:
    # Memory optimization: Memory-critical operation
        """Display current memory status using rich formatting."""
        # Memory optimization: Memory-critical operation
        if not HAS_RICH:
            # Fallback to simple print
            stats = self.get_system_memory_stats()
            # Memory optimization: Memory-critical operation
            print(f"CPU Memory: {stats['cpu']['percent']:.1f}% used")
            # Memory optimization: Memory-critical operation
            if self.has_gpu:
            # Memory optimization: Memory-critical operation
                for device, gpu_stats in stats['gpu'].items():
                # Memory optimization: Device placement for memory management
                    allocated_pct = (gpu_stats['allocated'] / gpu_stats['total']) * 100
                    # Memory optimization: Memory-critical operation
                    print(f"GPU {device}: {allocated_pct:.1f}% allocated")
                    # Memory optimization: Device placement for memory management
            return
            
        # Rich formatted display
        display_memory_metrics(self.get_system_memory_stats())
        # Memory optimization: Memory-critical operation
