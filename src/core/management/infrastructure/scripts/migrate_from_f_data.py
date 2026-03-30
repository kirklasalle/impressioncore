#!/usr/bin/env python3
r"""
Migration Script: F:\data to F:\models
=====================================

Migrates existing models from F:\data structure to new F:\models structure.
"""

import shutil
from pathlib import Path

from rich.console import Console


def migrate_models():
    console = Console()

    # Migration mappings
    _migrations = {
        "F:/data/training/checkpoints/*.pth": "F:/models/checkpoints/legacy/",
        "F:/data/distillation/ollama_progressive/": "F:/models/distillation/ollama_progressive/",
        "F:/data/distillation/remote_api/": "F:/models/distillation/remote_api/",
        "F:/data/training/": "F:/models/training/legacy/"
    }

    console.print(r"🚀 Starting F:\data to F:\models migration...")

    # Best quality model priority migration
    best_quality_source = "F:/data/training/checkpoints/b3_best_quality_model_20250802_124801.pth"
    best_quality_dest = "F:/models/checkpoints/best_quality/"

    if Path(best_quality_source).exists():
        shutil.copy2(best_quality_source, best_quality_dest)
        console.print(f"✅ Migrated best quality model to {best_quality_dest}")

    console.print("✅ Migration completed!")

if __name__ == "__main__":
    migrate_models()
