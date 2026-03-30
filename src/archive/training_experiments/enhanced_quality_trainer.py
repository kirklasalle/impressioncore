#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #attention_mechanism #memory_management #python #source_code #src/training/enhanced_quality_trainer.py #testing #training
**Category:** Training System
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** October 15, 2024
# Updated:** August 4, 2025
# Author:** ImpressionCore Team
# Tags:** #attention_mechanism #memory_management #python #source_code #src\\training\\enhanced_quality_trainer.py #testing #training
# Category:** Training System
# Status:** Active

"""
Enhanced High School Trainer with Better Text Quality

This version uses more epochs and better training parameters to produce
coherent text output instead of gibberish.
"""

import sys
from pathlib import Path

# Add proper paths
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

def main():
    print("🎓 Starting Enhanced High School Trainer for Better Text Quality...")

    try:
        # Import the trainer
        from.training.high_school_distillation_trainer import (
            HighSchoolDistillationTrainer,
            HighSchoolTrainingConfig
        )

        print("✓ Imports successful")

        # Create config with better settings for quality text output
        config = HighSchoolTrainingConfig(
            # Model architecture (keeping reasonable size for 4GB VRAM)
            model_dim=512,      # Larger than quick test
            num_layers=8,       # More layers for better learning
            num_heads=8,        # More attention heads
            vocab_size=50257,   # Full GPT vocabulary
            max_seq_length=512, # Longer sequences for better context

            # Training parameters for better convergence
            batch_size=2,       # Small batch for memory efficiency
            learning_rate=1e-4, # Lower learning rate for stability
            num_epochs=5,       # More epochs for better learning (instead of 1)
            warmup_steps=100,   # Gradual learning rate warmup
            weight_decay=0.01,

            # Distillation parameters optimized for text quality
            temperature=3.0,    # Lower temperature for sharper distributions
            alpha=0.8,          # Higher weight for distillation loss
            beta=0.2,           # Lower weight for task loss initially

            # Memory optimization (keep these for 4GB VRAM)
            gradient_checkpointing=True,
            mixed_precision=True,
            max_memory_mb=3500,
        )

        print("✓ Enhanced config created")
        print(f"  Training epochs: {config.num_epochs}")
        print(f"  Model dimensions: {config.model_dim}")
        print(f"  Sequence length: {config.max_seq_length}")

        # Create trainer
        trainer = HighSchoolDistillationTrainer(config)

        print("✓ Enhanced trainer initialized")
        print(f"  Student model parameters: {trainer.student_model.get_parameter_count():,}")

        # Run enhanced training
        print(f"\n🚀 Running {config.num_epochs} epochs for better text quality...")
        print("Expected training time: 3-5 minutes")
        print("Note: Text quality will improve progressively with each epoch!")

        trainer.train()

        print("\n✅ Enhanced training completed!")
        print("🎯 Text quality should now be significantly better!")
        print("📁 Check the final model outputs in the evaluation section above.")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0

if __name__ == "__main__":
    exit(main())
