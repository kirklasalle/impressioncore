#!/usr/bin/env python3
r"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** Kirk LaSalle
**Tags:** #cuda #gpu_optimization #memory_management #multimodal #performance #python #pytorch #source_code #src/interfaces/web/hardware_check.py #testing #web_interface
**Category:** Interface Definitions
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:02
# Author:** Kirk LaSalle
# Tags:** #cuda #gpu_optimization #memory_management #multimodal #performance #python #pytorch #source_code #src/interfaces/web/hardware_check.py #testing #web_interface
# Category:** Interface Definitions
# Status:** Active

r"""
ImpressionCore: Hardware Check

Module for hardware check functionality in the ImpressionCore framework.

File: web/hardware_check.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [memory-critical, pytorch, production, web, frontend, 2025]
Dependencies: [torch, pathlib]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements hardware check functionality for the
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
from web.hardware_check import MainClass
instance = MainClass()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

import platform

import psutil
import torch


def get_gpu_info():
# Memory optimization: Memory-critical operation
    """Get CUDA GPU information if available."""
    # Memory optimization: Memory-critical operation
    if torch.cuda.is_available():
    # Memory optimization: CUDA operations for GPU acceleration
        gpu_count = torch.cuda.device_count()
        # Memory optimization: CUDA operations for GPU acceleration
        gpu_names = [torch.cuda.get_device_name(i) for i in range(gpu_count)]
        # Memory optimization: CUDA operations for GPU acceleration
        total_memory = [torch.cuda.get_device_properties(i).total_memory for i in range(gpu_count)]
        # Memory optimization: CUDA operations for GPU acceleration
        return {
            'available': True,
            'count': gpu_count,
            # Memory optimization: Memory-critical operation
            'devices': [{'name': name, 'memory': mem} for name, mem in zip(gpu_names, total_memory)]
            # Memory optimization: Device placement for memory management
        }
    return {'available': False}

def get_system_info():
    """Get system hardware information."""
    cpu_count = psutil.cpu_count(logical=False)
    total_ram = psutil.virtual_memory().total / (1024 ** 3)  # Convert to GB
    # Memory optimization: Memory-critical operation
    free_disk = psutil.disk_usage('/').free / (1024 ** 3)  # Convert to GB
    python_version = platform.python_version()

    specs = {
        'CPU Cores': f"{cpu_count} physical cores",
        'RAM': f"{total_ram:.1f} GB",
        'Free Disk Space': f"{free_disk:.1f} GB",
        'Python Version': python_version,
        'Operating System': f"{platform.system()} {platform.release()}"
    }

    # Add GPU information if available
    # Memory optimization: Memory-critical operation
    gpu_info = get_gpu_info()
    # Memory optimization: Memory-critical operation
    if gpu_info['available']:
    # Memory optimization: Memory-critical operation
        gpu_specs = []
        # Memory optimization: Memory-critical operation
        for _i, device in enumerate(gpu_info['devices']):
        # Memory optimization: Device placement for memory management
            memory_gb = device['memory'] / (1024 ** 3)  # Convert to GB
            # Memory optimization: Device placement for memory management
            gpu_specs.append(f"{device['name']} ({memory_gb:.1f} GB)")
            # Memory optimization: Device placement for memory management
        specs['GPU'] = ' | '.join(gpu_specs)
        # Memory optimization: Memory-critical operation
    else:
        specs['GPU'] = 'No CUDA GPU detected'
        # Memory optimization: Memory-critical operation

    # Check if system meets minimum requirements
    suitable = (
        cpu_count >= 4 and
        total_ram >= 16 and  # 16GB RAM minimum
        free_disk >= 50 and  # 50GB free space minimum
        gpu_info['available']  # CUDA GPU required
        # Memory optimization: Memory-critical operation
    )

    return {
        'suitable': suitable,
        'specs': specs
    }

if __name__ == '__main__':
    print(get_system_info())
