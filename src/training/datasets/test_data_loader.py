#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #memory_management #multimodal #python #source_code #src/training/datasets\test_data_loader.py #testing #training
**Category:** Training System
**Status:** Active
"""









# Test Data Loader

# Created:** October 15, 2024
# Updated:** August 4, 2025
# Author:** ImpressionCore Team
# Tags:** #memory_management #multimodal #python #source_code #src\\training\\datasets\\test_data_loader.py #testing #training
# Category:** Training System
# Status:** Active

"""
test_data_loader.py

Test script for B2 multimodal data loader. Loads a batch from each modality and prints/logs results.

Usage:
    python test_data_loader.py

Memory: Designed for low VRAM (GTX 1050 Ti) and large datasets.
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))
from data_loading import get_dataloaders

if __name__ == '__main__':
    print("[ImpressionCore] Running data loader test...")
    loaders = get_dataloaders(batch_size=1)
    for modality, loader in loaders.items():
        print(f'\nTesting {modality} loader:')
        for i, batch in enumerate(loader):
            print(f'Batch {i}:', batch)
            if i > 0:
                break
    print("[ImpressionCore] Data loader test complete.")
