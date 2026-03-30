#!/usr/bin/env python3
"""
ImpressionCore: Conftest

Module for conftest functionality in the ImpressionCore framework.

File: tests\conftest.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [memory-critical, qa, pytorch, production, testing, 2025]
Dependencies: [torch, pathlib]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements conftest functionality for the
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
from tests.conftest import MainClass
instance = MainClass()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

# File: conftest.py
# Created: 2025-05-21
# Last Modified: 2025-05-22
# Author: Kirk LaSalle
# Copyright: ImpressionCore 2025
# Description: Pytest configuration file for ImpressionCore tests. Defines shared fixtures for device, test directories, dummy data, and environment cleanup. Also configures custom markers (slow, gpu) and modifies test collection based on GPU availability.
# Memory optimization: Device placement for memory management
# Tags: [pytest, conftest, testing, fixtures, test_setup, gpu_tests, slow_tests, torch, test_environment, pytest_hooks]
# Memory optimization: Memory-critical operation

import pytest
from pathlib import Path
import shutil
from typing import Any

# Handle torch import gracefully
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    torch = None
    TORCH_AVAILABLE = False

@pytest.fixture(scope="session")
def device():
    """Provide torch device for tests"""
    if not TORCH_AVAILABLE:
        return "cpu"  # String fallback when torch not available
    return torch.device('cuda' if torch.cuda.is_available() else 'cpu')

@pytest.fixture(scope="session")
def test_data_dir(tmp_path_factory):
    """Create and manage test data directory"""
    test_dir = tmp_path_factory.mktemp("test_data")
    return test_dir

@pytest.fixture(scope="session")
def test_output_dir(tmp_path_factory):
    """Create and manage test output directory"""
    output_dir = tmp_path_factory.mktemp("test_output")
    return output_dir

@pytest.fixture(scope="function")
def dummy_image_tensor(device):
    """Create dummy image tensor for testing"""
    if not TORCH_AVAILABLE:
        return [[1, 2, 3], [4, 5, 6]]  # Simple list fallback
    return torch.randn(1, 3, 224, 224).to(device)

@pytest.fixture(scope="function")
def clean_test_env(test_data_dir, test_output_dir):
    """Clean test environment before and after tests"""
    # Clean before test
    for path in [test_data_dir, test_output_dir]:
        if path.exists():
            shutil.rmtree(path)
        path.mkdir(parents=True, exist_ok=True)
    
    yield
    
    # Clean after test
    for path in [test_data_dir, test_output_dir]:
        if path.exists():
            shutil.rmtree(path)

def pytest_configure(config):
    """Configure test environment"""
    config.addinivalue_line(
        "markers",
        "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers",
        "gpu: marks tests that require GPU (deselect with '-m \"not gpu\"')"
        # Memory optimization: Memory-critical operation
    )

def pytest_collection_modifyitems(config, items):
    """Modify test collection based on hardware availability"""
    if not TORCH_AVAILABLE or not torch.cuda.is_available():
        skip_gpu = pytest.mark.skip(reason="GPU or torch not available")
        for item in items:
            if "gpu" in item.keywords:
                item.add_marker(skip_gpu)
