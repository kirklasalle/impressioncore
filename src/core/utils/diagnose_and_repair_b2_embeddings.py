#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #python #source_code #src/core/utils/diagnose_and_repair_b2_embeddings.py #training
**Category:** Core Implementation
**Status:** Active
"""









# Diagnose And Repair B2 Embeddings

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:00
# Author:** ImpressionCore Team
# Tags:** #python #source_code #src\\core\\utils\\diagnose_and_repair_b2_embeddings.py #training
# Category:** Core Implementation
# Status:** Active

"""
B2 Embedding Pipeline Diagnostics and Repair
-------------------------------------------
Checks and repairs the B2 embedding pipeline for ImpressionCore.
- Validates b2_embedding_catalogue.json
- Validates data/b2_embeddings/text/ directory and .npy files
- Reports missing/empty catalogue or files
- Auto-populates catalogue if needed

Usage: Run as a standalone script before training.
"""
import json
from pathlib import Path

EMBED_ROOT = Path("data/b2_embeddings")
CATALOGUE_PATH = EMBED_ROOT / "b2_embedding_catalogue.json"
TEXT_DIR = EMBED_ROOT / "text"


def find_npy_files(directory):
    return sorted([str(f.resolve()) for f in Path(directory).glob("*.npy")])

def validate_catalogue(catalogue_path):
    if not catalogue_path.exists():
        print(f"[FATAL] Catalogue file not found: {catalogue_path}")
        return None
    try:
        with open(catalogue_path, encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            print(f"[FATAL] Catalogue is not a dict: {catalogue_path}")
            return None
        return data
    except Exception as e:
        print(f"[FATAL] Failed to read catalogue: {e}")
        return None

def validate_text_embeddings(text_dir):
    if not text_dir.exists():
        print(f"[FATAL] Text embedding directory missing: {text_dir}")
        return []
    npy_files = find_npy_files(text_dir)
    if not npy_files:
        print(f"[FATAL] No .npy files found in {text_dir}")
    return npy_files

def repair_catalogue(catalogue_path, text_npy_files):
    catalogue = {"text": text_npy_files, "images": [], "audio": [], "video": []}
    with open(catalogue_path, "w", encoding="utf-8") as f:
        json.dump(catalogue, f, indent=2)
    print(f"[REPAIR] Catalogue updated with {len(text_npy_files)} text files.")
    return catalogue

def main():
    print("[DIAG] Starting B2 embedding pipeline diagnostics...")
    text_npy_files = validate_text_embeddings(TEXT_DIR)
    catalogue = validate_catalogue(CATALOGUE_PATH)
    needs_repair = False
    if catalogue is None or "text" not in catalogue or not isinstance(catalogue["text"], list):
        print("[WARN] Catalogue missing or invalid 'text' key. Will repair.")
        needs_repair = True
    elif set(catalogue["text"]) != set(text_npy_files):
        print("[WARN] Catalogue 'text' list does not match .npy files. Will repair.")
        needs_repair = True
    if needs_repair:
        catalogue = repair_catalogue(CATALOGUE_PATH, text_npy_files)
    else:
        print(f"[OK] Catalogue and text embeddings are consistent. {len(text_npy_files)} files ready.")
    # Final summary
    if not text_npy_files:
        print("[FATAL] No text embeddings available. Please generate .npy files in data/b2_embeddings/text/.")
    elif len(text_npy_files) < 10:
        print(f"[WARN] Only {len(text_npy_files)} text embeddings found. Training may be limited.")
    else:
        print(f"[READY] {len(text_npy_files)} text embeddings available. Pipeline is ready.")

if __name__ == "__main__":
    main()
