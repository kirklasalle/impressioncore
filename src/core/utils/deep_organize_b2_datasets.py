#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #python #source_code #src/core/utils/deep_organize_b2_datasets.py #testing
**Category:** Core Implementation
**Status:** Active
"""









# Deep Organize B2 Datasets

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:00
# Author:** ImpressionCore Team
# Tags:** #python #source_code #src\\core\\utils\\deep_organize_b2_datasets.py #testing
# Category:** Core Implementation
# Status:** Active

"""
deep_organize_b2_datasets.py
----------------------------
Recursively scans all known ImpressionCore data sources under F:/datasets, locates files by type, and moves them into the correct split/modality folders under F:/b2_datasets.

- Uses file extensions to infer modality: text (.txt, .json), images (.jpg, .jpeg, .png), audio (.wav, .flac, .mp3), video (.mp4, .avi, .npy)
- Uses folder names to infer split: train, val, test (case-insensitive, partial match)
- Moves files only if not already present in the destination
- Prints a summary of files moved per split/modality

Usage:
    python deep_organize_b2_datasets.py
"""
import shutil
from pathlib import Path

DATASET_ROOT = Path('F:/b2_datasets')
ALL_SOURCES = [Path('F:/datasets')]
SPLITS = ['train', 'val', 'test']
MODALITY_EXTS = {
    'text': ['.txt', '.json'],
    'images': ['.jpg', '.jpeg', '.png'],
    'audio': ['.wav', '.flac', '.mp3'],
    'video': ['.mp4', '.avi', '.npy']
}

def infer_split(path):
    parts = [p.lower() for p in path.parts]
    for split in SPLITS:
        if any(split in p for p in parts):
            return split
    return None

def infer_modality(path):
    ext = path.suffix.lower()
    for modality, exts in MODALITY_EXTS.items():
        if ext in exts:
            return modality
    return None

def deep_organize():
    moved = {s: {m: 0 for m in MODALITY_EXTS} for s in SPLITS}
    for source_root in ALL_SOURCES:
        for file in source_root.rglob('*'):
            if not file.is_file():
                continue
            split = infer_split(file)
            modality = infer_modality(file)
            if split and modality:
                dest_dir = DATASET_ROOT / split / modality
                dest_dir.mkdir(parents=True, exist_ok=True)
                dest_file = dest_dir / file.name
                if not dest_file.exists():
                    shutil.move(str(file), str(dest_file))
                    moved[split][modality] += 1
                    print(f"[OK] {file} -> {dest_file}")
                else:
                    print(f"[SKIP] {dest_file} exists")
    print("\n=== Move Summary ===")
    for split in SPLITS:
        for modality in MODALITY_EXTS:
            print(f"{split}/{modality}: {moved[split][modality]} files moved")

if __name__ == "__main__":
    deep_organize()
    print("[DONE] Deep B2 dataset organization complete.")
