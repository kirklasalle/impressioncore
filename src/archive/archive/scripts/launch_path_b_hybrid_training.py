"""
Launch Path B: Hybrid GPT-2 + B3 Training

Executes progressive training pipeline:
- Phase 1: Base GPT-2 (30M params)
- Phase 2: + MoE layers (35M params total)
- Phase 3: + Enhanced Attention (35.6M params total)

Tests conversation quality every 3 epochs.
Early stopping if quality degrades.

Created: October 6, 2025
Author: ImpressionCore Team
"""

import sys
import torch

print("=" * 70)
print("🚀 LAUNCHING PATH B: HYBRID GPT-2 + B3 TRAINING")
print("=" * 70)
print()

# Check CUDA availability
if torch.cuda.is_available():
    print(f"✅ CUDA available: {torch.cuda.get_device_name(0)}")
    print(f"   VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
else:
    print("⚠️  CUDA not available, using CPU (training will be slower)")

print()
print("📊 Training Configuration:")
print("   Dataset: 45,000 train + 2,500 val conversation pairs")
print("   Model: Hybrid GPT-2 + B3 (35.6M params)")
print("   Batch size: 2 (memory optimized for GTX 1050 Ti)")
print("   Testing: Every 3 epochs")
print()
print("🎯 Quality Targets:")
print("   Phase 1 (Base GPT-2):     ≥4.0/10.0")
print("   Phase 2 (+ MoE):          ≥6.0/10.0")
print("   Phase 3 (+ Attention):    ≥7.5/10.0")
print()
print("=" * 70)
print()

# Import and run trainer
from src.training.hybrid_gpt2_b3_trainer import main

try:
    main()
except KeyboardInterrupt:
    print("\n\n⚠️  Training interrupted by user")
    sys.exit(1)
except Exception as e:
    print(f"\n\n❌ Training failed with error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
