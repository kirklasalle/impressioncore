#!/usr/bin/env python3
"""
ImpressionCore: Main Package

Main package initialization for the ImpressionCore framework.

File: __init__.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-06-06
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [production, 2025]
Dependencies: [typing]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
Main package initialization for the ImpressionCore brain-inspired multimodal AI framework. 
Optimized for memory-constrained environments and designed to run efficiently on consumer hardware.

Design Philosophy:
- Memory-efficient implementation for GTX 1050 Ti constraints
- Modular design for easy extension and maintenance
- Rich logging and error handling
- Integration with ImpressionCore ecosystem

Examples:
```python
# Basic usage examples
import src.core.config
import src.training.models
import src.services.api
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

# ImpressionCore package initialization

# Import core modules with error handling
try:
    from . import core
except ImportError as e:
    print(f"Warning: Could not import core module: {e}")

try:
    from . import training
except ImportError as e:
    print(f"Warning: Could not import training module: {e}")

try:
    from . import services
except ImportError as e:
    print(f"Warning: Could not import services module: {e}")

try:
    from . import interfaces
except ImportError as e:
    print(f"Warning: Could not import interfaces module: {e}")

try:
    from . import data
except ImportError as e:
    print(f"Warning: Could not import data module: {e}")

__version__ = "1.0.0"
__all__ = [
    'core',
    'training', 
    'services',
    'interfaces',
    'data',
]
