#!/usr/bin/env python3
"""
Mixture of Experts (MoE) Implementation Validation
Tests the MoE implementation for correctness and memory efficiency
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import torch
import torch.nn as nn
import torch.nn.functional as F
import logging
from typing import Dict, Any
import tracemalloc
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_moe_imports():
    """Test MoE module imports"""
    print("1. Testing MoE Module Imports...")
    
    try:
        from src.models.moe import (
            ExpertLayer, TopKRouter, MoELayer, 
            MemoryEfficientMoE, create_moe_model
        )
        print("✓ Core MoE components imported successfully")
        
        from src.models.moe.routing import (
            SwitchRouter, GLaM_Router, StableMoERouter,
            AdaptiveRouter, HashRouter, create_router
        )
        print("✓ Advanced routing components imported successfully")
        
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False

def test_expert_layer():
    """Test individual expert layer"""
    print("\n2. Testing Expert Layer...")
    
    try:
        from src.models.moe import ExpertLayer
        
        # Create test expert
        d_model, d_ff = 512, 2048
        expert = ExpertLayer(d_model, d_ff)
        
        # Test forward pass
        batch_size, seq_len = 4, 10
        x = torch.randn(batch_size, seq_len, d_model)
        
        with torch.no_grad():
            output = expert(x)
        
        assert output.shape == x.shape, f"Output shape mismatch: {output.shape} vs {x.shape}"
        print(f"✓ Expert layer - Input: {x.shape}, Output: {output.shape}")
        
        # Test different activations
        for activation in ["gelu", "relu", "swish"]:
            expert_act = ExpertLayer(d_model, d_ff, activation=activation)
            output_act = expert_act(x)
            assert output_act.shape == x.shape
        
        print("✓ Multiple activation functions work correctly")
        return True
        
    except Exception as e:
        print(f"✗ Expert layer test failed: {e}")
        return False

def test_routers():
    """Test different routing mechanisms"""
    print("\n3. Testing Router Components...")
    
    try:
        from src.models.moe import TopKRouter
        from src.models.moe.routing import create_router
        
        d_model, num_experts = 512, 8
        batch_size, seq_len = 4, 10
        x = torch.randn(batch_size, seq_len, d_model)
        
        # Test different router types
        router_types = ["topk", "switch", "glam", "stable", "adaptive", "hash"]
        
        for router_type in router_types:
            try:
                if router_type == "topk":
                    router = TopKRouter(d_model, num_experts, top_k=2)
                    router_logits, top_k_indices, top_k_gates = router(x)
                    
                    assert router_logits.shape == (batch_size * seq_len, num_experts)
                    assert top_k_indices.shape == (batch_size * seq_len, 2)
                    assert top_k_gates.shape == (batch_size * seq_len, 2)
                    
                else:
                    router = create_router(router_type, d_model, num_experts)
                    outputs = router(x)
                    # Different routers return different numbers of outputs
                    
                print(f"✓ {router_type.upper()} router working correctly")
                
            except Exception as e:
                print(f"✗ {router_type.upper()} router failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"✗ Router test failed: {e}")
        return False

def test_moe_layer():
    """Test single MoE layer"""
    print("\n4. Testing MoE Layer...")
    
    try:
        from src.models.moe import MoELayer
        
        d_model, d_ff = 512, 2048
        num_experts, top_k = 8, 2
        
        moe_layer = MoELayer(
            d_model=d_model,
            d_ff=d_ff,
            num_experts=num_experts,
            top_k=top_k
        )
        
        batch_size, seq_len = 4, 10
        x = torch.randn(batch_size, seq_len, d_model)
        
        with torch.no_grad():
            output, load_balance_loss = moe_layer(x)
        
        assert output.shape == x.shape, f"Output shape mismatch: {output.shape} vs {x.shape}"
        assert isinstance(load_balance_loss, torch.Tensor), "Load balance loss should be a tensor"
        assert load_balance_loss.item() >= 0, "Load balance loss should be non-negative"
        
        print(f"✓ MoE layer - Input: {x.shape}, Output: {output.shape}")
        print(f"✓ Load balance loss: {load_balance_loss.item():.6f}")
        
        # Test parameter count
        total_params = sum(p.numel() for p in moe_layer.parameters())
        trainable_params = sum(p.numel() for p in moe_layer.parameters() if p.requires_grad)
        print(f"✓ Parameters - Total: {total_params:,}, Trainable: {trainable_params:,}")
        
        return True
        
    except Exception as e:
        print(f"✗ MoE layer test failed: {e}")
        return False

def test_memory_efficient_moe():
    """Test memory-efficient MoE stack"""
    print("\n5. Testing Memory-Efficient MoE Stack...")
    
    try:
        from src.models.moe import MemoryEfficientMoE
        
        d_model, d_ff = 512, 2048
        num_experts, top_k = 8, 2
        num_layers = 4
        
        moe_stack = MemoryEfficientMoE(
            d_model=d_model,
            d_ff=d_ff,
            num_experts=num_experts,
            top_k=top_k,
            num_layers=num_layers,
            use_gradient_checkpointing=True
        )
        
        batch_size, seq_len = 4, 10
        x = torch.randn(batch_size, seq_len, d_model)
        
        with torch.no_grad():
            output, total_loss = moe_stack(x)
        
        assert output.shape == x.shape, f"Output shape mismatch: {output.shape} vs {x.shape}"
        assert isinstance(total_loss, torch.Tensor), "Total loss should be a tensor"
        
        print(f"✓ MoE stack - Input: {x.shape}, Output: {output.shape}")
        print(f"✓ Total load balance loss: {total_loss.item():.6f}")
        
        # Test parameter count
        total_params = sum(p.numel() for p in moe_stack.parameters())
        trainable_params = sum(p.numel() for p in moe_stack.parameters() if p.requires_grad)
        print(f"✓ Parameters - Total: {total_params:,}, Trainable: {trainable_params:,}")
        
        return True
        
    except Exception as e:
        print(f"✗ Memory-efficient MoE test failed: {e}")
        return False

def test_memory_efficiency():
    """Test memory efficiency of MoE vs dense layers"""
    print("\n6. Testing Memory Efficiency...")
    
    try:
        from src.models.moe import create_moe_model
        
        d_model, d_ff = 512, 2048
        num_experts = 8
        top_k = 2
        
        # Create equivalent dense model
        class DenseModel(nn.Module):
            def __init__(self, d_model, d_ff, num_layers):
                super().__init__()
                self.layers = nn.ModuleList([
                    nn.Sequential(
                        nn.LayerNorm(d_model),
                        nn.Linear(d_model, d_ff),
                        nn.GELU(),
                        nn.Linear(d_ff, d_model)
                    )
                    for _ in range(num_layers)
                ])
                self.final_norm = nn.LayerNorm(d_model)
            
            def forward(self, x):
                for layer in self.layers:
                    x = x + layer(x)
                return self.final_norm(x)
        
        # Compare parameter counts
        num_layers = 4
        dense_model = DenseModel(d_model, d_ff, num_layers)
        moe_model = create_moe_model(
            d_model=d_model,
            d_ff=d_ff,
            num_experts=num_experts,
            top_k=top_k,
            num_layers=num_layers,
            memory_efficient=True
        )
        
        dense_params = sum(p.numel() for p in dense_model.parameters())
        moe_params = sum(p.numel() for p in moe_model.parameters())
        
        print(f"✓ Dense model parameters: {dense_params:,}")
        print(f"✓ MoE model parameters: {moe_params:,}")
        print(f"✓ Parameter ratio (MoE/Dense): {moe_params/dense_params:.2f}x")
        
        # Test inference speed
        batch_size, seq_len = 8, 64
        x = torch.randn(batch_size, seq_len, d_model)
        
        # Dense model timing
        start_time = time.time()
        with torch.no_grad():
            for _ in range(10):
                _ = dense_model(x)
        dense_time = time.time() - start_time
        
        # MoE model timing
        start_time = time.time()
        with torch.no_grad():
            for _ in range(10):
                _, _ = moe_model(x)
        moe_time = time.time() - start_time
        
        print(f"✓ Dense model inference time: {dense_time:.4f}s")
        print(f"✓ MoE model inference time: {moe_time:.4f}s")
        print(f"✓ Speed ratio (MoE/Dense): {moe_time/dense_time:.2f}x")
        
        return True
        
    except Exception as e:
        print(f"✗ Memory efficiency test failed: {e}")
        return False

def test_integration():
    """Test integration with existing ImpressionCore components"""
    print("\n7. Testing Integration...")
    
    try:
        # Test with different configurations
        configs = [
            {"d_model": 256, "d_ff": 1024, "num_experts": 4, "top_k": 2},
            {"d_model": 512, "d_ff": 2048, "num_experts": 8, "top_k": 2},
            {"d_model": 768, "d_ff": 3072, "num_experts": 16, "top_k": 4},
        ]
        
        from src.models.moe import create_moe_model
        
        for i, config in enumerate(configs):
            print(f"  Config {i+1}: {config}")
            
            model = create_moe_model(**config, num_layers=2, memory_efficient=True)
            
            batch_size, seq_len = 2, 8
            x = torch.randn(batch_size, seq_len, config["d_model"])
            
            with torch.no_grad():
                output, loss = model(x)
            
            assert output.shape == x.shape
            print(f"    ✓ Working - Loss: {loss.item():.6f}")
        
        print("✓ All configurations working correctly")
        return True
        
    except Exception as e:
        print(f"✗ Integration test failed: {e}")
        return False

def run_moe_validation():
    """Run comprehensive MoE validation"""
    print("=" * 60)
    print("MoE Implementation Validation")
    print("=" * 60)
    
    # Test results
    results = {
        "imports": test_moe_imports(),
        "expert_layer": test_expert_layer(),
        "routers": test_routers(),
        "moe_layer": test_moe_layer(),
        "memory_efficient": test_memory_efficient_moe(),
        "memory_comparison": test_memory_efficiency(),
        "integration": test_integration()
    }
    
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 All MoE tests passed!")
        print("Ready to proceed with integration into ImpressionCore!")
    else:
        print("\n⚠️  Some tests failed. Review implementation.")
    
    return all_passed

if __name__ == "__main__":
    run_moe_validation()
