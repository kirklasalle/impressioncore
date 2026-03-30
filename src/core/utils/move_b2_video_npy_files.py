#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #python #source_code #src/core/utils/move_b2_video_npy_files.py #testing
**Category:** Core Implementation
**Status:** Active
"""









# Move B2 Video Npy Files

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:01
# Author:** ImpressionCore Team
# Tags:** #python #source_code #src\\core\\utils\\move_b2_video_npy_files.py #testing
# Category:** Core Implementation
# Status:** Active

"""
move_b2_video_npy_files.py
-------------------------
Moves all .mp4, .avi, and .npy files found in F:/datasets (recursively) into the correct split/video folder under F:/b2_datasets.
- If the split cannot be inferred from the path, defaults to 'train'.
- Does not overwrite existing files.
- Prints a summary of files moved.

Usage:
    python move_b2_video_npy_files.py
"""
import shutil
from pathlib import Path

DATASET_ROOT = Path('F:/b2_datasets')
SOURCE_ROOT = Path('F:/datasets')
SPLITS = ['train', 'val', 'test']
VIDEO_EXTS = ['.mp4', '.avi', '.npy']

def infer_split(path):
    parts = [p.lower() for p in path.parts]
    for split in SPLITS:
        if any(split in p for p in parts):
            return split
    return 'train'  # Default if not found

def move_video_npy_files():
    moved = {s: 0 for s in SPLITS}
    for file in SOURCE_ROOT.rglob('*'):
        if not file.is_file():
            continue
        if file.suffix.lower() in VIDEO_EXTS:
            split = infer_split(file)
            dest_dir = DATASET_ROOT / split / 'video'
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest_file = dest_dir / file.name
            if not dest_file.exists():
                shutil.move(str(file), str(dest_file))
                moved[split] += 1
                print(f"[OK] {file} -> {dest_file}")
            else:
                print(f"[SKIP] {dest_file} exists")
    print("\n=== Move Summary ===")
    for split in SPLITS:
        print(f"{split}/video: {moved[split]} files moved")

if __name__ == "__main__":
    move_video_npy_files()
    print("[DONE] Video/NPY file move complete.")
