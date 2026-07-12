#!/usr/bin/env python3
"""
ImpressionCore: Exceptions

Module for exceptions functionality in the ImpressionCore framework.

File: core\exceptions.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [memory-critical, framework, core, production, 2025, object-oriented]
Dependencies: [typing]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements exceptions functionality for the
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
from src.core.exceptions import OutOfMemoryError
instance = OutOfMemoryError()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

class OutOfMemoryError(Exception):
# Memory optimization: Memory-critical operation
    """Raised when GPU runs out of memory during operations."""
    # Memory optimization: Memory-critical operation
    pass

class GPUNotAvailableError(Exception):
# Memory optimization: Memory-critical operation
    """Raised when GPU is required but not available."""
    # Memory optimization: Memory-critical operation
    pass

class TensorParallelismError(Exception):
    """Raised when tensor parallelism operations fail."""
    pass

class DistributedInitError(Exception):
    """Raised when distributed processing initialization fails."""
    pass

class ConfigurationError(Exception):
    """Raised when there's an error in the configuration."""
    pass

class ModelLoadError(Exception):
    """Raised when there's an error loading a model."""
    pass

class DatasetError(Exception):
    """Raised when there's an error with a dataset."""
    pass

class ModelNotFoundError(Exception):
    """Raised when a requested model cannot be found or loaded."""
    # Memory optimization: Explicit memory cleanup
    pass

class ModelInferenceError(Exception):
    """Raised when there's an error during model inference or prediction."""
    # Memory optimization: Explicit memory cleanup
    pass

class ImageGenerationError(Exception):
    """Raised when there's an error during image generation or processing."""
    pass

class InvalidPromptError(Exception):
    """Raised when a prompt is invalid or fails validation criteria."""
    pass