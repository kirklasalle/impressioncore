#!/usr/bin/env python3
"""
Sparse Transformer Implementation Validation
Tests the sparse attention patterns and memory efficiency
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import torch
import torch.nn as nn
import logging
import time
import tracemalloc
from typing import Dict, Any

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_sparse_imports():
    """Test sparse transformer imports"""
    print("1. Testing Sparse Transformer Imports...")
    
    try:
        from src.models.sparse import (
            SparseAttentionMask, SparseMultiHeadAttention,
            SparseTransformerBlock, SparseTransformer,
            create_sparse_transformer
        )
        print("✓ Core sparse components imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False

def test_attention_masks():
    """Test different sparse attention mask patterns"""
    print("\n2. Testing Attention Mask Patterns...")
    
    try:
        from src.models.sparse import SparseAttentionMask
        
        seq_len = 128
        
        # Test different mask types
        mask_tests = [
            ("local", {"window_size": 32}),
            ("strided", {"stride": 16}),
            ("global", {"global_tokens": 16}),
            ("blockwise", {"block_size": 32}),
            ("random", {"sparsity": 0.9, "seed": 42})
        ]
        
        for mask_type, kwargs in mask_tests:
            if mask_type == "local":
                mask = SparseAttentionMask.create_local_mask(seq_len, **kwargs)
            elif mask_type == "strided":
                mask = SparseAttentionMask.create_strided_mask(seq_len, **kwargs)
            elif mask_type == "global":
                mask = SparseAttentionMask.create_global_mask(seq_len, **kwargs)
            elif mask_type == "blockwise":
                mask = SparseAttentionMask.create_blockwise_mask(seq_len, **kwargs)
            elif mask_type == "random":
                mask = SparseAttentionMask.create_random_mask(seq_len, **kwargs)
            
            # Verify mask properties
            assert mask.shape == (seq_len, seq_len), f"Wrong mask shape: {mask.shape}"
            assert mask.dtype == torch.bool, f"Wrong mask dtype: {mask.dtype}"
            assert mask.diagonal().all(), f"Diagonal should be True for {mask_type}"
            
            sparsity = 1.0 - mask.float().mean().item()
            print(f"✓ {mask_type.capitalize()} mask - Shape: {mask.shape}, Sparsity: {sparsity:.2%}")
        
        # Test mask combination
        mask1 = SparseAttentionMask.create_local_mask(seq_len, window_size=32)
        mask2 = SparseAttentionMask.create_global_mask(seq_len, global_tokens=16)
        combined = SparseAttentionMask.combine_masks([mask1, mask2])
        
        assert combined.shape == (seq_len, seq_len)
        print("✓ Mask combination working correctly")
        
        return True
        
    except Exception as e:
        print(f"✗ Attention mask test failed: {e}")
        return False

def test_sparse_attention():
    """Test sparse multi-head attention"""
    print("\n3. Testing Sparse Multi-Head Attention...")
    
    try:
        from src.models.sparse import SparseMultiHeadAttention
        
        d_model, num_heads = 512, 8
        batch_size, seq_len = 4, 256
        
        # Test different sparse patterns
        patterns = ["local", "global", "strided", "blockwise", "combined"]
        
        for pattern in patterns:
            if pattern == "combined":
                pattern_kwargs = {"patterns": ["local", "global"]}
            else:
                pattern_kwargs = {"window_size": 64} if pattern == "local" else {}
            
            attention = SparseMultiHeadAttention(
                d_model=d_model,
                num_heads=num_heads,
                sparse_pattern=pattern,
                pattern_kwargs=pattern_kwargs
            )
            
            x = torch.randn(batch_size, seq_len, d_model)
            
            # Test forward pass
            with torch.no_grad():
                output = attention(x)
            
            assert output.shape == x.shape, f"Output shape mismatch: {output.shape} vs {x.shape}"
            
            # Test with return_attention
            with torch.no_grad():
                output, attn_weights = attention(x, return_attention=True)
            
            if attn_weights is not None:
                expected_attn_shape = (batch_size, num_heads, seq_len, seq_len)
                assert attn_weights.shape == expected_attn_shape
            
            print(f"✓ {pattern.capitalize()} sparse attention working correctly")
        
        return True
        
    except Exception as e:
        print(f"✗ Sparse attention test failed: {e}")
        return False

def test_sparse_transformer_block():
    """Test sparse transformer block"""
    print("\n4. Testing Sparse Transformer Block...")
    
    try:
        from src.models.sparse import SparseTransformerBlock
        
        d_model, num_heads, d_ff = 512, 8, 2048
        batch_size, seq_len = 4, 256
        
        block = SparseTransformerBlock(
            d_model=d_model,
            num_heads=num_heads,
            d_ff=d_ff,
            sparse_pattern="local",
            pattern_kwargs={"window_size": 64}
        )
        
        x = torch.randn(batch_size, seq_len, d_model)
        
        with torch.no_grad():
            output = block(x)
        
        assert output.shape == x.shape, f"Output shape mismatch: {output.shape} vs {x.shape}"
        
        # Test with attention mask
        attention_mask = torch.ones(batch_size, seq_len, dtype=torch.bool)
        attention_mask[:, seq_len//2:] = False  # Mask second half
        
        with torch.no_grad():
            output = block(x, attention_mask=attention_mask)
        
        assert output.shape == x.shape
        
        print(f"✓ Sparse transformer block - Input: {x.shape}, Output: {output.shape}")
        
        # Test parameter count
        total_params = sum(p.numel() for p in block.parameters())
        trainable_params = sum(p.numel() for p in block.parameters() if p.requires_grad)
        print(f"✓ Parameters - Total: {total_params:,}, Trainable: {trainable_params:,}")
        
        return True
        
    except Exception as e:
        print(f"✗ Sparse transformer block test failed: {e}")
        return False

def test_sparse_transformer():
    """Test full sparse transformer"""
    print("\n5. Testing Sparse Transformer Stack...")
    
    try:
        from src.models.sparse import create_sparse_transformer
        
        # Test different configurations
        configs = [
            {
                "num_layers": 4,
                "d_model": 256,
                "num_heads": 4,
                "d_ff": 1024,
                "max_seq_len": 512,
                "sparse_config": {
                    "patterns": ["local", "global"] * 2,
                    "local_window": 64,
                    "global_tokens": 32
                }
            },
            {
                "num_layers": 6,
                "d_model": 512,
                "num_heads": 8,
                "d_ff": 2048,
                "max_seq_len": 1024,
                "sparse_config": {
                    "patterns": ["local", "strided", "global"] * 2,
                    "local_window": 128,
                    "global_tokens": 64,
                    "stride": 64
                }
            }
        ]
        
        for i, config in enumerate(configs):
            print(f"  Testing config {i+1}...")
            
            model = create_sparse_transformer(**config)
            
            batch_size, seq_len = 2, config["max_seq_len"] // 2
            x = torch.randn(batch_size, seq_len, config["d_model"])
            
            with torch.no_grad():
                output = model(x)
            
            assert output.shape == x.shape, f"Output shape mismatch: {output.shape} vs {x.shape}"
            
            # Test parameter count
            total_params = sum(p.numel() for p in model.parameters())
            trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
            
            print(f"    ✓ Input: {x.shape}, Output: {output.shape}")
            print(f"    ✓ Parameters: {total_params:,}")
        
        return True
        
    except Exception as e:
        print(f"✗ Sparse transformer test failed: {e}")
        return False

def test_memory_efficiency():
    """Test memory efficiency compared to dense attention"""
    print("\n6. Testing Memory Efficiency...")
    
    try:
        from src.models.sparse import create_sparse_transformer
        
        # Test parameters
        d_model, num_heads = 512, 8
        seq_lengths = [256, 512, 1024, 2048]
        
        # Create dense transformer for comparison
        class DenseTransformerBlock(nn.Module):
            def __init__(self, d_model, num_heads, d_ff):
                super().__init__()
                self.attention = nn.MultiheadAttention(d_model, num_heads, batch_first=True)
                self.feed_forward = nn.Sequential(
                    nn.Linear(d_model, d_ff),
                    nn.GELU(),
                    nn.Linear(d_ff, d_model)
                )
                self.norm1 = nn.LayerNorm(d_model)
                self.norm2 = nn.LayerNorm(d_model)
                
            def forward(self, x):
                residual = x
                x = self.norm1(x)
                x, _ = self.attention(x, x, x)
                x = x + residual
                
                residual = x
                x = self.norm2(x)
                x = self.feed_forward(x)
                x = x + residual
                return x
        
        dense_model = DenseTransformerBlock(d_model, num_heads, d_model * 4)
        sparse_model = create_sparse_transformer(
            num_layers=1,
            d_model=d_model,
            num_heads=num_heads,
            d_ff=d_model * 4,
            sparse_config={"patterns": ["local"], "local_window": 128}
        )
        
        print("  Memory usage comparison:")
        print("  Seq Length | Dense Time | Sparse Time | Memory Ratio")
        print("  " + "-" * 52)
        
        for seq_len in seq_lengths:
            if seq_len > 2048:  # Skip very long sequences for dense
                continue
                
            batch_size = max(1, 64 // (seq_len // 256))  # Adjust batch size
            x = torch.randn(batch_size, seq_len, d_model)
            
            # Dense model timing
            start_time = time.time()
            with torch.no_grad():
                _ = dense_model(x)
            dense_time = time.time() - start_time
            
            # Sparse model timing
            start_time = time.time()
            with torch.no_grad():
                _ = sparse_model(x)
            sparse_time = time.time() - start_time
            
            # Memory complexity (theoretical)
            dense_memory = seq_len ** 2
            sparse_memory = seq_len * 128  # Local window size
            memory_ratio = sparse_memory / dense_memory
            
            print(f"  {seq_len:8d}   | {dense_time:8.4f}s | {sparse_time:9.4f}s | {memory_ratio:10.4f}")
        
        print("✓ Memory efficiency test completed")
        return True
        
    except Exception as e:
        print(f"✗ Memory efficiency test failed: {e}")
        return False

def test_gradient_checkpointing():
    """Test gradient checkpointing functionality"""
    print("\n7. Testing Gradient Checkpointing...")
    
    try:
        from src.models.sparse import create_sparse_transformer
        
        model = create_sparse_transformer(
            num_layers=4,
            d_model=256,
            num_heads=4,
            d_ff=1024,
            use_gradient_checkpointing=True
        )
        
        batch_size, seq_len = 2, 256
        x = torch.randn(batch_size, seq_len, 256, requires_grad=True)
        
        # Forward pass
        output = model(x)
        loss = output.sum()
        
        # Backward pass
        loss.backward()
        
        # Check gradients exist
        assert x.grad is not None, "Input gradients should exist"
        
        # Check model gradients
        for name, param in model.named_parameters():
            if param.requires_grad:
                assert param.grad is not None, f"Gradient missing for {name}"
        
        print("✓ Gradient checkpointing working correctly")
        return True
        
    except Exception as e:
        print(f"✗ Gradient checkpointing test failed: {e}")
        return False

def run_sparse_validation():
    """Run comprehensive sparse transformer validation"""
    print("=" * 60)
    print("Sparse Transformer Implementation Validation")
    print("=" * 60)
    
    # Test results
    results = {
        "imports": test_sparse_imports(),
        "attention_masks": test_attention_masks(),
        "sparse_attention": test_sparse_attention(),
        "transformer_block": test_sparse_transformer_block(),
        "transformer_stack": test_sparse_transformer(),
        "memory_efficiency": test_memory_efficiency(),
        "gradient_checkpointing": test_gradient_checkpointing()
    }
    
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 All Sparse Transformer tests passed!")
        print("Ready for integration with ImpressionCore!")
    else:
        print("\n⚠️  Some tests failed. Review implementation.")
    
    return all_passed

if __name__ == "__main__":
    run_sparse_validation()
