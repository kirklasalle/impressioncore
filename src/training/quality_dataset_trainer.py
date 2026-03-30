#!/usr/bin/env python3
"""
High School Graduate Quality Dataset Trainer

This trainer specifically uses the high-quality conversation dataset
to create a coherent, educational AI conversation partner.

Key Features:
- Uses high-quality educational conversation data
- Smaller model size to prevent overfitting
- Conservative training approach
- Focus on coherent, helpful responses
"""

import sys
from pathlib import Path
import json

# Add proper paths
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

def main():
    print("🎓 High School Graduate Quality Dataset Trainer")
    print("📚 Using high-quality conversation examples")
    print("🎯 Goal: Create coherent, educational conversation partner")
    
    try:
        # Import the trainer
        from src.training.high_school_distillation_trainer import (
            HighSchoolDistillationTrainer, 
            HighSchoolTrainingConfig
        )
        
        print("✓ Trainer imports successful")
        
        # Check if we have the quality dataset
        quality_data_path = project_root / "high_school_training_data.json"
        if quality_data_path.exists():
            with open(quality_data_path, 'r') as f:
                quality_data = json.load(f)
            print(f"✓ Found {len(quality_data)} high-quality conversation examples")
            
            # Show sample data
            print("\n📖 Sample conversation example:")
            sample = quality_data[0]
            print(f"Input: {sample['input'][:60]}...")
            print(f"Output: {sample['output'][:60]}...")
        else:
            print("⚠️  Quality dataset not found - creating it first...")
            # Create the dataset
            exec(open(project_root / "src" / "training" / "create_high_school_dataset.py").read())
            print("✓ Quality dataset created")
        
        # Create config optimized for quality learning
        config = HighSchoolTrainingConfig(
            # Smaller model to prevent overfitting on quality data
            model_dim=128,      # Much smaller (was 512)
            num_layers=2,       # Minimal layers (was 6+)
            num_heads=4,        # Balanced attention heads
            vocab_size=50257,   # Full vocabulary
            max_seq_length=256, # Reasonable context length
            
            # Very conservative training for quality output
            batch_size=1,       # Single example focus
            learning_rate=5e-6, # Very low learning rate
            num_epochs=1,       # Just one epoch to prevent overfitting
            warmup_steps=5,     # Minimal warmup
            weight_decay=0.01,
            
            # Distillation parameters for quality transfer
            temperature=1.5,    # Lower temperature for precision
            alpha=0.3,          # Lower distillation weight
            beta=0.7,           # Higher task loss weight
            
            # Memory optimization
            gradient_checkpointing=True,
            mixed_precision=True,
            max_memory_mb=2500, # Conservative memory usage
        )
        
        print("\n🔧 Quality-focused configuration:")
        print(f"  Model: {config.model_dim}d, {config.num_layers} layers, {config.num_heads} heads")
        print(f"  Training: {config.num_epochs} epoch, LR={config.learning_rate}")
        print(f"  Focus: Quality over quantity, prevent overfitting")
        
        # Create trainer
        trainer = HighSchoolDistillationTrainer(config)
        
        print("✓ Quality-focused trainer initialized")
        print(f"  Student model parameters: {trainer.student_model.get_parameter_count():,}")
        
        print("\n🚀 Starting quality-focused training...")
        print("Expected time: 1-2 minutes")
        print("🎯 Focus: Learning from high-quality conversation examples")
        
        # Run the quality training
        trainer.train()
        
        print("\n🎉 Quality training completed!")
        print("✅ Model trained on high-quality educational conversations")
        print("🎓 Should now produce more coherent, helpful responses")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
