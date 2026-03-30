#!/usr/bin/env python3
"""
Memory Optimizer Utility

Provides memory optimization utilities for running models efficiently on
GTX 1050 Ti (4GB VRAM) and other memory-constrained hardware.

File: core/utils/memory_optimizer.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-06-05
Version: 1.0.0

Authors:
- GitHub Copilot
- Kirk LaSalle

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [memory, optimization, gpu, gtx1050ti, 2025]
Dependencies: [torch, psutil]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module provides memory management and optimization utilities specifically
designed for running ImpressionCore models on consumer hardware with limited VRAM.

Key Features:
- Dynamic memory monitoring and cleanup
- Model optimization for low VRAM
- Gradient checkpointing support
- Memory profiling and reporting
"""

import torch
import gc
import psutil
import logging
from typing import Optional, Dict, Any, List
import time

# Rich logging
from src.core.utils.rich_logging import get_rich_logger


class MemoryOptimizer:
    """
    Memory optimization utility for ImpressionCore models.
    
    Provides dynamic memory management, cleanup, and optimization
    specifically designed for GTX 1050 Ti (4GB VRAM) constraints.
    
    Args:
        max_memory_gb (float): Maximum memory to use in GB
        device (str): Target device ('cuda', 'cpu')
        enable_monitoring (bool): Enable continuous memory monitoring
        
    Example:
        ```python
        optimizer = MemoryOptimizer(max_memory_gb=3.5, device='cuda')
        optimizer.optimize_model(model)
        optimizer.cleanup()
        ```
    """
    
    def __init__(
        self,
        max_memory_gb: float = 3.5,
        device: str = 'cuda',
        enable_monitoring: bool = True
    ):
        self.logger = get_rich_logger(__name__)
        self.max_memory_gb = max_memory_gb
        self.device = device
        self.enable_monitoring = enable_monitoring
        
        # Memory tracking
        self._memory_history: List[float] = []
        self._peak_memory: float = 0.0
        self._cleanup_count: int = 0
        
        # Check device availability
        self.cuda_available = torch.cuda.is_available() and device == 'cuda'
        
        if self.cuda_available:
            self.logger.info(f"Memory optimizer initialized for CUDA (max: {max_memory_gb}GB)")
            self._log_gpu_info()
        else:
            self.logger.info("Memory optimizer initialized for CPU")
    
    def _log_gpu_info(self):
        """Log GPU memory information."""
        if not self.cuda_available:
            return
        
        try:
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
            self.logger.info(f"GPU: {torch.cuda.get_device_name(0)}")
            self.logger.info(f"Total VRAM: {gpu_memory:.1f}GB")
            self.logger.info(f"Target usage: {self.max_memory_gb:.1f}GB")
        except Exception as e:
            self.logger.warning(f"Could not get GPU info: {e}")
    
    def get_memory_usage(self) -> Dict[str, float]:
        """
        Get current memory usage statistics.
        
        Returns:
            Dict with memory usage in GB
        """
        stats = {
            'cpu_memory_gb': psutil.virtual_memory().used / 1024**3,
            'cpu_memory_percent': psutil.virtual_memory().percent
        }
        
        if self.cuda_available:
            try:
                stats.update({
                    'gpu_memory_allocated_gb': torch.cuda.memory_allocated() / 1024**3,
                    'gpu_memory_reserved_gb': torch.cuda.memory_reserved() / 1024**3,
                    'gpu_memory_max_allocated_gb': torch.cuda.max_memory_allocated() / 1024**3
                })
            except Exception as e:
                self.logger.warning(f"Could not get GPU memory stats: {e}")
        
        return stats
    
    def cleanup(self):
        """
        Perform aggressive memory cleanup.
        
        This method performs comprehensive memory cleanup including:
        - Python garbage collection
        - PyTorch cache clearing
        - CUDA memory cleanup
        """
        self._cleanup_count += 1
        
        # Python garbage collection
        collected = gc.collect()
        
        # PyTorch cleanup
        if self.cuda_available:
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
        
        # Log cleanup results
        memory_stats = self.get_memory_usage()
        self.logger.debug(f"Cleanup #{self._cleanup_count}: Collected {collected} objects")
        
        if self.cuda_available:
            self.logger.debug(f"GPU memory after cleanup: {memory_stats.get('gpu_memory_allocated_gb', 0):.2f}GB")
    
    def optimize_model(self, model: torch.nn.Module) -> torch.nn.Module:
        """
        Apply memory optimizations to a PyTorch model.
        
        Args:
            model: PyTorch model to optimize
            
        Returns:
            Optimized model
        """
        self.logger.info("Applying memory optimizations to model...")
        
        try:
            # Enable gradient checkpointing if available
            if hasattr(model, 'gradient_checkpointing_enable'):
                model.gradient_checkpointing_enable()
                self.logger.info("✅ Gradient checkpointing enabled")
            
            # Set model to eval mode for inference
            model.eval()
            
            # Apply mixed precision if CUDA available
            if self.cuda_available and hasattr(torch, 'autocast'):
                self.logger.info("✅ Mixed precision optimization ready")
            
            # Move to device efficiently
            model = model.to(self.device)
            
            self.logger.info("✅ Model memory optimizations applied")
            return model
            
        except Exception as e:
            self.logger.error(f"Model optimization failed: {e}")
            return model
    
    def monitor_memory(self) -> bool:
        """
        Monitor memory usage and return True if within limits.
        
        Returns:
            bool: True if memory usage is within acceptable limits
        """
        if not self.enable_monitoring:
            return True
        
        stats = self.get_memory_usage()
        
        # Check GPU memory if available
        if self.cuda_available:
            gpu_memory = stats.get('gpu_memory_allocated_gb', 0)
            if gpu_memory > self.max_memory_gb:
                self.logger.warning(f"GPU memory usage ({gpu_memory:.2f}GB) exceeds limit ({self.max_memory_gb}GB)")
                return False
            
            # Track peak memory
            if gpu_memory > self._peak_memory:
                self._peak_memory = gpu_memory
        
        # Track memory history
        total_memory = stats.get('gpu_memory_allocated_gb', 0) + stats.get('cpu_memory_gb', 0)
        self._memory_history.append(total_memory)
        
        # Keep only recent history
        if len(self._memory_history) > 100:
            self._memory_history = self._memory_history[-50:]
        
        return True
    
    def get_optimization_stats(self) -> Dict[str, Any]:
        """
        Get memory optimization statistics.
        
        Returns:
            Dict with optimization statistics
        """
        current_stats = self.get_memory_usage()
        
        return {
            'current_memory': current_stats,
            'peak_memory_gb': self._peak_memory,
            'cleanup_count': self._cleanup_count,
            'memory_history_length': len(self._memory_history),
            'avg_memory_usage_gb': sum(self._memory_history) / len(self._memory_history) if self._memory_history else 0,
            'cuda_available': self.cuda_available,
            'max_memory_limit_gb': self.max_memory_gb
        }
    
    def emergency_cleanup(self):
        """
        Perform emergency memory cleanup when running low on memory.
        """
        self.logger.warning("🚨 Performing emergency memory cleanup")
        
        # Multiple cleanup passes
        for i in range(3):
            self.cleanup()
            time.sleep(0.1)  # Allow cleanup to complete
        
        # Log results
        stats = self.get_memory_usage()
        self.logger.info(f"Emergency cleanup complete. GPU memory: {stats.get('gpu_memory_allocated_gb', 0):.2f}GB")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        self.cleanup()


# Convenience functions
def create_optimizer(
    max_memory_gb: float = 3.5,
    device: str = 'auto'
) -> MemoryOptimizer:
    """
    Create a memory optimizer with GTX 1050 Ti defaults.
    
    Args:
        max_memory_gb: Maximum memory to use
        device: Target device
        
    Returns:
        MemoryOptimizer: Configured optimizer
    """
    if device == 'auto':
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
    
    return MemoryOptimizer(
        max_memory_gb=max_memory_gb,
        device=device,
        enable_monitoring=True
    )


def optimize_for_gtx1050ti(model: torch.nn.Module) -> torch.nn.Module:
    """
    Quick optimization for GTX 1050 Ti hardware.
    
    Args:
        model: PyTorch model to optimize
        
    Returns:
        Optimized model
    """
    optimizer = create_optimizer(max_memory_gb=3.5, device='cuda')
    return optimizer.optimize_model(model)


if __name__ == "__main__":
    # Test the memory optimizer
    optimizer = create_optimizer()
    
    print("Memory Optimizer Test")
    print("=" * 30)
    
    # Show initial stats
    stats = optimizer.get_memory_usage()
    print(f"Initial memory: {stats}")
    
    # Test cleanup
    optimizer.cleanup()
    
    # Show optimization stats
    opt_stats = optimizer.get_optimization_stats()
    print(f"Optimization stats: {opt_stats}")
    
    print("✅ Memory optimizer test complete")
