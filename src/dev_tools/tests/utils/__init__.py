#!/usr/bin/env python3
"""
ImpressionCore: Test Utils Init

Test utilities package initialization.

File: tests/utils/__init__.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-06-01
Modified: 2025-06-01
Version: 1.0.0

Authors:
- GitHub Copilot
- Development Team

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [testing, utilities, 2025]
Dependencies: [torch]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
Test utilities package for ImpressionCore testing framework.
"""

from .mock_models import (
    create_test_model,
    create_small_test_model,
    create_large_test_model,
    get_model_parameter_count,
    get_model_memory_footprint,
    MockTransformerModel,
    MockTransformerLayer
)

from .memory_utils import (
    MemoryProfiler,
    MemorySnapshot,
    MemoryBudget,
    memory_profiled,
    estimate_tensor_memory,
    get_model_memory_footprint,
    check_gpu_memory_available,
    optimize_memory_for_testing
)

__all__ = [
    # Mock models
    'create_test_model',
    'create_small_test_model',
    'create_large_test_model',
    'get_model_parameter_count',
    'get_model_memory_footprint',
    'MockTransformerModel',
    'MockTransformerLayer',
    
    # Memory utilities
    'MemoryProfiler',
    'MemorySnapshot',
    'MemoryBudget',
    'memory_profiled',
    'estimate_tensor_memory',
    'check_gpu_memory_available',
    'optimize_memory_for_testing'
]
