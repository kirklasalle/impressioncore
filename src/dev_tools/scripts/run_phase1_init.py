#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #python #source_code #src/scripts\run_phase1_init.py #training
**Category:** Source Code
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:02
# Author:** ImpressionCore Team
# Tags:** #python #source_code #src\\scripts\\run_phase1_init.py #training
# Category:** Source Code
# Status:** Active

"""
Automation for Phase 1: Initialization/Full Embedding Training
- Prepares and validates manifest
- Runs train_b2.py with correct config and output dir
- Ensures repeatability
"""
import os
import subprocess
import sys
from datetime import datetime


def main():
    # Set paths
    manifest_dir = "F:/b2_datasets/"
    catalogue_path = "F:/b2_embeddings/b2_embedding_catalogue.json"
    output_dir = f"F:/b2_phase1_init/{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(output_dir, exist_ok=True)

    # 1. Prepare/validate manifest
    subprocess.run([
        sys.executable, "prepare_raw_data.py",
        "--output-dir", manifest_dir,
        "--generate-real-manifest",
        "--catalogue-path", catalogue_path,
        "--real-sample-size", "1000"
    ], check=True)
    subprocess.run([
        sys.executable, "prepare_raw_data.py",
        "--output-dir", manifest_dir,
        "--validate"
    ], check=True)

    # 2. Run initialization training
    subprocess.run([
        sys.executable, "src/training/train_b2.py",
        "--output-dir", output_dir,
        "--manifest-dir", manifest_dir,
        "--seed", "42"
    ], check=True)

    print(f"\n✅ Phase 1 Initialization complete. Output: {output_dir}")

if __name__ == "__main__":
    main()
