#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #multimodal #python #source_code #src/training/inspect_batch_format.py #testing #training
**Category:** Training System
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** October 15, 2024
# Updated:** August 4, 2025
# Author:** ImpressionCore Team
# Tags:** #multimodal #python #source_code #src\\training\\inspect_batch_format.py #testing #training
# Category:** Training System
# Status:** Active

"""
Quick batch inspector to debug the dataloader format
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.training.b1_dataset_integration_pipeline import B1DatasetIntegrationPipeline

def inspect_batch_format():
    """Inspect the actual batch format from the dataloader"""

    print("🔍 Inspecting B1 DataLoader batch format...")

    # Create dataloader
    pipeline = B1DatasetIntegrationPipeline()
    dataloader = pipeline.create_b1_dataloader(
        modality="multimodal",
        split="train",
        batch_size=1
    )

    print(f"✅ DataLoader created with {len(dataloader)} batches")

    # Get first batch
    first_batch = next(iter(dataloader))

    print("\n📦 First Batch Analysis:")
    print(f"   Type: {type(first_batch)}")

    if isinstance(first_batch, dict):
        print(f"   Keys: {list(first_batch.keys())}")
        for key, value in first_batch.items():
            print(f"   {key}:")
            print(f"      Type: {type(value)}")
            if hasattr(value, 'shape'):
                print(f"      Shape: {value.shape}")
                print(f"      Device: {value.device}")
                print(f"      Dtype: {value.dtype}")
                if value.numel() < 20:
                    print(f"      Sample values: {value.flatten()[:10]}")
            else:
                print(f"      Value: {value}")
    elif isinstance(first_batch, (list, tuple)):
        print(f"   Length: {len(first_batch)}")
        for i, item in enumerate(first_batch):
            print(f"   Item {i}:")
            print(f"      Type: {type(item)}")
            if hasattr(item, 'shape'):
                print(f"      Shape: {item.shape}")
                print(f"      Device: {item.device}")
                print(f"      Dtype: {item.dtype}")
    else:
        print(f"   Direct tensor/object:")
        if hasattr(first_batch, 'shape'):
            print(f"      Shape: {first_batch.shape}")
            print(f"      Device: {first_batch.device}")
            print(f"      Dtype: {first_batch.dtype}")

    # Test a few more batches
    print("\n🔄 Testing next 3 batches...")
    for i, batch in enumerate(dataloader):
        if i >= 3:
            break
        print(f"   Batch {i+2}: Type={type(batch)}")
        if isinstance(batch, dict):
            print(f"      Keys: {list(batch.keys())}")
        elif isinstance(batch, (list, tuple)):
            print(f"      Length: {len(batch)}")

    print("\n✅ Batch inspection complete!")

if __name__ == "__main__":
    inspect_batch_format()
