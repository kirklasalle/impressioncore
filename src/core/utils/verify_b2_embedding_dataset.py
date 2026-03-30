#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #python #source_code #src/core/utils/verify_b2_embedding_dataset.py #testing
**Category:** Core Implementation
**Status:** Active
"""









# Verify B2 Embedding Dataset

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:01
# Author:** ImpressionCore Team
# Tags:** #python #source_code #src\\core\\utils\\verify_b2_embedding_dataset.py #testing
# Category:** Core Implementation
# Status:** Active

"""
verify_b2_embedding_dataset.py

Verifies that all required modalities (text, images, audio, video) are present in train, val, and test splits for B2 embedding generation.
Checks for file presence, minimum count, and reports missing or empty splits.

Usage:
    python src/core/utils/verify_b2_embedding_dataset.py

Returns:
    Prints a summary of file counts for each modality and split, and highlights any missing or empty splits.
    Exits with code 0 if all checks pass, 1 otherwise.
"""
import os
import sys
from collections import defaultdict

SPLITS = ["train", "val", "test"]
MODALITIES = ["text", "images", "audio", "video"]
DATASET_ROOT = "F:/b2_datasets"

MIN_COUNTS = {
    "text": 10,
    "images": 10,
    "audio": 10,
    "video": 10,
}

def count_files(folder):
    if not os.path.exists(folder):
        return 0
    return sum(len(files) for _, _, files in os.walk(folder))

def main():
    all_ok = True
    summary = defaultdict(dict)
    for split in SPLITS:
        for modality in MODALITIES:
            path = os.path.join(DATASET_ROOT, split, modality)
            count = count_files(path)
            summary[split][modality] = count
            if count < MIN_COUNTS[modality]:
                print(f"[ERROR] {split}/{modality}: Only {count} files found (minimum required: {MIN_COUNTS[modality]})")
                all_ok = False
            else:
                print(f"[OK] {split}/{modality}: {count} files found.")
    print("\n=== Summary ===")
    for split in SPLITS:
        for modality in MODALITIES:
            print(f"{split}/{modality}: {summary[split][modality]}")
    if all_ok:
        print("\nAll splits and modalities are present and meet minimum file count requirements. Ready for embedding generation.")
        sys.exit(0)
    else:
        print("\nSome splits/modalities are missing or have too few files. Please review the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
