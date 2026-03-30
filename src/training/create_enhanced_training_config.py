#!/usr/bin/env python3
"""
ImpressionCore-B1 Enhanced Training Configuration
===============================================

Enhanced configuration for scaled-up training with 60% more data.
Optimized for GTX 1050 Ti with improved performance and efficiency.

Author: ImpressionCore Team
Date: 2025-06-11
Version: 1.1.0 - Enhanced Scale-Up
Data: 8 samples per modality (60% increase from 5)
"""

import json
from pathlib import Path
from datetime import datetime

def create_enhanced_training_config():
    """Create enhanced training configuration for scaled-up datasets"""
    
    config = {
        "system_info": {
            "version": "1.1.0 - Enhanced Scale-Up",
            "date": datetime.now().isoformat(),
            "target_hardware": "NVIDIA GTX 1050 Ti (4GB VRAM)",
            "dataset_scale": "60% increase (5 → 8 samples per modality)",
            "optimization_level": "Enhanced for increased data"
        },
        
        "model": {
            "text_embed_dim": 128,
            "image_embed_dim": 128,
            "fusion_dim": 256,
            "num_classes": 10,
            "dropout_rate": 0.1,
            "activation": "relu"
        },
        
        "training": {
            # Enhanced batch configuration for increased data
            "batch_size": 4,  # Maintain for memory efficiency
            "learning_rate": 8e-5,  # Slightly reduced for more data
            "num_epochs": 15,  # Increased for better convergence with more data
            "fp16": True,
            "gradient_clip": 1.0,
            "weight_decay": 1e-4,
            "scheduler": "cosine",
            "warmup_epochs": 2
        },
        
        "optimization": {
            "memory_fraction": 0.75,  # Slightly more aggressive for enhanced data
            "gradient_checkpointing": True,
            "dataloader_workers": 0,
            "pin_memory": True,
            "prefetch_factor": 2,
            "enhanced_mode": True
        },
        
        "datasets": {
            "text": {
                "path": "src/data/minimal_datasets/text_samples",
                "expected_samples": 8,
                "max_length": 512,
                "tokenizer": "basic"
            },
            "images": {
                "path": "src/data/minimal_datasets/images", 
                "expected_samples": 8,
                "size": [224, 224],
                "augmentation": True,
                "normalization": True
            },
            "audio": {
                "path": "src/data/minimal_datasets/audio",
                "expected_samples": 8,
                "sample_rate": 22050,
                "n_mfcc": 13,
                "hop_length": 512
            }
        },
        
        "checkpointing": {
            "save_every": 3,  # More frequent saves with more data
            "keep_best": True,
            "monitor": "loss",
            "patience": 5,
            "early_stopping": True
        },
        
        "logging": {
            "level": "INFO",
            "save_logs": True,
            "rich_output": True,
            "progress_tracking": True,
            "memory_monitoring": True
        },
        
        "enhancement_features": {
            "data_scaling": {
                "original_samples": 5,
                "enhanced_samples": 8,
                "scale_factor": 1.6,
                "percentage_increase": 60
            },
            "performance_optimizations": [
                "Enhanced batch processing",
                "Improved memory utilization", 
                "Optimized learning rate scheduling",
                "Advanced gradient management",
                "Dynamic memory allocation"
            ],
            "quality_improvements": [
                "Richer text content with advanced AI concepts",
                "More sophisticated image patterns",
                "Enhanced audio signal diversity",
                "Improved cross-modal relationships",
                "Better convergence characteristics"
            ]
        }
    }
    
    return config

def save_enhanced_config():
    """Save enhanced training configuration"""
    config = create_enhanced_training_config()
    
    # Create enhanced config directory
    config_dir = Path("src/training/configs")
    config_dir.mkdir(parents=True, exist_ok=True)
    
    # Save configuration
    config_file = config_dir / "enhanced_training_config.json"
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    return str(config_file)

if __name__ == "__main__":
    config_file = save_enhanced_config()
    print(f"✅ Enhanced training configuration saved: {config_file}")
    
    # Print key enhancements
    config = create_enhanced_training_config()
    print(f"\n🚀 Enhanced Training Configuration Summary:")
    print(f"• Dataset Scale: {config['enhancement_features']['data_scaling']['percentage_increase']}% increase")
    print(f"• Samples per modality: {config['enhancement_features']['data_scaling']['enhanced_samples']}")
    print(f"• Training epochs: {config['training']['num_epochs']}")
    print(f"• Learning rate: {config['training']['learning_rate']}")
    print(f"• Memory optimization: Enhanced")
    print(f"• Ready for enhanced training!")
