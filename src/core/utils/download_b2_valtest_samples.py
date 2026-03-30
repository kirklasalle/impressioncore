#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #python #source_code #src/core/utils/download_b2_valtest_samples.py #testing
**Category:** Core Implementation
**Status:** Active
"""









# Download B2 Valtest Samples

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:00
# Author:** ImpressionCore Team
# Tags:** #python #source_code #src\\core\\utils\\download_b2_valtest_samples.py #testing
# Category:** Core Implementation
# Status:** Active

"""
Script to download open sample audio and video files for B2 validation/test splits.
- Downloads a small set of WAV audio files from COUGHVID
- Downloads MP4 video files from AVSync15 and ML Video Codec Dataset
- Places them in F:/b2_datasets/val/audio, test/audio, val/video, test/video
- Skips files if already present
- Requires: requests, tqdm
- Usage: Activate .venv310, then run this script from project root
"""
import os

import requests
from tqdm import tqdm

# Define download targets (expand as needed)
AUDIO_TARGETS = [
    # COUGHVID open samples (replace with direct links as needed)
    ("https://coughvid.epfl.ch/media/001-0001-0001.wav", "val/audio/001-0001-0001.wav"),
    ("https://coughvid.epfl.ch/media/001-0001-0002.wav", "test/audio/001-0001-0002.wav"),
]
VIDEO_TARGETS = [
    # AVSync15 sample videos (replace with direct links as needed)
    ("https://lzhangbj.github.io/projects/asva/videos/avsync15_sample1.mp4", "val/video/avsync15_sample1.mp4"),
    ("https://lzhangbj.github.io/projects/asva/videos/avsync15_sample2.mp4", "test/video/avsync15_sample2.mp4"),
    # ML Video Codec Dataset sample (replace with direct links as needed)
    ("https://mlvideocodec-dataset.org/samples/sample1.mp4", "val/video/mlcodec_sample1.mp4"),
]

ROOT = "F:/b2_datasets"


def safe_makedirs(path):
    os.makedirs(path, exist_ok=True)

def download_file(url, dest):
    if os.path.exists(dest):
        print(f"[SKIP] {dest} already exists.")
        return
    try:
        with requests.get(url, stream=True, timeout=30) as r:
            r.raise_for_status()
            total = int(r.headers.get('content-length', 0))
            with open(dest, 'wb') as f, tqdm(
                desc=f"Downloading {os.path.basename(dest)}",
                total=total, unit='B', unit_scale=True, unit_divisor=1024
            ) as bar:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        bar.update(len(chunk))
        print(f"[OK] {dest}")
    except Exception as e:
        print(f"[ERROR] Failed to download {url}: {e}")


def main():
    for url, relpath in AUDIO_TARGETS + VIDEO_TARGETS:
        dest = os.path.join(ROOT, relpath)
        safe_makedirs(os.path.dirname(dest))
        download_file(url, dest)

if __name__ == "__main__":
    main()
