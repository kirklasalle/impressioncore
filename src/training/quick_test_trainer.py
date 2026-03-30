#!/usr/bin/env python3
"""
Quick High School Trainer Test

Simple test to run the high school trainer directly
"""

import sys
from pathlib import Path

# Add proper paths
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

def main():
    print("Starting High School Trainer Test...")
    
    try:
        # Import the trainer
        from src.training.high_school_distillation_trainer import (
            HighSchoolDistillationTrainer, 
            HighSchoolTrainingConfig
        )
        
        print("✓ Imports successful")
        
        # Create config with conservative settings for testing
        config = HighSchoolTrainingConfig(
            model_dim=256,  # Smaller for faster testing
            num_layers=4,   # Fewer layers
            num_heads=4,
            batch_size=1,   # Minimal batch size
            num_epochs=1,   # Just one epoch for testing
            max_seq_length=128,  # Shorter sequences
        )
        
        print("✓ Config created")
        
        # Create trainer
        trainer = HighSchoolDistillationTrainer(config)
        
        print("✓ Trainer initialized")
        print(f"  Student model parameters: {trainer.student_model.get_parameter_count():,}")
        
        # Test a single training step
        print("Running single epoch test...")
        trainer.train()
        
        print("✓ Training completed successfully!")
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
