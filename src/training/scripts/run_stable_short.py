#!/usr/bin/env python3
"""Wrapper to run a short stable FP32 trainer session with safer defaults.

This script creates the trainer, applies temporary overrides (LR halved, stronger grad clipping, increased warmup,
FP16 disabled), then runs for a specified number of steps. It avoids editing the main trainer file.
"""
from __future__ import annotations

import argparse

# ensure local imports resolve
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.training.scripts.train_unified_sweet_spot import UnifiedSweetSpotTrainer


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--resume', type=str, default='auto')
    parser.add_argument('--steps', type=int, default=200)
    parser.add_argument('--lr-scale', type=float, default=0.5, help='Multiply base LR by this factor')
    parser.add_argument('--max-grad-norm', type=float, default=2.0, help='Gradient clipping max norm')
    parser.add_argument('--lr-warmup-steps', type=int, default=None, help='Explicit warmup steps override')
    parser.add_argument('--batch-size', type=int, default=None, help='Override training batch size')
    parser.add_argument('--gradient-accumulation-steps', type=int, default=None, help='Override gradient accumulation')
    args = parser.parse_args()

    trainer = UnifiedSweetSpotTrainer(resume=args.resume, total_steps=args.steps, auto_resume=True)

    # Apply safer overrides for stability (temporary, in-memory only)
    try:
        # Scale learning rate by requested factor
        base_lr = float(trainer.training_config.get('learning_rate', 3e-4))
        trainer.training_config['learning_rate'] = base_lr * float(args.lr_scale)
        # Apply requested max grad norm
        trainer.training_config['max_grad_norm'] = float(args.max_grad_norm)
        # Apply warmup override if provided, otherwise increase a bit for stability
        if args.lr_warmup_steps is not None:
            trainer.training_config['lr_warmup_steps'] = int(args.lr_warmup_steps)
        else:
            trainer.training_config['lr_warmup_steps'] = max(int(trainer.training_config.get('lr_warmup_steps', 1000)), 2000)
        # Apply batch size / accumulation overrides if provided
        if args.batch_size is not None:
            trainer.training_config['batch_size'] = int(args.batch_size)
        if args.gradient_accumulation_steps is not None:
            trainer.training_config['gradient_accumulation_steps'] = int(args.gradient_accumulation_steps)
        # Use FP32 for this stability run (disable FP16)
        trainer.training_config['fp16'] = False
        print(f"[WRAPPER] Applied overrides: lr={trainer.training_config['learning_rate']}, max_grad_norm={trainer.training_config['max_grad_norm']}, lr_warmup_steps={trainer.training_config['lr_warmup_steps']}, fp16={trainer.training_config['fp16']}, batch_size={trainer.training_config.get('batch_size')}, grad_accum={trainer.training_config.get('gradient_accumulation_steps')}")
    except Exception as e:
        print(f"[WRAPPER] failed to apply overrides: {e}")

    trainer.train()


if __name__ == '__main__':
    main()
