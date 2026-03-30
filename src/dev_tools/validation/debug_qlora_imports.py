#!/usr/bin/env python3
"""
Debug script to isolate QLoRA import issues
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

print("Testing basic imports...")

try:
    import torch
    import torch.nn as nn
    print("✅ PyTorch imports successful")
except Exception as e:
    print(f"❌ PyTorch import failed: {e}")

try:
    from models.trainer import ModelTrainer, TrainingConfig
    print("✅ Trainer imports successful")
except Exception as e:
    print(f"❌ Trainer import failed: {e}")

try:
    from torch.utils.data import DataLoader, TensorDataset
    print("✅ DataLoader imports successful")
except Exception as e:
    print(f"❌ DataLoader import failed: {e}")

try:
    from models.qlora import QLoRAConfig, QLoRAModel, create_qlora_model
    print("✅ QLoRA imports successful")
except Exception as e:
    print(f"❌ QLoRA import failed: {e}")

print("Testing trainer initialization...")
try:
    training_config = TrainingConfig(
        batch_size=2,
        learning_rate=1e-4,
        epochs=1,
        checkpoint_dir="./test_checkpoints",
        device="cpu"
    )
    print("✅ TrainingConfig creation successful")
    
    class TestModel(nn.Module):
        def __init__(self):
            super().__init__()
            self.embedding = nn.Embedding(100, 64)
            self.linear = nn.Linear(64, 100)
        
        def forward(self, input_ids):
            x = self.embedding(input_ids)
            return self.linear(x.mean(dim=1))
    
    print("✅ TestModel definition successful")
    
    dummy_data = torch.randint(0, 100, (10, 5))
    dummy_dataset = TensorDataset(dummy_data)
    dummy_dataloader = DataLoader(dummy_dataset, batch_size=2)
    print("✅ Dummy data creation successful")
    
    model = TestModel()
    trainer = ModelTrainer(
        model=model, 
        config=training_config, 
        train_dataloader=dummy_dataloader
    )
    print("✅ Trainer initialization successful")
    
except Exception as e:
    print(f"❌ Trainer initialization failed: {e}")
    import traceback
    traceback.print_exc()

print("Debug complete.")
