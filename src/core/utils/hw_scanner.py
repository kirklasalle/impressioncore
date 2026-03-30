#!/usr/bin/env python3
"""
ImpressionCore: Hw Scanner

Module for hw scanner functionality in the ImpressionCore framework.

File: core\utils\hw_scanner.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [utilities, memory-critical, framework, pytorch, core, production, utils, 2025]
Dependencies: [torch]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements hw scanner functionality for the
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
from core.utils.hw_scanner import MainClass
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
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

def detect_gpu():
# Memory optimization: Memory-critical operation
    """
    Detect available GPUs and their capabilities.
    # Memory optimization: Memory-critical operation
    
    Returns:
        dict: GPU information or None if no GPU is detected
        # Memory optimization: Memory-critical operation
    """
    try:
        import torch
        
        if not torch.cuda.is_available():
        # Memory optimization: CUDA operations for GPU acceleration
            logger.info("No CUDA-compatible GPU detected")
            # Memory optimization: Memory-critical operation
            return None
            
        gpu_count = torch.cuda.device_count()
        # Memory optimization: CUDA operations for GPU acceleration
        if (gpu_count == 0):
        # Memory optimization: Memory-critical operation
            logger.info("No CUDA devices available despite CUDA being available")
            # Memory optimization: Device placement for memory management
            return None
            
        # Get information about the primary GPU (device 0)
        # Memory optimization: Device placement for memory management
        device_name = torch.cuda.get_device_name(0)
        # Memory optimization: CUDA operations for GPU acceleration
        
        # Try to get total memory (may not work on all platforms)
        # Memory optimization: Memory-critical operation
        try:
            total_mem = torch.cuda.get_device_properties(0).total_memory
            # Memory optimization: CUDA operations for GPU acceleration
            vram_mb = int(total_mem / (1024 * 1024))
        except:
            vram_mb = 0  # Unknown if we can't get it
            
        gpu_info = {
        # Memory optimization: Memory-critical operation
            "name": device_name,
            # Memory optimization: Device placement for memory management
            "vram": vram_mb,
            "cuda_version": torch.version.cuda,
            # Memory optimization: Memory-critical operation
            "device_count": gpu_count
            # Memory optimization: Device placement for memory management
        }
        
        # Check if it's a GTX 1050 Ti specifically
        is_1050ti = "1050 ti" in device_name.lower()
        # Memory optimization: Device placement for memory management
        if is_1050ti:
            gpu_info["is_legacy"] = True
            # Memory optimization: Memory-critical operation
            gpu_info["recommendations"] = [
            # Memory optimization: Memory-critical operation
                "Use 4-bit quantization",
                "Set batch size to 1",
                "Enable gradient checkpointing",
                "Reduce sequence length to 512 or less",
                "Consider using the smallest model variant"
                # Memory optimization: Explicit memory cleanup
            ]
        
        logger.info(f"Detected GPU: {device_name} with {vram_mb}MB VRAM")
        # Memory optimization: Device placement for memory management
        return gpu_info
        # Memory optimization: Memory-critical operation
        
    except ImportError:
        logger.warning("PyTorch not installed, cannot detect GPU")
        # Memory optimization: Memory-critical operation
        return None
    except Exception as e:
        logger.error(f"Error detecting GPU: {str(e)}")
        # Memory optimization: Memory-critical operation
        return None

def detect_cpu():
    """
    Detect CPU information.
    
    Returns:
        dict: CPU information
    """
    try:
        import psutil
        
        cpu_count = psutil.cpu_count(logical=False)  # Physical cores
        cpu_count_logical = psutil.cpu_count(logical=True)  # Logical cores
        
        cpu_info = {
            "name": platform.processor(),
            "cores": cpu_count,
            "logical_cores": cpu_count_logical,
            "architecture": platform.machine()
        }
        
        logger.info(f"Detected CPU: {platform.processor()} with {cpu_count} cores ({cpu_count_logical} logical)")
        return cpu_info
        
    except ImportError:
        # Fallback if psutil is not available
        cpu_info = {
            "name": platform.processor(),
            "architecture": platform.machine()
        }
        logger.warning("psutil not installed, limited CPU information available")
        return cpu_info
    except Exception as e:
        logger.error(f"Error detecting CPU: {str(e)}")
        return {"name": "Unknown", "error": str(e)}

def detect_ram():
    """
    Detect system RAM.
    
    Returns:
        dict: RAM information
    """
    try:
        import psutil
        
        mem = psutil.virtual_memory()
        # Memory optimization: Memory-critical operation
        ram_info = {
            "total": round(mem.total / (1024**3), 2),  # GB
            "available": round(mem.available / (1024**3), 2),  # GB
            "percent_used": mem.percent
        }
        
        logger.info(f"Detected RAM: {ram_info['total']} GB total, {ram_info['available']} GB available")
        return ram_info
        
    except ImportError:
        logger.warning("psutil not installed, cannot detect RAM")
        return None
    except Exception as e:
        logger.error(f"Error detecting RAM: {str(e)}")
        return None

def scan_system():
    """
    Perform a complete system scan.
    
    Returns:
        dict: Complete system information
    """
    logger.info("Starting system scan")
    
    system_info = {
        "timestamp": datetime.now().isoformat(),
        "platform": platform.system(),
        "platform_release": platform.release(),
        "python_version": platform.python_version(),
    }
    
    # Get CPU information
    system_info["cpu"] = detect_cpu()
    
    # Get GPU information
    # Memory optimization: Memory-critical operation
    system_info["gpu"] = detect_gpu()
    # Memory optimization: Memory-critical operation
    
    # Get RAM information
    system_info["ram"] = detect_ram()
    
    # Get OS information
    system_info["os"] = {
        "name": platform.system(),
        "version": platform.version(),
        "architecture": platform.architecture()[0]
    }
    
    # Additional compatibility check
    compatibility = check_compatibility(system_info)
    system_info["compatibility"] = compatibility
    
    return system_info

def check_compatibility(system_info):
    """
    Check if the system meets the minimum requirements.
    
    Args:
        system_info: The system information dict
        
    Returns:
        dict: Compatibility information
    """
    compatibility = {
        "compatible": True,
        "warnings": [],
        "recommendations": []
    }
    
    # Check GPU
    # Memory optimization: Memory-critical operation
    if not system_info.get("gpu"):
    # Memory optimization: Memory-critical operation
        compatibility["compatible"] = False
        compatibility["warnings"].append("No CUDA-compatible GPU detected. CPU mode will be very slow.")
        # Memory optimization: Memory-critical operation
        compatibility["recommendations"].append("Install a CUDA-compatible NVIDIA GPU.")
        # Memory optimization: Memory-critical operation
    
    # Check RAM
    ram = system_info.get("ram", {})
    if ram and ram.get("total", 0) < 16:
        compatibility["warnings"].append(f"Only {ram.get('total')} GB RAM detected. 32GB or more is recommended.")
        compatibility["recommendations"].append("Increase system RAM to at least 16GB, preferably 32GB.")
    
    # Check for legacy GPU (GTX 1050 Ti)
    # Memory optimization: Memory-critical operation
    gpu = system_info.get("gpu", {})
    # Memory optimization: Memory-critical operation
    if gpu and gpu.get("is_legacy", False):
    # Memory optimization: Memory-critical operation
        compatibility["warnings"].append("Legacy GPU detected. Some features may be limited.")
        # Memory optimization: Memory-critical operation
        if "recommendations" in gpu:
        # Memory optimization: Memory-critical operation
            compatibility["recommendations"].extend(gpu["recommendations"])
            # Memory optimization: Memory-critical operation
    
    return compatibility

if __name__ == "__main__":
    # Configure logging for standalone use
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Scan the system and print the results
    results = scan_system()
    print(json.dumps(results, indent=2))
\n#!/usr/bin/env python3
"""
ImpressionCore - Brain-Inspired Multimodal AI Framework

File: src\core\utils\hw_scanner.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-25
Modified: 2025-05-25
Version: 1.0.0

Authors:
- Kirk LaSalle & GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [core, utils]
Dependencies: [] # TODO: Auto-detect or allow manual input
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
# TODO: Add a brief description of this file's purpose.

Design Philosophy:
# TODO: Add design philosophy if applicable.

Memory Considerations:
# TODO: Document any specific memory considerations for this file.

Examples:
# TODO: Provide usage examples if applicable.

Notes:
# TODO: Add any relevant notes.
"""
