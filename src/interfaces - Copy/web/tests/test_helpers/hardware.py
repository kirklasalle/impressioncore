#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** Kirk LaSalle
**Tags:** #cuda #gpu_optimization #memory_management #multimodal #performance #python #pytorch #source_code #src/interfaces/web\tests/test_helpers\\hardware.py #testing #web_interface
**Category:** Interface Definitions
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:02
# Author:** Kirk LaSalle
# Tags:** #cuda #gpu_optimization #memory_management #multimodal #performance #python #pytorch #source_code #src\\interfaces\\web\\tests\\test_helpers\\hardware.py #testing #web_interface
# Category:** Interface Definitions
# Status:** Active

"""
ImpressionCore: Hardware

Module for hardware functionality in the ImpressionCore framework.

File: web/tests/test_helpers//hardware.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [memory-critical, qa, pytorch, production, testing, web, frontend, 2025, object-oriented]
Dependencies: [torch, typing, numpy]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements hardware functionality for the
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
from web.tests.test_helpers.hardware import HardwareProfile
instance = HardwareProfile()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

import logging
import platform
from typing import Any

import psutil

logger = logging.getLogger(__name__)

class HardwareProfile:
    """Test hardware profile information"""

    def __init__(self):
        """

    __init__ function for processing.

    Args:
        self: Function parameters

    Returns:
        Processed result

    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints

        """
        self.gpu_info = self._get_gpu_info()
        # Memory optimization: Memory-critical operation
        self.memory_info = self._get_memory_info()
        # Memory optimization: Memory-critical operation
        self.cpu_info = self._get_cpu_info()

    def _get_gpu_info(self) -> dict[str, Any]:
    # Memory optimization: Memory-critical operation
        """Get GPU information"""
        # Memory optimization: Memory-critical operation
        try:
            import torch
            if torch.cuda.is_available():
            # Memory optimization: CUDA operations for GPU acceleration
                return {
                    'device': 'cuda',
                    # Memory optimization: Device placement for memory management
                    'name': torch.cuda.get_device_name(0),
                    # Memory optimization: CUDA operations for GPU acceleration
                    'memory_total': torch.cuda.get_device_properties(0).total_memory,
                    # Memory optimization: CUDA operations for GPU acceleration
                    'memory_available': torch.cuda.memory_allocated(0),
                    # Memory optimization: CUDA operations for GPU acceleration
                    'compute_capability': torch.cuda.get_device_capability(0)
                    # Memory optimization: CUDA operations for GPU acceleration
                }
        except ImportError:
            logger.warning("PyTorch not available for GPU detection")
            # Memory optimization: Memory-critical operation
        except Exception as e:
            logger.error(f"Error detecting GPU: {e!s}")
            # Memory optimization: Memory-critical operation

        return {
            'device': 'cpu',
            # Memory optimization: Device placement for memory management
            'name': 'CPU Only',
            'memory_total': 0,
            # Memory optimization: Memory-critical operation
            'memory_available': 0,
            # Memory optimization: Memory-critical operation
            'compute_capability': (0, 0)
        }

    def _get_memory_info(self) -> dict[str, int]:
    # Memory optimization: Memory-critical operation
        """Get system memory information"""
        # Memory optimization: Memory-critical operation
        try:
            vm = psutil.virtual_memory()
            # Memory optimization: Memory-critical operation
            return {
                'total': vm.total,
                'available': vm.available,
                'used': vm.used,
                'free': vm.free
            }
        except Exception as e:
            logger.error(f"Error getting memory info: {e!s}")
            # Memory optimization: Memory-critical operation
            return {
                'total': 0,
                'available': 0,
                'used': 0,
                'free': 0
            }

    def _get_cpu_info(self) -> dict[str, Any]:
        """Get CPU information"""
        try:
            return {
                'cores_physical': psutil.cpu_count(logical=False),
                'cores_logical': psutil.cpu_count(logical=True),
                'frequency': psutil.cpu_freq().current if psutil.cpu_freq() else 0,
                'architecture': platform.machine(),
                'platform': platform.platform()
            }
        except Exception as e:
            logger.error(f"Error getting CPU info: {e!s}")
            return {
                'cores_physical': 0,
                'cores_logical': 0,
                'frequency': 0,
                'architecture': '',
                'platform': ''
            }

    def can_support_model(self, config: dict[str, Any]) -> tuple[bool, str | None]:
        """
        Check if hardware can support the model configuration
        # Memory optimization: Explicit memory cleanup
        Returns (is_supported, reason_if_not_supported)
        """
        try:
            # Calculate memory requirements
            # Memory optimization: Memory-critical operation
            from .validation import estimate_memory_usage
            # Memory optimization: Memory-critical operation
            required_memory = estimate_memory_usage(config)
            # Memory optimization: Memory-critical operation

            # Check available memory
            # Memory optimization: Memory-critical operation
            if self.gpu_info['device'] == 'cuda':
            # Memory optimization: Device placement for memory management
                available_memory = self.gpu_info['memory_total']
                # Memory optimization: Memory-critical operation
                device_name = self.gpu_info['name']
                # Memory optimization: Device placement for memory management
            else:
                available_memory = self.memory_info['available']
                # Memory optimization: Memory-critical operation
                device_name = 'CPU'
                # Memory optimization: Device placement for memory management

            # Add 20% overhead margin
            required_with_overhead = int(required_memory * 1.2)
            # Memory optimization: Memory-critical operation

            if required_with_overhead > available_memory:
            # Memory optimization: Memory-critical operation
                return False, (
                    f"Insufficient memory: Model requires {required_with_overhead / (1024**3):.2f} GB, "
                    # Memory optimization: Explicit memory cleanup
                    f"but only {available_memory / (1024**3):.2f} GB available on {device_name}"
                    # Memory optimization: Device placement for memory management
                )

            return True, None

        except Exception as e:
            logger.error(f"Error checking hardware support: {e!s}")
            return False, f"Error checking hardware support: {e!s}"

    def get_optimal_batch_size(self, config: dict[str, Any]) -> int:
        """Calculate optimal batch size for hardware"""
        try:
            # Start with default batch size

            # Get per-sample memory usage
            # Memory optimization: Memory-critical operation
            from .validation import estimate_memory_usage
            # Memory optimization: Memory-critical operation
            sample_memory = estimate_memory_usage({**config, 'batchSize': 1})
            # Memory optimization: Memory-critical operation

            # Calculate available memory (use 80% of total)
            # Memory optimization: Memory-critical operation
            if self.gpu_info['device'] == 'cuda':
            # Memory optimization: Device placement for memory management
                available_memory = int(self.gpu_info['memory_total'] * 0.8)
                # Memory optimization: Memory-critical operation
            else:
                available_memory = int(self.memory_info['available'] * 0.8)
                # Memory optimization: Memory-critical operation

            # Calculate maximum batch size
            max_batch = available_memory // sample_memory
            # Memory optimization: Memory-critical operation

            # Limit to reasonable sizes
            return min(max_batch, 32)

        except Exception as e:
            logger.error(f"Error calculating batch size: {e!s}")
            return 1

    def estimate_throughput(self, config: dict[str, Any]) -> float | None:
        """
        Estimate samples per second based on hardware
        Returns estimated samples/second or None if estimation fails
        """
        try:
            if self.gpu_info['device'] == 'cuda':
            # Memory optimization: Device placement for memory management
                # Rough GPU throughput estimate based on compute capability
                # Memory optimization: Memory-critical operation
                cc_major, cc_minor = self.gpu_info['compute_capability']
                # Memory optimization: Memory-critical operation
                base_throughput = (cc_major * 10 + cc_minor) * 0.5
            else:
                # CPU throughput estimate based on cores and frequency
                base_throughput = (
                    self.cpu_info['cores_logical'] *
                    (self.cpu_info['frequency'] / 3000.0)  # Normalize to 3 GHz
                )

            # Adjust for model size
            # Memory optimization: Explicit memory cleanup
            num_layers = config['numLayers']
            hidden_size = config['hiddenSize']
            seq_length = config['maxSeqLength']

            # Simple scaling formula
            throughput = base_throughput * (12 / num_layers) * (768 / hidden_size) * (1024 / seq_length)

            return max(0.1, throughput)  # Minimum 0.1 samples/second

        except Exception as e:
            logger.error(f"Error estimating throughput: {e!s}")
            return None
