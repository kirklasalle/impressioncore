#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #python #source_code #src/core/utils/generate_b2_embedding_catalogue.py
**Category:** Core Implementation
**Status:** Active
"""









# Generate B2 Embedding Catalogue

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:00
# Author:** ImpressionCore Team
# Tags:** #python #source_code #src\\core\\utils\\generate_b2_embedding_catalogue.py
# Category:** Core Implementation
# Status:** Active

"""
Auto-generate b2_embedding_catalogue.json for all modalities (text, images, audio, video).
Scans embedding directories and outputs a complete catalogue JSON.

Usage:
    python generate_b2_embedding_catalogue.py

Output:
    data/b2_embeddings/b2_embedding_catalogue.json
"""
import json
from pathlib import Path

# Root embedding directory
EMBED_ROOT = Path("data/b2_embeddings")

# Modalities and their subfolders
MODALITIES = {
    "text": "text",
    "images": "images",
    "audio": "audio",
    "video": "video"
}

# File extensions for each modality
EXTENSIONS = {
    "text": [".npy"],
    "images": [".npy"],
    "audio": [".npy"],
    "video": [".npy"]
}

def scan_embeddings():
    catalogue = {}
    for modality, subdir in MODALITIES.items():
        folder = EMBED_ROOT / subdir
        if not folder.exists():
            catalogue[modality] = []
            continue
        files = []
        for ext in EXTENSIONS[modality]:
            files.extend(sorted(str(p.resolve()) for p in folder.glob(f"*{ext}")))
        catalogue[modality] = files
    return catalogue

def main():
    catalogue = scan_embeddings()
    out_path = EMBED_ROOT / "b2_embedding_catalogue.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(catalogue, f, indent=2)
    print(f"Catalogue written to {out_path} with counts: " + ", ".join(f"{k}: {len(v)}" for k,v in catalogue.items()))

if __name__ == "__main__":
    main()
