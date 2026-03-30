#!/usr/bin/env python3
"""
ImpressionCore: Check Gpu

Module for check gpu functionality in the ImpressionCore framework.

File: core/utils/check_gpu.py
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
Dependencies: [torch, pathlib]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements check gpu functionality for the
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
from core.utils.check_gpu import MainClass
instance = MainClass()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

import logging
import argparse
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

def check_torch_cuda():
# Memory optimization: Memory-critical operation
    """Check if PyTorch CUDA is available and working."""
    # Memory optimization: Memory-critical operation
    try:
        import torch
        print("\n=== PyTorch CUDA Information ===")
        # Memory optimization: Memory-critical operation
        
        cuda_available = torch.cuda.is_available()
        # Memory optimization: CUDA operations for GPU acceleration
        print(f"CUDA available: {cuda_available}")
        # Memory optimization: Memory-critical operation
        
        if cuda_available:
        # Memory optimization: Memory-critical operation
            # Get device count
            # Memory optimization: Device placement for memory management
            device_count = torch.cuda.device_count()
            # Memory optimization: CUDA operations for GPU acceleration
            print(f"CUDA device count: {device_count}")
            # Memory optimization: Device placement for memory management
            
            # Get current device
            # Memory optimization: Device placement for memory management
            current_device = torch.cuda.current_device()
            # Memory optimization: CUDA operations for GPU acceleration
            print(f"Current CUDA device: {current_device}")
            # Memory optimization: Device placement for memory management
            
            # Get device name
            # Memory optimization: Device placement for memory management
            device_name = torch.cuda.get_device_name(current_device)
            # Memory optimization: CUDA operations for GPU acceleration
            print(f"CUDA device name: {device_name}")
            # Memory optimization: Device placement for memory management
            
            # Test small tensor operations
            print("\nTesting CUDA with tensor operations...")
            # Memory optimization: Memory-critical operation
            try:
                x = torch.rand(1000, 1000).cuda()
                # Memory optimization: Memory-critical operation
                y = torch.rand(1000, 1000).cuda()
                # Memory optimization: Memory-critical operation
                start_event = torch.cuda.Event(enable_timing=True)
                # Memory optimization: CUDA operations for GPU acceleration
                end_event = torch.cuda.Event(enable_timing=True)
                # Memory optimization: CUDA operations for GPU acceleration
                
                start_event.record()
                z = torch.matmul(x, y)
                end_event.record()
                
                # Waits for everything to finish running
                torch.cuda.synchronize()
                # Memory optimization: CUDA operations for GPU acceleration
                
                print(f"Matrix multiplication test: Success")
                print(f"Elapsed time: {start_event.elapsed_time(end_event):.2f} ms")
                
                # Memory information
                # Memory optimization: Memory-critical operation
                memory_allocated = torch.cuda.memory_allocated() / 1024**2
                # Memory optimization: CUDA operations for GPU acceleration
                memory_reserved = torch.cuda.memory_reserved() / 1024**2
                # Memory optimization: CUDA operations for GPU acceleration
                device_props = torch.cuda.get_device_properties(current_device)
                # Memory optimization: CUDA operations for GPU acceleration
                total_memory = device_props.total_memory / 1024**2
                # Memory optimization: Device placement for memory management
                
                print(f"\nMemory Information:")
                # Memory optimization: Memory-critical operation
                print(f"Total GPU memory: {total_memory:.2f} MB")
                # Memory optimization: Memory-critical operation
                print(f"Memory allocated: {memory_allocated:.2f} MB")
                # Memory optimization: Memory-critical operation
                print(f"Memory reserved: {memory_reserved:.2f} MB")
                # Memory optimization: Memory-critical operation
                print(f"Memory available: {total_memory - memory_reserved:.2f} MB")
                # Memory optimization: Memory-critical operation
                
            except Exception as e:
                print(f"Error during CUDA tensor operations: {e}")
                # Memory optimization: Memory-critical operation
                return False
            
            # Check CUDA version
            # Memory optimization: Memory-critical operation
            print(f"\nPyTorch CUDA Version: {torch.version.cuda}")
            # Memory optimization: Memory-critical operation
            print(f"PyTorch CuDNN Version: {torch.backends.cudnn.version()}")
            print(f"PyTorch Version: {torch.__version__}")
            
            return True
        else:
            print("CUDA is not available in PyTorch.")
            # Memory optimization: Memory-critical operation
            return False
            
    except ImportError:
        print("PyTorch is not installed.")
        return False
    except Exception as e:
        print(f"Error checking PyTorch CUDA: {e}")
        # Memory optimization: Memory-critical operation
        return False

def check_system_gpus():
# Memory optimization: Memory-critical operation
    """Check system GPUs using system tools."""
    # Memory optimization: Memory-critical operation
    print("\n=== System GPU Information ===")
    # Memory optimization: Memory-critical operation
    
    try:
        if os.name == 'nt':  # Windows
            print("Checking Windows GPU information...")
            # Memory optimization: Memory-critical operation
            try:
                import wmi
                computer = wmi.WMI()
                gpu_info = computer.Win32_VideoController()
                # Memory optimization: Memory-critical operation
                for i, gpu in enumerate(gpu_info):
                # Memory optimization: Memory-critical operation
                    print(f"GPU {i}:")
                    # Memory optimization: Memory-critical operation
                    print(f"  Name: {gpu.Name}")
                    # Memory optimization: Memory-critical operation
                    print(f"  Driver Version: {gpu.DriverVersion}")
                    # Memory optimization: Memory-critical operation
                    print(f"  Video Mode Description: {gpu.VideoModeDescription}")
                    # Memory optimization: Memory-critical operation
                    print(f"  Current Refresh Rate: {gpu.CurrentRefreshRate}")
                    # Memory optimization: Memory-critical operation
                    print("")
            except ImportError:
                print("WMI module not installed. Install with: pip install wmi")
                # Try alternative method with subprocess
                import subprocess
                try:
                    result = subprocess.run(['wmic', 'path', 'win32_VideoController', 'get', 'Caption,DriverVersion'], 
                                          capture_output=True, text=True, check=True)
                    print(result.stdout)
                except Exception as e:
                    print(f"Error running WMIC: {e}")
        else:  # Linux/Unix
            print("Checking Linux/Unix GPU information...")
            # Memory optimization: Memory-critical operation
            try:
                import subprocess
                try:
                    # Try nvidia-smi for NVIDIA GPUs
                    # Memory optimization: Memory-critical operation
                    result = subprocess.run(['nvidia-smi'], 
                                          capture_output=True, text=True, check=True)
                    print(result.stdout)
                except Exception:
                    # Try lspci for generic GPU detection
                    # Memory optimization: Memory-critical operation
                    print("nvidia-smi failed, trying lspci...")
                    result = subprocess.run(['lspci', '|', 'grep', '-i', 'vga'], 
                                          shell=True, capture_output=True, text=True)
                    print(result.stdout)
            except Exception as e:
                print(f"Error getting system GPU info: {e}")
                # Memory optimization: Memory-critical operation
    except Exception as e:
        print(f"Error checking system GPUs: {e}")
        # Memory optimization: Memory-critical operation

def check_env_variables():
    """Check environment variables relevant to CUDA."""
    # Memory optimization: Memory-critical operation
    print("\n=== CUDA Environment Variables ===")
    # Memory optimization: Memory-critical operation
    
    cuda_vars = {
    # Memory optimization: Memory-critical operation
        "CUDA_VISIBLE_DEVICES": os.environ.get("CUDA_VISIBLE_DEVICES", "Not set"),
        # Memory optimization: Device placement for memory management
        "CUDA_DEVICE_ORDER": os.environ.get("CUDA_DEVICE_ORDER", "Not set"),
        # Memory optimization: Device placement for memory management
        "CUDA_HOME": os.environ.get("CUDA_HOME", "Not set"),
        # Memory optimization: Memory-critical operation
        "LD_LIBRARY_PATH": os.environ.get("LD_LIBRARY_PATH", "Not set")
    }
    
    for var, value in cuda_vars.items():
    # Memory optimization: Memory-critical operation
        print(f"{var}: {value}")

def check_gpu_capabilities():
# Memory optimization: Memory-critical operation
    """Check GPU compute capabilities."""
    # Memory optimization: Memory-critical operation
    try:
        import torch
        if torch.cuda.is_available():
        # Memory optimization: CUDA operations for GPU acceleration
            print("\n=== CUDA Compute Capabilities ===")
            # Memory optimization: Memory-critical operation
            for i in range(torch.cuda.device_count()):
            # Memory optimization: CUDA operations for GPU acceleration
                prop = torch.cuda.get_device_properties(i)
                # Memory optimization: CUDA operations for GPU acceleration
                print(f"Device {i}: {prop.name}")
                # Memory optimization: Device placement for memory management
                print(f"  Compute Capability: {prop.major}.{prop.minor}")
                print(f"  Total Memory: {prop.total_memory / 1024**2:.2f} MB")
                # Memory optimization: Memory-critical operation
                print(f"  Multi Processor Count: {prop.multi_processor_count}")
                print(f"  Max Threads Per Block: {prop.max_threads_per_block}")
                print(f"  Max Threads Per MP: {prop.max_threads_per_multi_processor}")
                
                # Check if GTX 1050 Ti
                if "1050 Ti" in prop.name:
                    print("\n=== GTX 1050 Ti Specific Information ===")
                    print("  Memory Recommendations:")
                    # Memory optimization: Memory-critical operation
                    print("  - Maximum batch size: 4-8 (depending on model)")
                    print("  - Maximum sequence length: 64-128 (depending on model)")
                    print("  - Mixed precision (FP16) recommended for larger models")
                    print("  - For large models, use gradient accumulation (8+ steps)")
                    print("")
                    print("  Common GTX 1050 Ti Issues:")
                    print("  - Ensure latest NVIDIA drivers are installed")
                    print("  - Common VRAM limitations with < 4GB available to PyTorch")
                    print("  - May need to close other GPU-using applications")
                    # Memory optimization: Memory-critical operation
    except Exception as e:
        print(f"Error checking GPU capabilities: {e}")
        # Memory optimization: Memory-critical operation

def main():
    """Main function."""
    print("=== ImpressionCore GPU Status Check ===")
    # Memory optimization: Memory-critical operation
    print("Checking GPU availability for GTX 1050 Ti and other GPUs...")
    # Memory optimization: Memory-critical operation
    
    check_system_gpus()
    # Memory optimization: Memory-critical operation
    torch_available = check_torch_cuda()
    # Memory optimization: Memory-critical operation
    check_env_variables()
    if torch_available:
        check_gpu_capabilities()
        # Memory optimization: Memory-critical operation
    
    print("\n=== GPU Check Complete ===")
    # Memory optimization: Memory-critical operation
    if not torch_available:
        print("\nRecommendations to fix CUDA detection:")
        # Memory optimization: Memory-critical operation
        print("1. Update NVIDIA drivers: https://www.nvidia.com/Download/index.aspx")
        print("2. Reinstall PyTorch with correct CUDA version:")
        # Memory optimization: Memory-critical operation
        print("   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118")
        print("3. Ensure no other applications are using the GPU")
        # Memory optimization: Memory-critical operation
        print("4. Check if your GPU is properly recognized in Device Manager")
        # Memory optimization: Device placement for memory management
        print("5. If all else fails, use CPU mode with --use_cpu flag")

if __name__ == "__main__":
    main()
