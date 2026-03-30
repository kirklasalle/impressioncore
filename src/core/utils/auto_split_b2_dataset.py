#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #python #source_code #src/core/utils/auto_split_b2_dataset.py #testing
**Category:** Core Implementation
**Status:** Active
"""









# Auto Split B2 Dataset

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:00
# Author:** ImpressionCore Team
# Tags:** #python #source_code #src\\core\\utils\\auto_split_b2_dataset.py #testing
# Category:** Core Implementation
# Status:** Active

"""
Automated script to split all files in F:/b2_datasets by modality (video, audio, images, text)
into train, val, and test splits for embedding pipeline completeness.
- Evenly/randomly assigns files to val/ and test/ splits (default: 80% train, 10% val, 10% test)
- Supports .avi, .mp4, .wav, .flac, .jpg, .png, .txt, .json, .npy, etc.
- Skips files already in correct split
- Safe for repeated use
- Usage: Activate .venv310, then run from project root
"""
import os
import random
import shutil
from glob import glob

ROOT = "F:/b2_datasets"
SPLITS = ["train", "val", "test"]
SPLIT_RATIOS = {"train": 0.8, "val": 0.1, "test": 0.1}
MODALITIES = ["video", "audio", "images", "text"]
EXTS = {
    "video": [".avi", ".mp4", ".mov", ".mkv"],
    "audio": [".wav", ".flac", ".mp3"],
    "images": [".jpg", ".jpeg", ".png", ".bmp"],
    "text": [".txt", ".json", ".csv"],
}


def get_all_files(modality):
    files = []
    for ext in EXTS[modality]:
        files.extend(glob(os.path.join(ROOT, "**", modality, f"*{ext}"), recursive=True))
    return files

def get_split_path(f, split, modality):
    fname = os.path.basename(f)
    return os.path.join(ROOT, split, modality, fname)

def move_files(files, split, modality):
    for f in files:
        dest = get_split_path(f, split, modality)
        if os.path.abspath(f) == os.path.abspath(dest):
            continue
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.move(f, dest)
        print(f"[OK] {f} -> {dest}")

def assign_and_move(modality):
    files = get_all_files(modality)
    # Remove files already in correct split
    files = [f for f in files if not any(f"/{split}/{modality}/" in f.replace('\\','/') for split in SPLITS)]
    random.shuffle(files)
    n = len(files)
    n_train = int(n * SPLIT_RATIOS["train"])
    n_val = int(n * SPLIT_RATIOS["val"])
    train_files = files[:n_train]
    val_files = files[n_train:n_train+n_val]
    test_files = files[n_train+n_val:]
    move_files(val_files, "val", modality)
    move_files(test_files, "test", modality)
    # Optionally move train files (if not already in train)
    for f in train_files:
        if f"/train/{modality}/" not in f.replace('\\','/'):
            move_files([f], "train", modality)

def main():
    for modality in MODALITIES:
        assign_and_move(modality)
    print("[DONE] Automated split assignment complete.")

if __name__ == "__main__":
    main()
