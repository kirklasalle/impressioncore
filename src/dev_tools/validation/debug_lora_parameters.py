#!/usr/bin/env python3
"""
Debug LoRA Parameter Configuration
Investigates why trainable parameters are reported as 0
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import torch
import torch.nn as nn
from peft import LoraConfig, get_peft_model

class SimpleTestModel(nn.Module):
    def __init__(self, input_size=20, hidden_size=50, output_size=10):
        super().__init__()
        self.linear1 = nn.Linear(input_size, hidden_size)
        self.linear2 = nn.Linear(hidden_size, output_size)
        self.activation = nn.ReLU()
        
    def forward(self, x):
        x = self.activation(self.linear1(x))
        x = self.linear2(x)
        return x

def count_parameters(model):
    """Count total and trainable parameters"""
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    return total_params, trainable_params

def debug_lora_parameters():
    print("=" * 60)
    print("LoRA Parameter Configuration Debug")
    print("=" * 60)
    
    # Create base model
    print("\n1. Creating base model...")
    base_model = SimpleTestModel()
    total_base, trainable_base = count_parameters(base_model)
    print(f"   Base model - Total: {total_base}, Trainable: {trainable_base}")
    
    # Show parameter details
    print("\n2. Base model parameters:")
    for name, param in base_model.named_parameters():
        print(f"   {name}: {param.shape}, requires_grad={param.requires_grad}")
    
    # Apply LoRA with different configurations
    print("\n3. Testing different LoRA configurations...")
    
    configs = [
        {"r": 8, "alpha": 16, "dropout": 0.1, "target_modules": ["linear1", "linear2"]},
        {"r": 4, "alpha": 8, "dropout": 0.05, "target_modules": ["linear1"]},
        {"r": 16, "alpha": 32, "dropout": 0.2, "target_modules": ["linear2"]},
    ]
    
    for i, config in enumerate(configs):
        print(f"\n   Config {i+1}: {config}")
        
        # Create fresh model for each test
        test_model = SimpleTestModel()
        
        try:
            # Create LoRA config
            lora_config = LoraConfig(
                r=config["r"],
                lora_alpha=config["alpha"],
                lora_dropout=config["dropout"],
                target_modules=config["target_modules"],
                bias="none",
                task_type="FEATURE_EXTRACTION"
            )
            
            # Apply LoRA
            lora_model = get_peft_model(test_model, lora_config)
            total_lora, trainable_lora = count_parameters(lora_model)
            
            print(f"   Result - Total: {total_lora}, Trainable: {trainable_lora}")
            
            # Show LoRA-specific parameters
            print(f"   LoRA parameters:")
            for name, param in lora_model.named_parameters():
                if param.requires_grad:
                    print(f"     {name}: {param.shape}")
                    
        except Exception as e:
            print(f"   Error: {e}")
    
    # Test with model that has named modules matching our config
    print("\n4. Testing with explicitly named modules...")
    
    class NamedTestModel(nn.Module):
        def __init__(self):
            super().__init__()
            self.layer1 = nn.Linear(20, 50)
            self.layer2 = nn.Linear(50, 10)
            
        def forward(self, x):
            x = torch.relu(self.layer1(x))
            x = self.layer2(x)
            return x
    
    named_model = NamedTestModel()
    print(f"   Named model parameters:")
    for name, param in named_model.named_parameters():
        print(f"     {name}: {param.shape}")
    
    # Apply LoRA to named model
    try:
        lora_config = LoraConfig(
            r=8,
            lora_alpha=16,
            lora_dropout=0.1,
            target_modules=["layer1", "layer2"],
            bias="none",
            task_type="FEATURE_EXTRACTION"
        )
        
        lora_named_model = get_peft_model(named_model, lora_config)
        total_named, trainable_named = count_parameters(lora_named_model)
        
        print(f"   Named LoRA model - Total: {total_named}, Trainable: {trainable_named}")
        
        print(f"   Named LoRA trainable parameters:")
        for name, param in lora_named_model.named_parameters():
            if param.requires_grad:
                print(f"     {name}: {param.shape}")
                
    except Exception as e:
        print(f"   Named model error: {e}")
    
    print("\n" + "=" * 60)
    print("Debug complete!")
    print("=" * 60)

if __name__ == "__main__":
    debug_lora_parameters()
