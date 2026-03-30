#!/usr/bin/env python3
"""Resume model weights only into the UnifiedSweetSpotTrainer and run a short diagnostic.

This script instantiates the trainer with no resume, calls setup_model_and_optimizer (to create optimizer
fresh), then loads only the model weights from the checkpoint (skipping optimizer/scaler state) and runs
`trainer.train()` for a small number of steps (overriding max_steps).

Usage: python tools/resume_model_only_run.py --checkpoint <path> --steps 50
"""
import argparse
from pathlib import Path

import torch

from src.training.scripts.train_unified_sweet_spot import UnifiedSweetSpotTrainer


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--checkpoint', required=True)
    parser.add_argument('--steps', type=int, default=50)
    args = parser.parse_args()

    ckpt_path = Path(args.checkpoint)
    if not ckpt_path.exists():
        print('Checkpoint not found:', ckpt_path)
        return

    trainer = UnifiedSweetSpotTrainer(resume='none', total_steps=args.steps, auto_resume=False)
    # create model/optimizer/scheduler/scaler without resuming
    trainer.setup_model_and_optimizer()
    # load only model weights from checkpoint
    ckpt = torch.load(str(ckpt_path), map_location=trainer.device)
    model_state = ckpt.get('model_state_dict', ckpt)
    try:
        trainer.model.load_state_dict(model_state)
        print('Loaded model weights only')
    except Exception as e:
        print('Failed to load model weights:', e)

    # Ensure fp16 mode follows training_config; force fp16=False for this diagnostic
    trainer.training_config['fp16'] = False
    trainer.training_config['max_steps'] = args.steps
    trainer.setup_data_loader()
    # run training loop (this will use trainer._dump_bad_batch if NaNs detected)
    trainer.train()


if __name__ == '__main__':
    main()
