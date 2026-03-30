#!/usr/bin/env python3
"""
Simple test to isolate the training module import error.
"""

import sys
import os

# Add the project root to the path
project_root = os.path.join(os.path.dirname(__file__), '..', '..', '..')
sys.path.insert(0, project_root)

try:
    print("Testing imports...")
    
    print("1. Importing ModelTrainer...")
    from src.training.trainer import ModelTrainer
    print("   ✓ ModelTrainer imported successfully")
    
    print("2. Testing from_config method...")
    model_config = {"model_name": "test_model"}
    trainer = ModelTrainer.from_config(
        model_config=model_config,
        device="cpu",
        mixed_precision=False,
        target_vram_usage=1.0
    )
    print("   ✓ ModelTrainer.from_config successful")
    
except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()
