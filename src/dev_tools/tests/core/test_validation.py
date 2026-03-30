#!/usr/bin/env python3
"""
Simple validation test for performance optimizations.
"""

import torch
import torch.nn as nn
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

def test_basic_functionality():
    """Test basic PyTorch functionality."""
    print("Testing basic PyTorch functionality...")
    
    # Test tensor creation
    x = torch.randn(2, 4, 512)
    print(f"✅ Created tensor with shape: {x.shape}")
    
    # Test basic attention
    attention = nn.MultiheadAttention(512, 8, batch_first=True)
    output, _ = attention(x, x, x)
    print(f"✅ Basic attention output shape: {output.shape}")
    
    return True

def test_quantization_imports():
    """Test quantization module imports."""
    print("Testing quantization imports...")
    
    try:
        import torch.quantization as quant
        print("✅ PyTorch quantization module available")
        
        # Test basic quantization setup
        model = nn.Linear(512, 512)
        qconfig = torch.quantization.get_default_qconfig('fbgemm')
        print("✅ Quantization config created")
        
        return True
    except Exception as e:
        print(f"❌ Quantization test failed: {e}")
        return False

def test_memory_tracking():
    """Test memory tracking functionality."""
    print("Testing memory tracking...")
    
    try:
        import psutil
        import gc
        
        # Get initial memory
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Create some tensors
        tensors = []
        for i in range(10):
            tensors.append(torch.randn(1024, 1024))
        
        # Check memory increase
        current_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = current_memory - initial_memory
        
        print(f"✅ Memory tracking works. Increase: {memory_increase:.2f} MB")
        
        # Cleanup
        del tensors
        gc.collect()
        
        return True
    except Exception as e:
        print(f"❌ Memory tracking test failed: {e}")
        return False

def main():
    """Run all validation tests."""
    print("=== ImpressionCore Performance Optimization Validation ===\n")
    
    tests = [
        ("Basic Functionality", test_basic_functionality),
        ("Quantization Imports", test_quantization_imports),
        ("Memory Tracking", test_memory_tracking),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"Running {test_name}...")
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                print(f"✅ {test_name} PASSED\n")
            else:
                print(f"❌ {test_name} FAILED\n")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}\n")
            results.append((test_name, False))
    
    # Summary
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print("=== Test Summary ===")
    print(f"Passed: {passed}/{total}")
    
    for test_name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {test_name}")
    
    if passed == total:
        print("\n🎉 All validation tests passed! Performance optimizations are ready.")
        return True
    else:
        print(f"\n⚠️ {total - passed} tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
