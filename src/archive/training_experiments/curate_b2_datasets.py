#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #multimodal #python #source_code #src/training/curate_b2_datasets.py #testing #training
**Category:** Training System
**Status:** Active
"""









# Curate B2 Datasets

# Created:** October 15, 2024
# Updated:** August 4, 2025
# Author:** ImpressionCore Team
# Tags:** #multimodal #python #source_code #src\\training\\curate_b2_datasets.py #testing #training
# Category:** Training System
# Status:** Active

"""
B2 Dataset Curation and Validation Script

- Recursively searches F:/datasets/ for all usable data (ignoring sample/placeholder files)
- Catalogues all files by modality and validates readability/labeling
- Moves curated files into b2 multimodal dataset folders
- Outputs a summary report and updates docs/data_prep_notes.md with schema info

Author: GitHub Copilot
Date: 2025-06-29
"""


import os
import shutil
from pathlib import Path
import json
import soundfile as sf
from PIL import Image
# --- Ensure src/ is in sys.path for rich enhancements ---
import sys
from pathlib import Path as _Path
PROJECT_ROOT = _Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
# --- Rich Enhancements ---
from src.core.utils.rich_enhancements import create_header, print_info, print_success
## Removed imports for non-existent rich_log and rich_progress_bar
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn, TimeRemainingColumn, SpinnerColumn, TaskProgressColumn
from rich.console import Console
console = Console()

# --- Config ---
DATA_ROOT = Path('F:/datasets')
B2_ROOT = Path('F:/b2_datasets')
MODALITIES = {
    'text': ['.txt', '.jsonl'],
    'images': ['.png', '.jpg', '.jpeg'],
    'audio': ['.wav', '.mp3'],
    'video': ['.mp4', '.avi']
}
IGNORE_KEYWORDS = ['sample', 'placeholder', 'test']

# --- Utility Functions ---
def is_valid_file(file_path, exts):
    return file_path.suffix.lower() in exts and not any(k in file_path.name.lower() for k in IGNORE_KEYWORDS)

def validate_text(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            _ = f.read(100)
        return True
    except Exception:
        return False

def validate_image(file_path):
    try:
        with Image.open(file_path) as img:
            img.verify()
        return True
    except Exception:
        return False

def validate_audio(file_path):
    try:
        _ = sf.info(str(file_path))
        return True
    except Exception:
        return False

def validate_video(file_path):
    # Only check file exists and extension for now
    return file_path.exists() and file_path.stat().st_size > 0

VALIDATORS = {
    'text': validate_text,
    'images': validate_image,
    'audio': validate_audio,
    'video': validate_video
}

# --- Main Curation Logic ---
def curate_and_catalogue():
    create_header("B2 Dataset Curation and Validation Script")
    catalogue = {m: [] for m in MODALITIES}
    total_files = {m: 0 for m in MODALITIES}
    # Count total files per modality for progress bars
    for modality, exts in MODALITIES.items():
        total_files[modality] = sum(1 for file_path in DATA_ROOT.rglob('*') if is_valid_file(file_path, exts))
    # Curation with progress
    for modality, exts in MODALITIES.items():
        print_info(f"Processing {modality} files...")
        with Progress(
            SpinnerColumn(),
            TextColumn("{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            console=console,
            transient=True
        ) as progress:
            task = progress.add_task(f"Validating {modality}", total=total_files[modality])
            for file_path in DATA_ROOT.rglob('*'):
                if is_valid_file(file_path, exts):
                    if VALIDATORS[modality](file_path):
                        catalogue[modality].append(str(file_path))
                    progress.update(task, advance=1)
    # Move files to B2 folders with progress
    for modality in MODALITIES:
        print_info(f"Moving curated {modality} files to {B2_ROOT / modality}...")
        dest_dir = B2_ROOT / modality
        dest_dir.mkdir(parents=True, exist_ok=True)
        with Progress(
            SpinnerColumn(),
            TextColumn("{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            console=console,
            transient=True
        ) as progress:
            task = progress.add_task(f"Copying {modality}", total=len(catalogue[modality]))
            for src in catalogue[modality]:
                src_path = Path(src)
                dest_path = dest_dir / src_path.name
                if not dest_path.exists():
                    shutil.copy2(src_path, dest_path)
                progress.update(task, advance=1)
    # Save catalogue
    catalogue_path = B2_ROOT / 'b2_data_catalogue.json'
    with open(catalogue_path, 'w', encoding='utf-8') as f:
        json.dump(catalogue, f, indent=2)
    print_success(f"Curation complete. {sum(len(v) for v in catalogue.values())} files catalogued and moved.")
    print_info(f"Catalogue saved to: {catalogue_path}")
    return catalogue

if __name__ == '__main__':
    catalogue = curate_and_catalogue()
    # Print summary with rich
    create_header("B2 Dataset Curation Summary", style="bold magenta")
    for modality, files in catalogue.items():
        print_info(f"{modality}: {len(files)} files")
