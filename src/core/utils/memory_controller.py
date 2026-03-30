#!/usr/bin/env python3
"""
Memory Controller for ImpressionCore
===================================

Simple memory management and monitoring for VRAM-constrained environments.

Author: ImpressionCore Team
Date: 2025-01-09
"""

import torch
import psutil
import logging
from typing import Optional
from contextlib import contextmanager


class MemoryController:
    """
    Simple memory controller for managing VRAM and system memory usage.
    """
    
    def __init__(self, target_memory_gb: float = 3.5):
        """
        Initialize memory controller.
        
        Args:
            target_memory_gb: Target memory limit in GB
        """
        self.target_memory_gb = target_memory_gb
        self.logger = logging.getLogger(__name__)
        
    def get_memory_info(self) -> dict:
        """Get current memory usage information."""
        info = {}
        
        # CUDA memory info
        if torch.cuda.is_available():
            info['cuda_allocated'] = torch.cuda.memory_allocated() / (1024**3)
            info['cuda_cached'] = torch.cuda.memory_reserved() / (1024**3)
            info['cuda_total'] = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        else:
            info['cuda_allocated'] = 0
            info['cuda_cached'] = 0
            info['cuda_total'] = 0
        
        # System memory info
        memory = psutil.virtual_memory()
        info['system_used'] = memory.used / (1024**3)
        info['system_total'] = memory.total / (1024**3)
        info['system_percent'] = memory.percent
        
        return info
    
    def clear_cache(self):
        """Clear CUDA cache if available."""
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            self.logger.info("CUDA cache cleared")
    
    @contextmanager
    def memory_context(self):
        """Context manager for memory-sensitive operations."""
        try:
            # Clear cache before operation
            self.clear_cache()
            yield
        finally:
            # Clear cache after operation
            self.clear_cache()
    
    def __enter__(self):
        """Enter context manager."""
        return self.memory_context().__enter__()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager."""
        return self.memory_context().__exit__(exc_type, exc_val, exc_tb)
