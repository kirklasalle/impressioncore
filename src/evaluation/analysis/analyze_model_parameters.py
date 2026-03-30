#!/usr/bin/env python3
"""Quick model parameter analyzer"""
from pathlib import Path

import torch


def analyze_checkpoint(checkpoint_path):
    """Analyze checkpoint parameters"""
    try:
        checkpoint = torch.load(checkpoint_path, map_location='cpu', weights_only=False)

        if 'model_state_dict' in checkpoint:
            state_dict = checkpoint['model_state_dict']
        elif 'model' in checkpoint:
            state_dict = checkpoint['model']
        else:
            state_dict = checkpoint

        total_params = sum(p.numel() for p in state_dict.values() if hasattr(p, 'numel'))

        print(f"\n📊 {checkpoint_path.name}")
        print(f"   Size: {checkpoint_path.stat().st_size / 1024**3:.2f} GB")
        print(f"   Parameters: {total_params:,}")

        if 'step' in checkpoint:
            print(f"   Step: {checkpoint['step']}")
        if 'epoch' in checkpoint:
            print(f"   Epoch: {checkpoint['epoch']}")
        if 'best_loss' in checkpoint:
            print(f"   Best Loss: {checkpoint['best_loss']}")

        return total_params

    except Exception as e:
        print(f"❌ Error analyzing {checkpoint_path.name}: {e}")
        return 0

# Analyze key models
large_models = [
    "F:/models/checkpoints/b1/impressioncore_b1_flagship_1.pth",
    "F:/models/checkpoints/b1/distillation_checkpoint_epoch_75_quality_0.00_1.pth",
    "F:/models/checkpoints/phase2/checkpoints/b3_phase2_epoch_1_20250806_135110.pth",
    "F:/models/checkpoints/phase2/checkpoints/b3_phase2_epoch_1_20250805_211624.pth",
    "F:/models/checkpoints/b3_training/b3_training_epoch_50_20250805_184808.pth",
    "F:/models/checkpoints/sweet_spot_recovery/recovery_step_5000.pth"
]

print("🔍 ANALYZING IMPRESSIONCORE MODEL PARAMETERS")
print("=" * 60)

for model_path in large_models:
    path = Path(model_path)
    if path.exists():
        analyze_checkpoint(path)
    else:
        print(f"❌ Not found: {path.name}")

print("\n" + "=" * 60)
