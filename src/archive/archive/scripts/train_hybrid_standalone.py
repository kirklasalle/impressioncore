"""
Standalone Path B Training Launcher - Direct Import

Bypasses src/training/__init__.py to avoid import conflicts.
Directly imports and runs the hybrid trainer.

Created: October 6, 2025
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

import torch
import json
from torch.utils.data import Dataset, DataLoader
from pathlib import Path
from typing import List, Dict, Tuple
import time

print("=" * 70)
print("🚀 LAUNCHING PATH B: HYBRID GPT-2 + B3 TRAINING (STANDALONE)")
print("=" * 70)
print()

# Check CUDA
if torch.cuda.is_available():
    print(f"✅ CUDA available: {torch.cuda.get_device_name(0)}")
    print(f"   VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
else:
    print("⚠️  CUDA not available, using CPU")

print()
print("📊 Training Configuration:")
print("   Dataset: 45,000 train + 2,500 val conversation pairs")
print("   Model: Hybrid GPT-2 + B3 (35.6M params)")
print("   Batch size: 2")
print("   Testing: Every 3 epochs")
print()
print("=" * 70)
print()

try:
    # Import transformers components
    from transformers import GPT2Tokenizer

    # Import our hybrid model directly (avoiding __init__.py)
    sys.path.insert(0, os.path.join(project_root, 'src', 'training'))
    from hybrid_gpt2_b3_model import create_hybrid_model, HybridGPT2B3Model

    # Import trainer components
    from hybrid_gpt2_b3_trainer import ConversationDataset, QualityTester, HybridTrainer

    print("✅ All imports successful!")
    print()

    # Setup
    device = 'cuda' if torch.cuda.is_available() else 'cpu'

    # Load tokenizer
    print("📥 Loading GPT-2 tokenizer...")
    tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
    tokenizer.pad_token = tokenizer.eos_token
    print("✅ Tokenizer loaded")

    # Load datasets
    print("📥 Loading datasets...")
    train_dataset = ConversationDataset(
        "F:/data/conversations/hybrid_training_train.json",
        tokenizer
    )
    val_dataset = ConversationDataset(
        "F:/data/conversations/hybrid_training_val.json",
        tokenizer
    )
    print("✅ Datasets loaded")

    # Phase 1: Base GPT-2
    print()
    print("=" * 70)
    print("PHASE 1: TRAIN BASE GPT-2")
    print("=" * 70)
    print()

    print("🔨 Creating model...")
    model, _ = create_hybrid_model(
        use_moe=False,
        use_enhanced_attention=False,
        use_brain_adapters=False
    )
    print("✅ Model created (30.1M params)")

    print("🔧 Initializing trainer...")
    trainer = HybridTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=train_dataset,
        val_dataset=val_dataset,
        device=device,
        batch_size=2,
        learning_rate=5e-5
    )
    print("✅ Trainer initialized")

    print()
    print("🚀 STARTING TRAINING...")
    print("=" * 70)

    phase1_quality = trainer.train_phase(
        phase_name="PHASE 1: Base GPT-2",
        num_epochs=6,
        quality_target=4.0,
        test_every=3
    )

    print()
    print("=" * 70)
    print(f"✅ PHASE 1 COMPLETE - Quality: {phase1_quality:.2f}/10.0")
    print("=" * 70)

    if phase1_quality < 3.0:
        print("\n⚠️  Phase 1 quality insufficient. Stopping.")
        sys.exit(0)

    print("\n🎉 Training complete! Check F:/models/checkpoints/b3/hybrid/ for saved models.")

except KeyboardInterrupt:
    print("\n\n⚠️  Training interrupted by user")
    sys.exit(1)
except Exception as e:
    print(f"\n\n❌ Training failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
