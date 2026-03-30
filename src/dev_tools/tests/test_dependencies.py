#!/usr/bin/env python3
"""
Test script to verify PyTorch and xformers compatibility
"""
import sys

def test_pytorch():
    """Test PyTorch functionality"""
    try:
        import torch
        print(f"✅ PyTorch: {torch.__version__}")
        print(f"✅ CUDA Available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"✅ CUDA Device: {torch.cuda.get_device_name()}")
        return True
    except Exception as e:
        print(f"❌ PyTorch Error: {e}")
        return False

def test_xformers():
    """Test xformers functionality"""
    try:
        import xformers
        print(f"✅ xformers: {xformers.__version__}")
        return True
    except Exception as e:
        print(f"❌ xformers Error: {e}")
        return False

def test_torchaudio():
    """Test torchaudio functionality"""
    try:
        import torchaudio
        print(f"✅ torchaudio: {torchaudio.__version__}")
        return True
    except Exception as e:
        print(f"❌ torchaudio Error: {e}")
        return False

def test_torchvision():
    """Test torchvision functionality"""
    try:
        import torchvision
        print(f"✅ torchvision: {torchvision.__version__}")
        return True
    except Exception as e:
        print(f"❌ torchvision Error: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing PyTorch ecosystem dependencies...")
    print("=" * 50)
    
    pytorch_ok = test_pytorch()
    xformers_ok = test_xformers()
    torchaudio_ok = test_torchaudio()
    torchvision_ok = test_torchvision()
    
    print("=" * 50)
    
    if all([pytorch_ok, xformers_ok, torchaudio_ok, torchvision_ok]):
        print("🎉 All dependencies are working correctly!")
        sys.exit(0)
    else:
        print("⚠️  Some dependencies have issues")
        sys.exit(1)
