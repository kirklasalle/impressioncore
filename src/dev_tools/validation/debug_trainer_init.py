#!/usr/bin/env python3
"""
Debug script for trainer initialization issue
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import torch
    import torch.nn as nn
    print("✅ Basic imports successful")
    
    from models.trainer import ModelTrainer, TrainingConfig
    from torch.utils.data import DataLoader, TensorDataset
    print("✅ Trainer imports successful")
    
    training_config = TrainingConfig(
        batch_size=2,
        learning_rate=1e-4,
        epochs=1,
        checkpoint_dir="./test_checkpoints",
        device="cpu"
    )
    print("✅ TrainingConfig created")
    
    # Simple test model
    class TestModel(nn.Module):
        def __init__(self):
            super().__init__()
            self.embedding = nn.Embedding(100, 64)
            self.linear = nn.Linear(64, 100)
        
        def forward(self, input_ids):
            x = self.embedding(input_ids)
            return self.linear(x.mean(dim=1))
    
    print("✅ TestModel defined")
    
    # Create dummy dataloader
    dummy_data = torch.randint(0, 100, (10, 5))
    dummy_dataset = TensorDataset(dummy_data)
    dummy_dataloader = DataLoader(dummy_dataset, batch_size=2)
    print("✅ Dummy dataloader created")
    
    model = TestModel()
    print("✅ Model instantiated")
    
    trainer = ModelTrainer(
        model=model, 
        config=training_config, 
        train_dataloader=dummy_dataloader
    )
    print("✅ Trainer created successfully")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
