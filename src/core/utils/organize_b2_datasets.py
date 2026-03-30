#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #python #source_code #src/core/utils/organize_b2_datasets.py #testing #training
**Category:** Core Implementation
**Status:** Active
"""









# Organize B2 Datasets

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:01
# Author:** ImpressionCore Team
# Tags:** #python #source_code #src\\core\\utils\\organize_b2_datasets.py #testing #training
# Category:** Core Implementation
# Status:** Active

"""
organize_b2_datasets.py
----------------------
Organizes and copies data from prepared ImpressionCore folders into the canonical B2 dataset structure for embedding generation.

- Source dataset root: F:/b2_datasets
- Output embedding root: F:/b2_embeddings
- Copies from: ImpressionCore_Training_Data, impressioncore-training-data, impressioncore-processed-transcripts, impressioncore-enhanced-dataset, impressioncore-embeddings-062125, etc.
- Ensures F:/b2_datasets/{split}/{modality} exists and is populated.
- Does not overwrite existing files.
- Safe to run multiple times.

Usage:
    python organize_b2_datasets.py
"""
import shutil
from pathlib import Path

# Define canonical splits and modalities
splits = ['train', 'val', 'test']
modalities = ['text', 'images', 'audio', 'video']

# Canonical dataset root
DATASET_ROOT = Path('F:/b2_datasets')

# List of prepared data sources (add more as needed)
PREPARED_SOURCES = [
    Path('F:/datasets/ImpressionCore_Training_Data'),
    Path('F:/datasets/impressioncore-training-data'),
    Path('F:/datasets/impressioncore-processed-transcripts'),
    Path('F:/datasets/impressioncore-enhanced-dataset'),
    Path('F:/datasets/impressioncore-embeddings-062125'),
]

# Mapping from known source subfolders to canonical split/modality
# (Extend this mapping as needed for your data)
SOURCE_MAP = {
    'train2017': ('train', 'images'),
    'train-other-500': ('train', 'audio'),
    'train-clean-360': ('train', 'audio'),
    'train-clean-100': ('train', 'audio'),
    'training_data': ('train', 'text'),
    'val2017': ('val', 'images'),
    'test-clean': ('test', 'audio'),
    'test-other': ('test', 'audio'),
}

def ensure_dirs():
    for split in splits:
        for modality in modalities:
            (DATASET_ROOT / split / modality).mkdir(parents=True, exist_ok=True)

def move_if_missing(src, dst):
    if dst.exists():
        return
    if src.is_file():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))
    elif src.is_dir():
        for item in src.iterdir():
            move_if_missing(item, dst / item.name)

def organize():
    ensure_dirs()
    for source_root in PREPARED_SOURCES:
        if not source_root.exists():
            continue
        for subdir in source_root.glob('**/*'):
            if not subdir.is_dir():
                continue
            name = subdir.name.lower()
            if name in SOURCE_MAP:
                split, modality = SOURCE_MAP[name]
                dest = DATASET_ROOT / split / modality
                print(f"[INFO] Moving from {subdir} to {dest}")
                for file in subdir.glob('**/*'):
                    if file.is_file():
                        rel = file.relative_to(subdir)
                        target = dest / rel
                        target.parent.mkdir(parents=True, exist_ok=True)
                        if not target.exists():
                            shutil.move(str(file), str(target))
                            print(f"[OK] {file} -> {target}")
                        else:
                            print(f"[SKIP] {target} exists")

if __name__ == "__main__":
    organize()
    print("[DONE] B2 dataset organization complete.")
