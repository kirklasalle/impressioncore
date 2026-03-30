#!/usr/bin/env python3
"""
ImpressionCore: Import Utilities

Module for handling optional dependencies and graceful fallbacks.
Based on patterns from Hugging Face Transformers and librosa.

File: core/utils/import_utils.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-06-12
Modified: 2025-06-12
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [utilities, imports, dependencies, fallbacks, 2025]
Dependencies: [importlib, functools, logging]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements import utilities for graceful handling of optional
dependencies, following industry best practices from HuggingFace Transformers.
"""

import importlib
import importlib.util
import sys
import warnings
from functools import wraps
from typing import Dict, Optional, Set, Union, Callable, Any


# Cache for import availability checks
_import_cache: Dict[str, bool] = {}

def is_package_available(package_name: str, min_version: Optional[str] = None) -> bool:
    """
    Check if a package is available for import.
    
    Args:
        package_name: Name of the package to check
        min_version: Optional minimum version requirement
        
    Returns:
        True if package is available and meets version requirements
    """
    if package_name in _import_cache:
        return _import_cache[package_name]
    
    try:
        spec = importlib.util.find_spec(package_name)
        if spec is None:
            _import_cache[package_name] = False
            return False
            
        # Try to import the module
        module = importlib.import_module(package_name)
        
        # Check version if specified
        if min_version and hasattr(module, '__version__'):
            from packaging import version
            if version.parse(module.__version__) < version.parse(min_version):
                _import_cache[package_name] = False
                return False
        
        _import_cache[package_name] = True
        return True
        
    except (ImportError, AttributeError, ModuleNotFoundError):
        _import_cache[package_name] = False
        return False


def requires_package(
    package_name: str, 
    min_version: Optional[str] = None,
    fallback_message: Optional[str] = None
):
    """
    Decorator to ensure a package is available before calling a function.
    
    Args:
        package_name: Required package name
        min_version: Optional minimum version
        fallback_message: Custom error message
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not is_package_available(package_name, min_version):
                error_msg = fallback_message or (
                    f"Function '{func.__name__}' requires '{package_name}'"
                    f"{f' >= {min_version}' if min_version else ''} "
                    f"but it was not found in your environment."
                )
                raise ImportError(error_msg)
            return func(*args, **kwargs)
        return wrapper
    return decorator


class OptionalImport:
    """
    Context manager for optional imports with graceful fallbacks.
    """
    
    def __init__(self, package_name: str, fallback_message: Optional[str] = None):
        self.package_name = package_name
        self.fallback_message = fallback_message
        self.module = None
        self.available = False
    
    def __enter__(self):
        try:
            self.module = importlib.import_module(self.package_name)
            self.available = True
            return self.module
        except ImportError:
            self.available = False
            if self.fallback_message:
                warnings.warn(f"Optional dependency '{self.package_name}' not available: {self.fallback_message}")
            return None
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


# Audio processing dependencies
def is_librosa_available() -> bool:
    """Check if librosa is available."""
    return is_package_available("librosa")

def is_soundfile_available() -> bool:
    """Check if soundfile is available."""
    return is_package_available("soundfile")

def is_torchaudio_available() -> bool:
    """Check if torchaudio is available."""
    return is_package_available("torchaudio")

def is_audioread_available() -> bool:
    """Check if audioread is available."""
    return is_package_available("audioread")

# Vision processing dependencies
def is_pillow_available() -> bool:
    """Check if PIL/Pillow is available."""
    return is_package_available("PIL") or is_package_available("Pillow")

def is_opencv_available() -> bool:
    """Check if OpenCV is available."""
    return is_package_available("cv2")

def is_torchvision_available() -> bool:
    """Check if torchvision is available."""
    return is_package_available("torchvision")

# ML framework dependencies
def is_torch_available() -> bool:
    """Check if PyTorch is available."""
    return is_package_available("torch")

def is_transformers_available() -> bool:
    """Check if transformers is available."""
    return is_package_available("transformers")

# Development and utility dependencies
def is_rich_available() -> bool:
    """Check if rich is available."""
    return is_package_available("rich")

def is_psutil_available() -> bool:
    """Check if psutil is available."""
    return is_package_available("psutil")


class DependencyChecker:
    """
    Utility class for checking and reporting dependency status.
    """
    
    AUDIO_DEPS = {
        'librosa': 'Audio analysis and feature extraction',
        'soundfile': 'Audio file I/O',
        'torchaudio': 'PyTorch audio processing',
        'audioread': 'Audio file reading fallback'
    }
    
    VISION_DEPS = {
        'PIL': 'Image processing',
        'cv2': 'Computer vision operations',
        'torchvision': 'PyTorch vision utilities'
    }
    
    ML_DEPS = {
        'torch': 'PyTorch deep learning framework',
        'transformers': 'Hugging Face transformers',
        'numpy': 'Numerical computing'
    }
    
    UTIL_DEPS = {
        'rich': 'Rich terminal formatting',
        'psutil': 'System monitoring',
        'packaging': 'Version handling'
    }
    
    @classmethod
    def check_audio_deps(cls) -> Dict[str, bool]:
        """Check availability of audio processing dependencies."""
        return {dep: is_package_available(dep) for dep in cls.AUDIO_DEPS.keys()}
    
    @classmethod
    def check_vision_deps(cls) -> Dict[str, bool]:
        """Check availability of vision processing dependencies."""
        return {dep: is_package_available(dep) for dep in cls.VISION_DEPS.keys()}
    
    @classmethod
    def check_ml_deps(cls) -> Dict[str, bool]:
        """Check availability of ML framework dependencies."""
        return {dep: is_package_available(dep) for dep in cls.ML_DEPS.keys()}
    
    @classmethod
    def check_util_deps(cls) -> Dict[str, bool]:
        """Check availability of utility dependencies."""
        return {dep: is_package_available(dep) for dep in cls.UTIL_DEPS.keys()}
    
    @classmethod
    def get_missing_deps(cls, category: str = 'all') -> Dict[str, str]:
        """
        Get missing dependencies for a category.
        
        Args:
            category: Category to check ('audio', 'vision', 'ml', 'util', 'all')
            
        Returns:
            Dictionary of missing dependencies and their descriptions
        """
        missing = {}
        
        if category in ('audio', 'all'):
            for dep, desc in cls.AUDIO_DEPS.items():
                if not is_package_available(dep):
                    missing[dep] = desc
        
        if category in ('vision', 'all'):
            for dep, desc in cls.VISION_DEPS.items():
                if not is_package_available(dep):
                    missing[dep] = desc
        
        if category in ('ml', 'all'):
            for dep, desc in cls.ML_DEPS.items():
                if not is_package_available(dep):
                    missing[dep] = desc
        
        if category in ('util', 'all'):
            for dep, desc in cls.UTIL_DEPS.items():
                if not is_package_available(dep):
                    missing[dep] = desc
        
        return missing
    
    @classmethod
    def print_dependency_report(cls):
        """Print a comprehensive dependency report."""
        print("📋 ImpressionCore Dependency Report")
        print("=" * 50)
        
        categories = [
            ('Audio Processing', cls.AUDIO_DEPS, cls.check_audio_deps()),
            ('Vision Processing', cls.VISION_DEPS, cls.check_vision_deps()),
            ('ML Frameworks', cls.ML_DEPS, cls.check_ml_deps()),
            ('Utilities', cls.UTIL_DEPS, cls.check_util_deps())
        ]
        
        for cat_name, cat_deps, cat_status in categories:
            print(f"\n{cat_name}:")
            for dep, desc in cat_deps.items():
                status = "✅" if cat_status.get(dep, False) else "❌"
                print(f"  {status} {dep:<15} - {desc}")


# Lazy import utilities
def lazy_import(module_name: str):
    """
    Lazy import utility that defers import until attribute access.
    """
    class LazyModule:
        def __init__(self, name):
            self.name = name
            self._module = None
        
        def _load_module(self):
            if self._module is None:
                self._module = importlib.import_module(self.name)
            return self._module
        
        def __getattr__(self, attr):
            module = self._load_module()
            return getattr(module, attr)
        
        def __dir__(self):
            module = self._load_module()
            return dir(module)
    
    return LazyModule(module_name)


# Example usage
if __name__ == "__main__":
    # Print dependency report
    DependencyChecker.print_dependency_report()
    
    # Example of optional import
    with OptionalImport("librosa") as librosa:
        if librosa:
            print("✅ Librosa available for audio processing")
        else:
            print("❌ Librosa not available - using fallbacks")
    
    # Example of decorator usage
    @requires_package("torch", "1.0.0")
    def train_model():
        print("Training with PyTorch...")
    
    try:
        train_model()
    except ImportError as e:
        print(f"Cannot train model: {e}")
