#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #python #source_code #src/core/utils/move_b2_avi_and_orphans.py #testing
**Category:** Core Implementation
**Status:** Active
"""









# Move B2 Avi And Orphans

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:01
# Author:** ImpressionCore Team
# Tags:** #python #source_code #src\\core\\utils\\move_b2_avi_and_orphans.py #testing
# Category:** Core Implementation
# Status:** Active

"""
Move all .avi video files and any remaining data files in F:/b2_datasets to the correct split/modality folders.
- Moves .avi files from F:/b2_datasets/video/ to train/val/test splits based on a sampling strategy (default: val=100, test=100, rest=train)
- Moves any orphaned files in F:/b2_datasets (not in split folders) to the appropriate split/modality
- Skips files already in the correct location
- Requires: Python 3.8+, tqdm
"""
import os
import random
import shutil

from tqdm import tqdm

ROOT = "F:/b2_datasets"
VIDEO_SRC = os.path.join(ROOT, "video")
SPLITS = ["train", "val", "test"]
MODALITIES = ["images", "audio", "video", "text"]

VAL_COUNT = 100
TEST_COUNT = 100


def safe_makedirs(path):
    os.makedirs(path, exist_ok=True)

def move_file(src, dest):
    if os.path.abspath(src) == os.path.abspath(dest):
        return
    safe_makedirs(os.path.dirname(dest))
    shutil.move(src, dest)
    print(f"[OK] {src} -> {dest}")

def move_avi_files():
    avi_files = [f for f in os.listdir(VIDEO_SRC) if f.lower().endswith('.avi')]
    random.shuffle(avi_files)
    val_files = avi_files[:VAL_COUNT]
    test_files = avi_files[VAL_COUNT:VAL_COUNT+TEST_COUNT]
    train_files = avi_files[VAL_COUNT+TEST_COUNT:]
    for split, files in zip(["val", "test", "train"], [val_files, test_files, train_files]):
        for fname in tqdm(files, desc=f"Moving {split} .avi files"):
            src = os.path.join(VIDEO_SRC, fname)
            dest = os.path.join(ROOT, split, "video", fname)
            move_file(src, dest)

def move_orphaned_files():
    for dirpath, _, filenames in os.walk(ROOT):
        # Skip split/modality folders
        rel = os.path.relpath(dirpath, ROOT)
        if rel == "." or rel.split(os.sep)[0] not in SPLITS:
            for fname in filenames:
                fpath = os.path.join(dirpath, fname)
                # Guess modality by extension
                ext = fname.split(".")[-1].lower()
                if ext in ["jpg", "jpeg", "png", "bmp"]:
                    modality = "images"
                elif ext in ["wav", "flac", "mp3"]:
                    modality = "audio"
                elif ext in ["avi", "mp4", "mov"]:
                    modality = "video"
                elif ext in ["txt", "json"]:
                    modality = "text"
                else:
                    continue
                # Default to train split if not inferable
                dest = os.path.join(ROOT, "train", modality, fname)
                move_file(fpath, dest)

def main():
    move_avi_files()
    move_orphaned_files()
    print("[DONE] All .avi and orphaned files moved to canonical structure.")

if __name__ == "__main__":
    main()
