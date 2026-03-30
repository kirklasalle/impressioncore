#!/usr/bin/env python3
"""
Quick debug script for QLoRA tensor size issues.
"""

import torch
import torch.nn as nn
from src.models.qlora import QLoRAConfig, QLoRALinear, QLoRAModel

def debug_qlora_issue():
    """Debug the tensor size mismatch issue."""
    print("🔍 Debugging QLoRA tensor size issue...")
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    # Create a simple model
    class SimpleModel(nn.Module):
        def __init__(self):
            super().__init__()
            self.linear = nn.Linear(512, 512)
            
        def forward(self, x):
            return self.linear(x)
    
    # Test 1: QLoRA Linear layer directly
    print("\n📝 Test 1: QLoRA Linear Layer")
    try:
        config = QLoRAConfig(r=4, lora_alpha=8)
        qlora_linear = QLoRALinear(512, 512, config, device=device)
        x = torch.randn(2, 64, 512, device=device)
        print(f"Input shape: {x.shape}")
        
        output = qlora_linear(x)
        print(f"Output shape: {output.shape}")
        print("✅ QLoRA Linear works!")
        
    except Exception as e:
        print(f"❌ QLoRA Linear failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: QLoRA Model conversion
    print("\n📝 Test 2: QLoRA Model Conversion")
    try:
        base_model = SimpleModel().to(device)
        config = QLoRAConfig(r=4, lora_alpha=8, target_modules=['linear'])
        
        print("Original model:")
        x = torch.randn(2, 64, 512, device=device)
        orig_out = base_model(x)
        print(f"Original output shape: {orig_out.shape}")
        
        print("Converting to QLoRA...")
        qlora_model = QLoRAModel(base_model, config)
        
        print("Testing QLoRA model:")
        qlora_out = qlora_model(x)
        print(f"QLoRA output shape: {qlora_out.shape}")
        print("✅ QLoRA Model works!")
        
    except Exception as e:
        print(f"❌ QLoRA Model failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_qlora_issue()
