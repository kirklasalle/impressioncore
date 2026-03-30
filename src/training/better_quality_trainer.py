#!/usr/bin/env python3
"""
Better Quality Trainer (No Multiprocessing)

This version runs more epochs and disables multiprocessing to avoid import issues.
"""

import sys
from pathlib import Path

# Add proper paths
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

def main():
    print("🎓 Starting Better Quality Trainer (5 epochs, no multiprocessing)...")
    
    try:
        # Import the trainer
        from src.training.high_school_distillation_trainer import (
            HighSchoolDistillationTrainer, 
            HighSchoolTrainingConfig
        )
        
        print("✓ Imports successful")
          # Create config with better settings for quality text output
        config = HighSchoolTrainingConfig(
            # Model architecture (reasonable size for 4GB VRAM)
            model_dim=512,      # Larger than quick test
            num_layers=6,       # More layers for better learning
            num_heads=8,        # More attention heads
            vocab_size=50257,   # Full GPT vocabulary
            max_seq_length=256, # Longer sequences for better context
            
            # Training parameters for better convergence
            batch_size=2,       # Small batch for memory efficiency
            learning_rate=5e-5, # Lower learning rate for stability
            num_epochs=5,       # More epochs for better learning
            warmup_steps=50,    # Gradual learning rate warmup
            weight_decay=0.01,
            
            # Distillation parameters optimized for text quality
            temperature=4.0,    # Good temperature for knowledge transfer
            alpha=0.7,          # Balanced distillation weight
            beta=0.3,           # Task loss weight
            
            # Memory optimization (using correct parameter names)
            gradient_checkpointing=True,
            mixed_precision=True,
            max_memory_mb=3500,
        )
        
        print("✓ Better config created")
        print(f"  Training epochs: {config.num_epochs}")
        print(f"  Model dimensions: {config.model_dim}")
        print(f"  Sequence length: {config.max_seq_length}")
        
        # Create trainer
        trainer = HighSchoolDistillationTrainer(config)
        
        print("✓ Better trainer initialized")
        print(f"  Student model parameters: {trainer.student_model.get_parameter_count():,}")
        
        print("\n🚀 Running 5 epochs for better text quality...")
        print("Expected training time: 3-5 minutes")
        print("Note: Text quality will improve progressively with each epoch!")
        
        # Run training with more epochs
        trainer.train()
        
        print("\n✅ Better quality training completed!")
        print("🎯 The model should now generate more coherent text.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
