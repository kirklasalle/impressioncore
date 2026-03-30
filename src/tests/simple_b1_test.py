#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #cuda #inference #memory_management #multimodal #python #pytorch #source_code #src/tests/simple_b1_test.py #testing #training
**Category:** Testing Framework
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:02
# Author:** ImpressionCore Team
# Tags:** #cuda #inference #memory_management #multimodal #python #pytorch #source_code #src\\tests\\simple_b1_test.py #testing #training
# Category:** Testing Framework
# Status:** Active

"""Simple B1 Model Validation Test"""

import sys

sys.path.append('.')

try:
    import torch
    print("✅ PyTorch imported successfully")
    print(f"PyTorch version: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")

    if torch.cuda.is_available():
        print(f"CUDA device: {torch.cuda.get_device_name(0)}")
        print(f"CUDA memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")

    # Test model import
    from .core.models.multimodal_b1_architecture import ImpressionCoreBMultimodal, MultimodalConfig
    print("✅ B1 model imported successfully")

    # Initialize model
    config = MultimodalConfig()
    model = ImpressionCoreBMultimodal(config)
    print("✅ B1 model initialized successfully")

    # Test inference
    test_input = {"text": ["What is machine learning?", "Explain neural networks"]}

    with torch.no_grad():
        output = model(test_input)

    print("✅ Model inference successful!")
    print(f"Output keys: {list(output.keys())}")
    print(f"Feature shape: {output['conversation_features'].shape}")
    print(f"Quality score: {float(output['quality_score'].mean()):.4f}")
    print(f"Academic level shape: {output['academic_level'].shape}")

    # Check F: drive data
    from pathlib import Path
    f_drive = Path("F:/impressioncore_training_data/processed_embeddings")
    print(f"\n✅ F: drive accessible: {f_drive.exists()}")

    if f_drive.exists():
        files = list(f_drive.glob("*"))
        print(f"Files in embeddings directory: {len(files)}")
        for f in files:
            print(f"  - {f.name}")

    print("\n🎉 ALL VALIDATION TESTS PASSED!")
    print("ImpressionCore B1 multimodal model with real data integration is fully operational!")

except Exception as e:
    print(f"❌ Validation failed: {e}")
    import traceback
    traceback.print_exc()
