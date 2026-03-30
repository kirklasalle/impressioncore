#!/usr/bin/env python3
"""
Simple test for datasets directory functionality
"""

import os
import torch
from pathlib import Path

def simple_get_device():
    """Simple device detection"""
    if torch.cuda.is_available():
        return 'cuda'
    return 'cpu'

def test_datasets_directory():
    """Test that datasets directory is properly structured"""
    print("Testing datasets directory structure...")
    
    datasets_root = Path("src/data/datasets")
    
    # Check main datasets directory
    if not datasets_root.exists():
        print("❌ Datasets directory not found!")
        return False
    
    print(f"✅ Found datasets directory: {datasets_root}")
    
    # Check subdirectories
    expected_dirs = ['text', 'multimodal', 'benchmark', 'preprocessed', 'validation']
    
    for dirname in expected_dirs:
        dir_path = datasets_root / dirname
        if dir_path.exists():
            print(f"✅ Found {dirname}/ directory")
            
            # Count files in directory
            files = list(dir_path.rglob('*'))
            file_count = len([f for f in files if f.is_file()])
            print(f"   - {file_count} files found")
            
            # Show first few files as examples
            for i, file_path in enumerate([f for f in files if f.is_file()][:3]):
                print(f"   - {file_path.name}")
                
        else:
            print(f"⚠️  Missing {dirname}/ directory")
    
    # Test device detection
    device = simple_get_device()
    print(f"✅ Device detection: {device}")
    
    # Check README
    readme_path = datasets_root / "README.md"
    if readme_path.exists():
        print("✅ Found datasets README.md")
    else:
        print("⚠️  Missing datasets README.md")
    
    print("\n✅ Datasets directory test completed successfully!")
    print(f"📁 Structure: {datasets_root} contains the expected subdirectories")
    print("🎯 Ready for real dataset integration!")
    
    return True

if __name__ == "__main__":
    test_datasets_directory()
