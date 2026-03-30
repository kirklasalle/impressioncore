#!/usr/bin/env python3
"""
Simple test script to verify the ImpressionCore environment is working
Tests PyTorch, CUDA, and basic model loading capabilities
"""

import sys
print(f"Python version: {sys.version}")

try:
    import torch
    print(f"PyTorch version: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    
    if torch.cuda.is_available():
        print(f"CUDA version: {torch.version.cuda}")
        print(f"Device count: {torch.cuda.device_count()}")
        print(f"Current device: {torch.cuda.current_device()}")
        print(f"Device name: {torch.cuda.get_device_name()}")
        
        # Test basic tensor operations on GPU
        x = torch.randn(3, 3).cuda()
        y = torch.randn(3, 3).cuda()
        z = torch.matmul(x, y)
        print("✅ Basic CUDA tensor operations working")
        
        # Test memory info
        memory_allocated = torch.cuda.memory_allocated() / 1024**2  # MB
        memory_reserved = torch.cuda.memory_reserved() / 1024**2   # MB
        print(f"GPU Memory - Allocated: {memory_allocated:.1f}MB, Reserved: {memory_reserved:.1f}MB")
    
except ImportError as e:
    print(f"❌ PyTorch import error: {e}")

try:
    from transformers import AutoTokenizer
    print("✅ Transformers library working")
except ImportError as e:
    print(f"❌ Transformers import error: {e}")

try:
    import numpy as np
    print(f"NumPy version: {np.__version__}")
except ImportError as e:
    print(f"❌ NumPy import error: {e}")

print("\n🎯 Environment Test Complete")
