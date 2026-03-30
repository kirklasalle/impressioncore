#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #python #source_code #src/scripts\run_phase1_automation.py #training
**Category:** Source Code
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:02
# Author:** ImpressionCore Team
# Tags:** #python #source_code #src\\scripts\\run_phase1_automation.py #training
# Category:** Source Code
# Status:** Active

"""
Automated Phase 1 Training Pipeline for ImpressionCore
- Prepares/validates manifest
- Runs initialization (train_b2.py)
- Runs optimization (train_b2_enhanced_optimized.py)
- Ensures outputs are in timestamped directories
"""
import datetime
import os
import subprocess


def run(cmd):
    print(f"\n[RUN] {cmd}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed: {cmd}")

def main():
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    base_dir = f"F:/b2_phase1_runs/{timestamp}"
    os.makedirs(base_dir, exist_ok=True)
    # 1. Prepare/validate manifest
    run("python prepare_raw_data.py --output-dir F:/b2_datasets/ --generate-real-manifest --catalogue-path F:/b2_embeddings/b2_embedding_catalogue.json --real-sample-size 1000")
    run("python prepare_raw_data.py --output-dir F:/b2_datasets/ --validate")
    # 2. Initialization/embedding training
    init_dir = os.path.join(base_dir, "init")
    os.makedirs(init_dir, exist_ok=True)
    run(f"python src/training/train_b2.py --output-dir {init_dir}")
    # 3. Optimization training
    opt_dir = os.path.join(base_dir, "optimize")
    os.makedirs(opt_dir, exist_ok=True)
    # Find best checkpoint from init (assume naming convention)
    best_ckpt = os.path.join(init_dir, "best_model.pth")
    if not os.path.exists(best_ckpt):
        # Fallback: pick any .pth file
        ckpts = [f for f in os.listdir(init_dir) if f.endswith('.pth')]
        if ckpts:
            best_ckpt = os.path.join(init_dir, ckpts[0])
        else:
            raise FileNotFoundError("No checkpoint found in init output.")
    run(f"python train_b2_enhanced_optimized.py --output-dir {opt_dir} --init-checkpoint {best_ckpt}")
    print("\n✅ Phase 1 automation complete. All outputs in:", base_dir)

if __name__ == "__main__":
    main()
