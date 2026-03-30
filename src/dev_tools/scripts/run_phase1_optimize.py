#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #python #source_code #src/scripts\run_phase1_optimize.py #testing #training
**Category:** Source Code
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:02
# Author:** ImpressionCore Team
# Tags:** #python #source_code #src\\scripts\\run_phase1_optimize.py #testing #training
# Category:** Source Code
# Status:** Active

"""
Automation for Phase 1: Enhanced/Optimized Training
- Assumes initialization checkpoint exists
- Runs train_b2_enhanced_optimized.py with correct config, init checkpoint, and output dir
- Ensures repeatability
"""
import os
import subprocess
import sys
from datetime import datetime


def main():
    # Set paths
    manifest_dir = "F:/b2_datasets/"
    # You may need to update this to the actual checkpoint from initialization
    init_checkpoint = "F:/b2_phase1_init/latest/best_model.pth"
    output_dir = f"F:/b2_phase1_optimize/{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(output_dir, exist_ok=True)

    # 1. Validate manifest (optional, but recommended)
    subprocess.run([
        sys.executable, "prepare_raw_data.py",
        "--output-dir", manifest_dir,
        "--validate"
    ], check=True)

    # 2. Run optimized training
    subprocess.run([
        sys.executable, "train_b2_enhanced_optimized.py",
        "--output-dir", output_dir,
        "--manifest-dir", manifest_dir,
        "--init-checkpoint", init_checkpoint,
        "--seed", "42"
    ], check=True)

    print(f"\n✅ Phase 1 Optimization complete. Output: {output_dir}")

if __name__ == "__main__":
    main()
