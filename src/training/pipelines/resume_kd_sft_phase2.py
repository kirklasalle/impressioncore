#!/usr/bin/env python3
"""
Resume KD + SFT Training (Phase 2)
==================================

Resumes training from step 5000 using the existing checkpoint.
Extends training to 6000 steps.
"""

import sys
from pathlib import Path

# Ensure project root is in sys.path
_file_path = Path(__file__).resolve()
_parents = _file_path.parents
_PROJECT_ROOT = _parents[3] if len(_parents) > 3 else _parents[-1]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from src.training.pipelines.kd_sft_curriculum import KDConfig, run_kd_sft


def main():
    print("🚀 Resuming Phase 2 Training from Step 5000...")

    # Configure to resume
    cfg = KDConfig(
        base_checkpoint="F:/models/checkpoints/kd_sft_phase2/step_5000.pt",
        output_dir="F:/models/checkpoints/kd_sft_phase2_resume",
        max_steps=6000,  # Extend by 1000 steps
        warmup_steps=100, # Re-warmup slightly
        save_every=200,
        log_every=10,
        eval_every=200,
        accum_steps=32, # Keep effective batch size high
        micro_batch=1,
        device="cuda",
        fp16=True
    )

    print(f"   Base Checkpoint: {cfg.base_checkpoint}")
    print(f"   Output Directory: {cfg.output_dir}")
    print(f"   Target Steps: {cfg.max_steps}")

    run_kd_sft(cfg)

if __name__ == "__main__":
    main()
