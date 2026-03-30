#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #attention_mechanism #memory_management #python #source_code #src/training/better_text_trainer.py #testing #training
**Category:** Training System
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** October 15, 2024
# Updated:** August 4, 2025
# Author:** ImpressionCore Team
# Tags:** #attention_mechanism #memory_management #python #source_code #src\\training\\better_text_trainer.py #testing #training
# Category:** Training System
# Status:** Active

"""
Improved Text Quality Training - Simple Approach

This modifies the working quick_test_trainer to use better parameters
for coherent text generation instead of gibberish.
"""

import sys
from pathlib import Path

# Add proper paths
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

def main():
    print("🎯 Starting Improved Text Quality Training...")
    print("Goal: Fix gibberish output with better training parameters")

    try:
        # Import the trainer
        from.training.high_school_distillation_trainer import (
            HighSchoolDistillationTrainer,
            HighSchoolTrainingConfig
        )

        print("✓ Imports successful")

        # Improved config - keep working settings but enhance for text quality
        config = HighSchoolTrainingConfig(
            model_dim=512,      # Larger than original 256
            num_layers=6,       # More layers than original 4
            num_heads=8,        # More attention heads
            batch_size=1,       # Keep minimal for memory
            num_epochs=3,       # More epochs than original 1
            max_seq_length=256, # Reasonable sequence length
            learning_rate=1e-4, # Lower learning rate for stability
            temperature=2.0,    # Lower temperature for sharper outputs
            alpha=0.8,          # Higher distillation weight
            beta=0.2,           # Lower task weight
        )

        print("✓ Improved config created")
        print(f"  Epochs: {config.num_epochs} (was 1)")
        print(f"  Model size: {config.model_dim}d (was 256d)")
        print(f"  Layers: {config.num_layers} (was 4)")

        # Create trainer
        trainer = HighSchoolDistillationTrainer(config)

        print("✓ Trainer initialized")
        print(f"  Student model parameters: {trainer.student_model.get_parameter_count():,}")

        print(f"\n🚀 Running {config.num_epochs} epochs for better text quality...")
        print("This should produce much more coherent text!")

        # Run training
        trainer.train()

        print("\n✅ Improved training completed!")
        print("🎉 Text should now be much more coherent than gibberish!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0

if __name__ == "__main__":
    exit(main())
