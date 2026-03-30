#!/usr/bin/env python3
"""
ImpressionCore: Assistant Tests Module

Test module initialization for the personal assistant components.

File: src/tests/assistant/__init__.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-31
Modified: 2025-05-31
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [tests, assistant, init, 2025]
Dependencies: [pytest]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module provides test initialization for the personal assistant components,
ensuring proper test discovery and configuration for pytest.
"""

# Test module metadata
__version__ = "1.0.0"
__author__ = "ImpressionCore Development Team"
__license__ = "MIT"
__description__ = "Assistant Tests for ImpressionCore"

# Test configuration
TEST_TIMEOUT = 30  # Maximum test timeout in seconds
MEMORY_LIMIT_MB = 100  # Memory limit for tests
PERFORMANCE_THRESHOLD = 2.0  # Performance threshold in seconds

# Test exports
__all__ = [
    "__version__",
    "__author__", 
    "__license__",
    "__description__",
    "TEST_TIMEOUT",
    "MEMORY_LIMIT_MB",
    "PERFORMANCE_THRESHOLD"
]
