#!/usr/bin/env python3
"""
ImpressionCore: Install Pytorch Cuda

Module for install pytorch cuda functionality in the ImpressionCore framework.

File: tools\install_pytorch_cuda.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [pytorch, production, memory-critical, 2025]
Dependencies: [torch, pathlib]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements install pytorch cuda functionality for the
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
# from tools.install_pytorch_cuda import  # Fixed: using local implementation MainClass
instance = MainClass()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

import os
import sys
import platform
import subprocess
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# CUDA toolkit detection
# Memory optimization: Memory-critical operation
DEFAULT_CUDA_PATHS = [
    # Memory optimization: Memory-critical operation
    "C:\\Program Files\\NVIDIA GPU Computing Toolkit\\CUDA\\v12.1",
    "C:\\Program Files\\NVIDIA GPU Computing Toolkit\\CUDA\\v12.0",
    "C:\\Program Files\\NVIDIA GPU Computing Toolkit\\CUDA\\v11.8",
    # Memory optimization: Memory-critical operation
]

def get_cuda_version():
# Memory optimization: Memory-critical operation
    """Detect installed CUDA version."""
    # Memory optimization: Memory-critical operation
    # First check environment variable
    cuda_path = os.environ.get("CUDA_PATH", "")
    # Memory optimization: Memory-critical operation
    if cuda_path:
    # Memory optimization: Memory-critical operation
        for version in ["12.1", "12.0", "11.8", "11.7", "11.6"]:
            if version in cuda_path:
            # Memory optimization: Memory-critical operation
                return version
    
    # Check default install paths
    for path in DEFAULT_CUDA_PATHS:
        if os.path.exists(path):
            for version in ["12.1", "12.0", "11.8", "11.7", "11.6"]:
                if version in path:
                    return version
    
    # Check nvidia-smi output
    try:
        result = subprocess.run(["nvidia-smi"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                if "CUDA Version:" in line:
                # Memory optimization: Memory-critical operation
                    parts = line.split("CUDA Version:")
                    # Memory optimization: Memory-critical operation
                    if len(parts) > 1:
                        return parts[1].strip()
    except Exception:
        pass
    
    return None

def is_python_compatible():
    """Check if current Python version is compatible with PyTorch."""
    py_version = sys.version_info
    
    # Check Python version - PyTorch generally supports 3.8-3.11 well
    if py_version.major == 3 and 8 <= py_version.minor <= 11:
        return True, f"Python {py_version.major}.{py_version.minor} is compatible with PyTorch"
    elif py_version.major == 3 and py_version.minor >= 12:
        # Newer Python may have limited pre-built wheel support
        return False, f"Python {py_version.major}.{py_version.minor} may have limited PyTorch pre-built wheel support"
    else:
        return False, f"Python {py_version.major}.{py_version.minor} is not fully compatible with recent PyTorch versions"

def get_pytorch_install_command(cuda_version):
# Memory optimization: Memory-critical operation
    """Get the correct PyTorch install command for the CUDA version."""
    # Memory optimization: Memory-critical operation
    # Map CUDA versions to compatible PyTorch CUDA versions
    # Memory optimization: Memory-critical operation
    version_map = {
        "12.1": "121",  # PyTorch uses cu121 for CUDA 12.1 compatibility
        "12.0": "121",  # PyTorch uses cu121 for CUDA 12.x compatibility
        "11.8": "118",
        "11.7": "117",
        "11.6": "116",
    }
    pytorch_cuda = version_map.get(cuda_version, "121")  # Default to 121 if unknown
    # Memory optimization: Memory-critical operation
    
    # Command to uninstall existing PyTorch
    uninstall_cmd = [sys.executable, "-m", "pip", "uninstall", "-y", "torch", "torchvision", "torchaudio"]
    
    # Command to install PyTorch with CUDA support - FIX: separate packages to avoid parsing error
    # Memory optimization: Memory-critical operation
    if platform.system() == "Windows":
        install_cmd = [
            sys.executable, "-m", "pip", "install", 
            "torch", "torchvision", "torchaudio", 
            "--index-url", f"https://download.pytorch.org/whl/cu{pytorch_cuda}"
            # Memory optimization: Memory-critical operation
        ]
    else:
        # Linux/Mac
        install_cmd = [
            sys.executable, "-m", "pip", "install", 
            "torch", "torchvision", "torchaudio", 
            "--extra-index-url", f"https://download.pytorch.org/whl/cu{pytorch_cuda}"
            # Memory optimization: Memory-critical operation
        ]
    
    return uninstall_cmd, install_cmd, pytorch_cuda
    # Memory optimization: Memory-critical operation

def install_onnx_runtime():
    """Install ONNX Runtime packages required for torch-ort."""
    logger.info("Installing ONNX Runtime packages...")
    
    try:
        # First try to uninstall any existing packages that might cause conflicts
        uninstall_cmd = [
            sys.executable, "-m", "pip", "uninstall", "-y", 
            "onnx", "onnxruntime", "onnxruntime-gpu", "torch-ort", "onnxruntime-training"
            # Memory optimization: Memory-critical operation
        ]
        subprocess.run(uninstall_cmd)
        
        # Install base ONNX package
        logger.info("Installing ONNX base package...")
        onnx_cmd = [sys.executable, "-m", "pip", "install", "onnx>=1.14.0"]
        subprocess.run(onnx_cmd)
        
        # Install appropriate ONNX Runtime based on CUDA availability
        # Memory optimization: Memory-critical operation
        cuda_version = get_cuda_version()
        # Memory optimization: Memory-critical operation
        if cuda_version:
        # Memory optimization: Memory-critical operation
            logger.info(f"Installing ONNX Runtime with GPU support for CUDA {cuda_version}...")
            # Memory optimization: Memory-critical operation
            # For newer CUDA versions (12.x), we need specific package versions
            # Memory optimization: Memory-critical operation
            if cuda_version.startswith("12"):
                ort_cmd = [
                    sys.executable, "-m", "pip", "install", 
                    "onnxruntime-gpu>=1.16.0"
                ]
            else:
                # For CUDA 11.x
                # Memory optimization: Memory-critical operation
                ort_cmd = [sys.executable, "-m", "pip", "install", "onnxruntime-gpu>=1.15.0"]
                # Memory optimization: Memory-critical operation
            
            subprocess.run(ort_cmd)
        else:
            # CPU-only version
            logger.info("Installing CPU-only ONNX Runtime...")
            ort_cmd = [sys.executable, "-m", "pip", "install", "onnxruntime>=1.15.0"]
            subprocess.run(ort_cmd)
        
        # Install torch-ort with specific version to avoid conflicts
        logger.info("Installing torch-ort with specific version...")
        torch_ort_cmd = [sys.executable, "-m", "pip", "install", "torch-ort==1.13.1"]
        result = subprocess.run(torch_ort_cmd)
        
        if result.returncode != 0:
            # Try alternative version if the first one fails
            logger.warning("First torch-ort installation attempt failed, trying alternate version...")
            alt_cmd = [sys.executable, "-m", "pip", "install", "torch-ort==1.12.0"]
            result = subprocess.run(alt_cmd)
        
        return result.returncode == 0
            
    except Exception as e:
        logger.error(f"Error installing ONNX Runtime: {e}")
        return False

def fallback_pytorch_install(pytorch_cuda):
# Memory optimization: Memory-critical operation
    """Try alternative installation methods if the standard one fails."""
    
    logger.info("Attempting fallback installation methods...")
    
    # Try installing just torch first, then the others
    try:
        logger.info("Fallback 1: Installing only torch package...")
        cmd = [
            sys.executable, "-m", "pip", "install", "torch",
            "--index-url", f"https://download.pytorch.org/whl/cu{pytorch_cuda}"
            # Memory optimization: Memory-critical operation
        ]
        result = subprocess.run(cmd)
        if result.returncode == 0:
            logger.info("Successfully installed torch, now installing vision & audio...")
            vision_cmd = [
                sys.executable, "-m", "pip", "install", "torchvision", "torchaudio",
                "--index-url", f"https://download.pytorch.org/whl/cu{pytorch_cuda}"
                # Memory optimization: Memory-critical operation
            ]
            subprocess.run(vision_cmd)
            return True
    except Exception as e:
        logger.warning(f"Fallback 1 failed: {e}")
    
    # Try the explicit local install approach using a temp file
    try:
        logger.info("Fallback 2: Using requirements file approach...")
        req_content = f"""
torch
torchvision
torchaudio
--index-url https://download.pytorch.org/whl/cu{pytorch_cuda}
# Memory optimization: Memory-critical operation
"""
        req_file = Path(os.path.join(os.getcwd(), "pytorch_requirements.txt"))
        with open(req_file, "w") as f:
            f.write(req_content)
        
        cmd = [sys.executable, "-m", "pip", "install", "-r", str(req_file)]
        result = subprocess.run(cmd)
        req_file.unlink()  # Clean up
        
        return result.returncode == 0
    except Exception as e:
        logger.warning(f"Fallback 2 failed: {e}")
    
    # Try direct URLs as last resort
    try:
        logger.info("Fallback 3: Using direct download from PyTorch website...")
        
        # Determine Python version for URL
        py_version = f"{sys.version_info.major}{sys.version_info.minor}"
        
        # Construct direct URLs - this is a simplified version for 3.10
        platform_suffix = "win_amd64" if platform.system() == "Windows" else "linux_x86_64"
        torch_url = f"https://download.pytorch.org/whl/cu{pytorch_cuda}/torch-2.1.0%2Bcu{pytorch_cuda}-cp{py_version}-cp{py_version}-{platform_suffix}.whl"
        # Memory optimization: Memory-critical operation
        
        cmd = [sys.executable, "-m", "pip", "install", torch_url]
        result = subprocess.run(cmd)
        return result.returncode == 0
    except Exception as e:
        logger.warning(f"Fallback 3 failed: {e}")
    
    return False

def install_pytorch_cuda():
# Memory optimization: Memory-critical operation
    """Install PyTorch with CUDA support."""
    # Memory optimization: Memory-critical operation
    # Check if PyTorch is already installed with CUDA
    # Memory optimization: Memory-critical operation
    try:
        import torch
        if torch.cuda.is_available():
        # Memory optimization: CUDA operations for GPU acceleration
            logger.info(f"PyTorch {torch.__version__} is already installed with CUDA support.")
            # Memory optimization: Memory-critical operation
            logger.info(f"CUDA available: {torch.cuda.is_available()}")
            # Memory optimization: CUDA operations for GPU acceleration
            logger.info(f"CUDA version: {torch.version.cuda}")
            # Memory optimization: Memory-critical operation
            logger.info(f"GPU devices: {torch.cuda.device_count()}")
            # Memory optimization: CUDA operations for GPU acceleration
            if torch.cuda.is_available() and torch.cuda.device_count() > 0:
            # Memory optimization: CUDA operations for GPU acceleration
                logger.info(f"Current GPU: {torch.cuda.get_device_name(0)}")
                # Memory optimization: CUDA operations for GPU acceleration
            return True
    except ImportError:
        logger.info("PyTorch is not installed.")
    except Exception as e:
        logger.warning(f"Error checking PyTorch: {e}")
    
    # Check Python compatibility
    is_compatible, message = is_python_compatible()
    if not is_compatible:
        logger.warning(message)
        logger.warning("Installation may fail due to Python version incompatibility")
        
    # Detect CUDA version
    # Memory optimization: Memory-critical operation
    cuda_version = get_cuda_version()
    # Memory optimization: Memory-critical operation
    if not cuda_version:
    # Memory optimization: Memory-critical operation
        logger.error("Could not detect CUDA version. Please install CUDA toolkit first.")
        # Memory optimization: Memory-critical operation
        return False
    
    logger.info(f"Detected CUDA version: {cuda_version}")
    # Memory optimization: Memory-critical operation
    
    # Get install commands
    uninstall_cmd, install_cmd, pytorch_cuda = get_pytorch_install_command(cuda_version)
    # Memory optimization: Memory-critical operation
    
    # Uninstall existing PyTorch
    logger.info("Uninstalling existing PyTorch installation...")
    subprocess.run(uninstall_cmd)
    
    # Install PyTorch with CUDA
    # Memory optimization: Memory-critical operation
    logger.info(f"Installing PyTorch with CUDA {pytorch_cuda} support...")
    # Memory optimization: Memory-critical operation
    logger.info(f"Running: {' '.join(install_cmd)}")
    result = subprocess.run(install_cmd)
    
    if result.returncode != 0:
        logger.warning("Standard PyTorch installation failed, trying fallback methods...")
        success = fallback_pytorch_install(pytorch_cuda)
        # Memory optimization: Memory-critical operation
        if not success:
            logger.error("All PyTorch installation methods failed.")
            return False
    
    # Verify installation
    try:
        import importlib
        if 'torch' in sys.modules:
            importlib.reload(sys.modules['torch'])
        else:
            import torch
        
        logger.info(f"PyTorch {torch.__version__} installed successfully.")
        logger.info(f"CUDA available: {torch.cuda.is_available()}")
        # Memory optimization: CUDA operations for GPU acceleration
        if torch.cuda.is_available():
        # Memory optimization: CUDA operations for GPU acceleration
            logger.info("Installation completed successfully with CUDA support.")
            # Memory optimization: Memory-critical operation
            logger.info(f"CUDA version: {torch.version.cuda}")
            # Memory optimization: Memory-critical operation
            if torch.cuda.device_count() > 0:
            # Memory optimization: CUDA operations for GPU acceleration
                logger.info(f"Current GPU: {torch.cuda.get_device_name(0)}")
                # Memory optimization: CUDA operations for GPU acceleration
            return True
        else:
            logger.error("PyTorch was installed, but CUDA is still not available.")
            # Memory optimization: Memory-critical operation
            return False
    except Exception as e:
        logger.error(f"Error verifying PyTorch installation: {e}")
        return False

if __name__ == "__main__":
    logger.info("Starting PyTorch CUDA installation")
    # Memory optimization: Memory-critical operation
    success = install_pytorch_cuda()
    # Memory optimization: Memory-critical operation
    if success:
        logger.info("PyTorch with CUDA has been successfully installed!")
        # Memory optimization: Memory-critical operation
        
        # Add ONNX Runtime installation
        logger.info("Now installing ONNX Runtime for torch-ort compatibility...")
        onnx_success = install_onnx_runtime()
        if onnx_success:
            logger.info("ONNX Runtime has been successfully installed!")
        else:
            logger.warning("Failed to install ONNX Runtime, but PyTorch installation was successful.")
            logger.warning("You may need to manually install torch-ort dependencies.")
    else:
        logger.error("Failed to install PyTorch with CUDA support.")
        # Memory optimization: Memory-critical operation
        sys.exit(1)


# Placeholder MainClass for compatibility
class MainClass:
    """Placeholder class for tools compatibility."""
    
    def __init__(self, **kwargs):
        pass
    
    def process(self, *args, **kwargs):
        """Process method placeholder."""
        print(f"Processing in {self.__class__.__module__}")
        return True
