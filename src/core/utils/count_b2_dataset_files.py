#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #python #source_code #src/core/utils/count_b2_dataset_files.py #testing
**Category:** Core Implementation
**Status:** Active
"""









# Count B2 Dataset Files

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:00
# Author:** ImpressionCore Team
# Tags:** #python #source_code #src\\core\\utils\\count_b2_dataset_files.py #testing
# Category:** Core Implementation
# Status:** Active

"""
count_b2_dataset_files.py
------------------------
Recursively counts and lists files in each split/modality under F:/b2_datasets.
Provides a full inventory to help locate or fix missing data.

Usage:
    python count_b2_dataset_files.py
"""
from pathlib import Path

DATASET_ROOT = Path('F:/b2_datasets')
splits = ['train', 'val', 'test']
modalities = ['text', 'images', 'audio', 'video']

def count_and_list():
    for split in splits:
        print(f"\n=== Split: {split} ===")
        for modality in modalities:
            folder = DATASET_ROOT / split / modality
            if not folder.exists():
                print(f"  [MISSING] {modality} folder: {folder}")
                continue
            files = list(folder.rglob('*'))
            file_count = sum(1 for f in files if f.is_file())
            print(f"  {modality}: {file_count} files")
            if file_count > 0:
                for f in files:
                    if f.is_file():
                        print(f"    - {f.relative_to(DATASET_ROOT)}")
                        if file_count > 10 and files.index(f) == 9:
                            print(f"    ... ({file_count-10} more files)")
                            break

if __name__ == "__main__":
    count_and_list()
