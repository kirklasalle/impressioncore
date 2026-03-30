#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #cuda #memory_management #python #pytorch #source_code #src/core/utils/device_manager.py
**Category:** Core Implementation
**Status:** Active
"""









# Device Manager

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:00
# Author:** ImpressionCore Team
# Tags:** #cuda #memory_management #python #pytorch #source_code #src\\core\\utils\\device_manager.py
# Category:** Core Implementation
# Status:** Active

"""
ImpressionCore-B1 Device Management Utility
Ensures consistent device placement and dtype handling for CUDA operations.

Author: Virtually Robotic GitHub Copilot
Date: June 20, 2025
Sacred Covenant: Verified
"""

import logging
from typing import Any

import torch
import torch.nn as nn

logger = logging.getLogger(__name__)

class DeviceManager:
    """Comprehensive device and dtype management for GTX 1050 Ti optimization."""

    def __init__(self, force_cuda: bool = True, dtype: torch.dtype = torch.float32):
        """
        Initialize device manager with CUDA-first approach.

        Args:
            force_cuda: Always use CUDA when available (ImpressionCore requirement)
            dtype: Default tensor dtype for consistency
        """
        self.force_cuda = force_cuda
        self.dtype = dtype
        self.device = self._initialize_device()

        logger.info(f"🔧 DeviceManager initialized: {self.device}, dtype: {self.dtype}")

    def _initialize_device(self) -> torch.device:
        """Initialize device with CUDA preference as documented."""
        if self.force_cuda and torch.cuda.is_available():
            device = torch.device("cuda")
            logger.info(f"✅ CUDA device selected: {torch.cuda.get_device_name()}")
            logger.info(f"📊 VRAM available: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f}GB")
        else:
            device = torch.device("cpu")
            logger.warning("⚠️ Falling back to CPU (CUDA not available)")

        return device

    def ensure_device_dtype(self, tensor: torch.Tensor) -> torch.Tensor:
        """
        Ensure tensor is on correct device with correct dtype.

        Args:
            tensor: Input tensor to fix

        Returns:
            Tensor on correct device with correct dtype
        """
        if tensor.device != self.device:
            tensor = tensor.to(self.device)

        # Only convert dtype for float types to avoid mixed precision issues
        if tensor.dtype != self.dtype and tensor.dtype.is_floating_point:
            try:
                tensor = tensor.to(self.dtype)
            except RuntimeError:
                # If conversion fails, keep original dtype but log warning
                print(f"Warning: Could not convert tensor from {tensor.dtype} to {self.dtype}")

        return tensor

    def ensure_batch_consistency(self, batch: dict[str, Any]) -> dict[str, Any]:
        """
        Ensure all tensors in batch have consistent device and dtype.

        Args:
            batch: Dictionary containing model inputs

        Returns:
            Batch with consistent device and dtype
        """
        fixed_batch = {}

        for key, value in batch.items():
            if isinstance(value, torch.Tensor):
                fixed_batch[key] = self.ensure_device_dtype(value)
            elif isinstance(value, dict):
                # Handle nested dictionaries (like modality inputs)
                fixed_batch[key] = self.ensure_batch_consistency(value)
            elif isinstance(value, list) and len(value) > 0 and isinstance(value[0], torch.Tensor):
                # Handle lists of tensors
                fixed_batch[key] = [self.ensure_device_dtype(t) for t in value]
            else:
                fixed_batch[key] = value

        return fixed_batch

    def prepare_model(self, model: nn.Module) -> nn.Module:
        """
        Prepare model for consistent device and dtype usage.

        Args:
            model: PyTorch model to prepare

        Returns:
            Model on correct device with correct dtype
        """
        model = model.to(self.device, self.dtype)

        # Ensure all model parameters have consistent dtype
        for param in model.parameters():
            if param.dtype != self.dtype:
                param.data = param.data.to(self.dtype)

        return model

    def get_device_info(self) -> dict[str, Any]:
        """Get comprehensive device information."""
        info = {
            "device": str(self.device),
            "dtype": str(self.dtype),
            "cuda_available": torch.cuda.is_available(),
            "cuda_device_count": torch.cuda.device_count() if torch.cuda.is_available() else 0
        }

        if torch.cuda.is_available():
            info.update({
                "cuda_device_name": torch.cuda.get_device_name(),
                "cuda_memory_total": torch.cuda.get_device_properties(0).total_memory,
                "cuda_memory_allocated": torch.cuda.memory_allocated(),
                "cuda_memory_cached": torch.cuda.memory_reserved()
            })

        return info

# Global device manager instance
_device_manager = None

def get_device_manager() -> DeviceManager:
    """Get global device manager instance."""
    global _device_manager
    if _device_manager is None:
        _device_manager = DeviceManager()
    return _device_manager

def ensure_cuda_tensor(tensor: torch.Tensor) -> torch.Tensor:
    """Quick utility to ensure tensor is on CUDA with float32."""
    dm = get_device_manager()
    return dm.ensure_device_dtype(tensor)

def prepare_model_for_cuda(model: nn.Module) -> nn.Module:
    """Quick utility to prepare model for CUDA usage."""
    dm = get_device_manager()
    return dm.prepare_model(model)
