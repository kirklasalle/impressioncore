#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #python #source_code #src/training/migrate_models_to_b1_root.py #training
**Category:** Training System
**Status:** Active
"""









# Migrate Models To B1 Root

# Created:** October 15, 2024
# Updated:** August 4, 2025
# Author:** ImpressionCore Team
# Tags:** #python #source_code #src\\training\\migrate_models_to_b1_root.py #training
# Category:** Training System
# Status:** Active

"""
Model Migration Script for ImpressionCore B1

Moves/symlinks all model checkpoints and production models from F:/models/* to the canonical ImpressionCore B1 data root.
Generates a manifest JSON for all production models.

Usage:
    python src/training/migrate_models_to_b1_root.py

Author: GitHub Copilot
Created: 2025-06-22
"""
import os
import shutil
import json
from pathlib import Path
from datetime import datetime

# Source directories
SRC_CHECKPOINTS = Path("F:/models/b1_checkpoints")
SRC_INTEGRATED = Path("F:/models/integrated_model")
SRC_PRODUCTION = Path("F:/models/production_model")

# Target directories
B1_ROOT = Path("F:/impressioncore-b1-embeddings-062125")
DST_CHECKPOINTS = B1_ROOT / "model_checkpoints"
DST_PRODUCTION = B1_ROOT / "production_models"

# Ensure target directories exist
DST_CHECKPOINTS.mkdir(parents=True, exist_ok=True)
DST_PRODUCTION.mkdir(parents=True, exist_ok=True)

# Helper: move or symlink files
def move_or_symlink(src, dst):
    try:
        if dst.exists():
            print(f"[INFO] {dst} already exists. Skipping.")
            return
        try:
            os.symlink(src, dst)
            print(f"[SYMLINK] {src} -> {dst}")
        except Exception:
            shutil.copy2(src, dst)
            print(f"[COPY] {src} -> {dst}")
    except Exception as e:
        print(f"[ERROR] Failed to move/symlink {src} to {dst}: {e}")

# 1. Move/symlink all checkpoints
for folder in [SRC_CHECKPOINTS, SRC_INTEGRATED]:
    for f in folder.glob("*.pt"):
        move_or_symlink(f, DST_CHECKPOINTS / f.name)
    for f in folder.glob("*.pth"):
        move_or_symlink(f, DST_CHECKPOINTS / f.name)

# 2. Move/symlink all production models
for f in SRC_PRODUCTION.glob("*.pth"):
    move_or_symlink(f, DST_PRODUCTION / f.name)

# 3. Symlink/copy flagship model as impressioncore_b1_flagship.pth
flagship_candidates = list(SRC_PRODUCTION.glob("impressioncore_b1_production.pth"))
if not flagship_candidates:
    flagship_candidates = list(SRC_PRODUCTION.glob("best_model.pth"))
if flagship_candidates:
    flagship_src = flagship_candidates[0]
    flagship_dst = DST_PRODUCTION / "impressioncore_b1_flagship.pth"
    move_or_symlink(flagship_src, flagship_dst)
    print(f"[INFO] Flagship model set: {flagship_dst}")
else:
    print("[WARNING] No flagship model found in production_model.")

# 4. Generate manifest for production models
manifest = []
for f in DST_PRODUCTION.glob("*.pth"):
    stat = f.stat()
    manifest.append({
        "filename": f.name,
        "path": str(f.resolve()),
        "size_bytes": stat.st_size,
        "timestamp": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        "description": "Flagship model" if f.name == "impressioncore_b1_flagship.pth" else "Production model"
    })
manifest_path = DST_PRODUCTION / "model_manifest.json"
with open(manifest_path, "w", encoding="utf-8") as mf:
    json.dump(manifest, mf, indent=2)
print(f"[INFO] Model manifest written: {manifest_path}")
