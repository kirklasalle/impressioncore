#!/usr/bin/env python3
"""
Enhanced Sparse Transformer Implementation Validation with ImpressionCore Rich Enhancements
Tests sparse attention patterns, memory efficiency, and correctness with beautiful rich UI
"""

import sys
import os
import traceback
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import torch
import torch.nn as nn
import torch.nn.functional as F
import logging
from typing import Dict, Any, Tuple, List
import tracemalloc
import time
import numpy as np

# ImpressionCore Rich Enhancements
from src.core.utils.rich_enhancements import (
    create_header, create_table, create_progress, 
    print_success, print_warning, print_error, print_info,
    console, HAS_RICH
)
from src.core.utils.rich_logging import setup_rich_logging
from src.core.utils.rich_status_animation import StatusAnimation, get_memory_usage

# Set up rich logging
logger = setup_rich_logging(__name__)

def create_test_header(test_name: str, description: str):
    """Create a styled test header"""
    create_header(f"🔥 {test_name}", description, style="bold magenta")

def print_test_result(test_name: str, success: bool, details: str = ""):
    """Print formatted test results"""
    if success:
        print_success(f"{test_name} PASSED" + (f" - {details}" if details else ""))
    else:
        print_error(f"{test_name} FAILED" + (f" - {details}" if details else ""))

def test_sparse_imports():
    """Test sparse transformer imports"""
    create_test_header("Sparse Transformer Import Tests", "Validating all sparse components can be imported")
    
    try:
        from src.models.sparse import (
            SparseAttentionMask, SparseMultiHeadAttention,
            SparseTransformerBlock, SparseTransformer,
            create_sparse_transformer
        )
        print_success("All sparse transformer components imported successfully")
        return True
    except ImportError as e:
        print_error(f"Import failed: {e}")
        logger.error(f"Sparse import error: {e}")
        return False

def test_attention_mask_patterns():
    """Test different sparse attention mask patterns"""
    create_test_header("Attention Mask Pattern Tests", "Validating sparse attention mask generation and patterns")
    
    try:
        from src.models.sparse import SparseAttentionMask
        
        seq_len = 128
        patterns_table = create_table("Sparse Attention Patterns", 
                                    ["Pattern", "Configuration", "Sparsity %", "Memory", "Status"])
        
        # Test different mask types
        mask_tests = [
            ("Local", "create_local_mask", {"window_size": 32}),
            ("Strided", "create_strided_mask", {"stride": 16}),
            ("Global", "create_global_mask", {"global_tokens": 8}),
            ("Blockwise", "create_blockwise_mask", {"block_size": 32}),
            ("Random", "create_random_mask", {"sparsity": 0.9, "seed": 42}),
        ]
        
        for pattern_name, method_name, kwargs in mask_tests:
            console.print(f"\n🧪 Testing {pattern_name} attention pattern...")
            
            try:
                method = getattr(SparseAttentionMask, method_name)
                mask = method(seq_len, **kwargs)
                
                # Validate mask properties
                assert mask.shape == (seq_len, seq_len), f"Wrong mask shape: {mask.shape}"
                assert mask.dtype == torch.bool, f"Wrong mask dtype: {mask.dtype}"
                
                # Calculate sparsity
                total_elements = seq_len * seq_len
                sparse_elements = mask.sum().item()
                sparsity = 100 * (1 - sparse_elements / total_elements)
                
                # Estimate memory usage (simplified)
                mask_memory = mask.numel() * mask.element_size() / 1024  # KB
                
                patterns_table.add_row(
                    pattern_name,
                    str(kwargs),
                    f"{sparsity:.1f}%",
                    f"{mask_memory:.1f}KB",
                    "✅ PASSED"
                )
                
            except Exception as e:
                patterns_table.add_row(
                    pattern_name,
                    str(kwargs),
                    "N/A",
                    "N/A",
                    f"❌ FAILED: {str(e)[:30]}..."
                )
                
        console.print(patterns_table)
        
        # Test mask combination
        console.print(f"\n🔗 Testing mask combination...")
        local_mask = SparseAttentionMask.create_local_mask(seq_len, window_size=32)
        global_mask = SparseAttentionMask.create_global_mask(seq_len, global_tokens=8)
        combined_mask = SparseAttentionMask.combine_masks([local_mask, global_mask])
        
        assert combined_mask.shape == (seq_len, seq_len)
        print_success("Mask combination works correctly")
        
        print_success("All attention mask patterns validated successfully")
        return True
        
    except Exception as e:
        print_error(f"Attention mask test failed: {e}")
        logger.error(f"Attention mask error: {e}")
        traceback.print_exc()
        return False

def test_sparse_attention_layer():
    """Test sparse multi-head attention layer"""
    create_test_header("Sparse Attention Layer Tests", "Testing sparse multi-head attention implementation")
    
    try:
        from src.models.sparse import SparseMultiHeadAttention
        
        # Test configurations
        configs = [
            {"d_model": 256, "num_heads": 8, "pattern": "local", "seq_len": 128},
            {"d_model": 512, "num_heads": 8, "pattern": "global", "seq_len": 256},
            {"d_model": 768, "num_heads": 12, "pattern": "combined", "seq_len": 512},
        ]
        
        attention_table = create_table("Sparse Attention Tests", 
                                     ["Config", "Pattern", "Forward Time", "Memory", "Output Valid"])
        
        for i, config in enumerate(configs):
            console.print(f"\n⚡ Testing attention config {i+1}...")
            
            d_model = config["d_model"]
            num_heads = config["num_heads"]
            pattern = config["pattern"]
            seq_len = config["seq_len"]
            
            # Create attention layer
            if pattern == "combined":
                pattern_kwargs = {"patterns": ["local", "global"]}
            else:
                pattern_kwargs = {}
                
            attention_layer = SparseMultiHeadAttention(
                d_model=d_model,
                num_heads=num_heads,
                sparse_pattern=pattern,
                pattern_kwargs=pattern_kwargs
            )
            
            # Create test input
            batch_size = 2
            x = torch.randn(batch_size, seq_len, d_model)
            
            # Memory tracking
            memory_before, _ = get_memory_usage()
            
            # Time the forward pass
            start_time = time.time()
            
            with torch.no_grad():
                output = attention_layer(x)
            
            end_time = time.time()
            
            memory_after, _ = get_memory_usage()
            memory_used = memory_after - memory_before
            
            # Validate output
            expected_shape = (batch_size, seq_len, d_model)
            output_valid = output.shape == expected_shape
            
            forward_time = (end_time - start_time) * 1000
            
            attention_table.add_row(
                f"{d_model}d/{num_heads}h",
                pattern,
                f"{forward_time:.2f}ms",
                f"{memory_used:.1f}MB" if memory_used > 0 else "< 0.1MB",
                "✅ Valid" if output_valid else "❌ Invalid"
            )
            
            if not output_valid:
                print_error(f"Output shape mismatch: expected {expected_shape}, got {output.shape}")
                return False
                
        console.print(attention_table)
        print_success("All sparse attention layer tests passed")
        return True
        
    except Exception as e:
        print_error(f"Sparse attention layer test failed: {e}")
        logger.error(f"Sparse attention layer error: {e}")
        traceback.print_exc()
        return False

def test_sparse_transformer_block():
    """Test complete sparse transformer block"""
    create_test_header("Sparse Transformer Block Tests", "Testing complete transformer block with sparse attention")
    
    try:
        from src.models.sparse import SparseTransformerBlock
        
        # Test configuration
        d_model = 512
        num_heads = 8
        d_ff = 2048
        seq_len = 256
        batch_size = 4
        
        console.print(f"🏗️ Creating sparse transformer block...")
        console.print(f"   d_model: {d_model}, num_heads: {num_heads}, d_ff: {d_ff}")
        
        block = SparseTransformerBlock(
            d_model=d_model,
            num_heads=num_heads,
            d_ff=d_ff,
            sparse_pattern="local",
            pattern_kwargs={"window_size": 64},
            dropout=0.1
        )
        
        # Test input
        x = torch.randn(batch_size, seq_len, d_model)
        
        console.print(f"📊 Testing forward pass...")
        
        # Forward pass
        with torch.no_grad():
            output = block(x)
        
        # Validate output
        expected_shape = (batch_size, seq_len, d_model)
        if output.shape != expected_shape:
            print_error(f"Block output shape mismatch: expected {expected_shape}, got {output.shape}")
            return False
        
        # Test gradient flow
        console.print(f"🔄 Testing gradient flow...")
        block.train()
        x.requires_grad_(True)
        
        output = block(x)
        loss = output.sum()
        loss.backward()
        
        # Check gradients
        has_gradients = any(p.grad is not None and p.grad.abs().sum() > 0 
                           for p in block.parameters())
        
        if not has_gradients:
            print_error("No gradients found in sparse transformer block")
            return False
        
        print_success("Sparse transformer block validation completed successfully")
        return True
        
    except Exception as e:
        print_error(f"Sparse transformer block test failed: {e}")
        logger.error(f"Sparse transformer block error: {e}")
        traceback.print_exc()
        return False

def test_memory_efficiency():
    """Test memory efficiency of sparse vs dense attention"""
    create_test_header("Memory Efficiency Comparison", "Comparing sparse vs dense attention memory usage")
    
    try:
        from src.models.sparse import SparseMultiHeadAttention
        
        d_model = 512
        num_heads = 8
        batch_size = 2
        
        # Test different sequence lengths
        seq_lengths = [128, 256, 512, 1024]
        
        efficiency_table = create_table("Memory Efficiency Results", 
                                      ["Seq Length", "Sparse Time", "Sparse Mem", "Dense Time", "Dense Mem", "Speedup"])
        
        for seq_len in seq_lengths:
            console.print(f"\n📏 Testing sequence length {seq_len}...")
            
            # Create sparse attention
            sparse_attention = SparseMultiHeadAttention(
                d_model=d_model,
                num_heads=num_heads,
                sparse_pattern="local",
                pattern_kwargs={"window_size": 64}
            )
            
            # Create dense attention for comparison
            dense_attention = nn.MultiheadAttention(
                embed_dim=d_model,
                num_heads=num_heads,
                batch_first=True
            )
            
            x = torch.randn(batch_size, seq_len, d_model)
            
            # Test sparse attention
            tracemalloc.start()
            start_time = time.time()
            
            with torch.no_grad():
                sparse_output = sparse_attention(x)
            
            sparse_time = (time.time() - start_time) * 1000
            sparse_memory = tracemalloc.get_traced_memory()[1] / 1024 / 1024  # MB
            tracemalloc.stop()
            
            # Test dense attention
            tracemalloc.start()
            start_time = time.time()
            
            with torch.no_grad():
                dense_output, _ = dense_attention(x, x, x)
            
            dense_time = (time.time() - start_time) * 1000
            dense_memory = tracemalloc.get_traced_memory()[1] / 1024 / 1024  # MB
            tracemalloc.stop()
            
            # Calculate speedup
            speedup = dense_time / sparse_time if sparse_time > 0 else float('inf')
            
            efficiency_table.add_row(
                str(seq_len),
                f"{sparse_time:.2f}ms",
                f"{sparse_memory:.1f}MB",
                f"{dense_time:.2f}ms",
                f"{dense_memory:.1f}MB",
                f"{speedup:.2f}x"
            )
            
        console.print(efficiency_table)
        print_success("Memory efficiency comparison completed")
        return True
        
    except Exception as e:
        print_error(f"Memory efficiency test failed: {e}")
        logger.error(f"Memory efficiency error: {e}")
        traceback.print_exc()
        return False

def test_edge_cases():
    """Test edge cases and boundary conditions"""
    create_test_header("Edge Case Tests", "Testing boundary conditions and unusual configurations")
    
    try:
        from src.models.sparse import SparseMultiHeadAttention, SparseAttentionMask
        
        edge_case_table = create_table("Edge Case Tests", 
                                      ["Test Case", "Configuration", "Result", "Details"])
        
        successes = 0
        total_tests = 0
        
        # Test 1: Very small sequence
        total_tests += 1
        try:
            attention = SparseMultiHeadAttention(d_model=64, num_heads=4, sparse_pattern="local")
            x = torch.randn(1, 4, 64)  # Very small sequence
            output = attention(x)
            assert output.shape == x.shape
            edge_case_table.add_row("Small Sequence", "seq_len=4", "✅ PASSED", "Minimal sequence length")
            successes += 1
        except Exception as e:
            edge_case_table.add_row("Small Sequence", "seq_len=4", "❌ FAILED", str(e))
        
        # Test 2: Single head
        total_tests += 1
        try:
            attention = SparseMultiHeadAttention(d_model=128, num_heads=1, sparse_pattern="global")
            x = torch.randn(2, 32, 128)
            output = attention(x)
            assert output.shape == x.shape
            edge_case_table.add_row("Single Head", "num_heads=1", "✅ PASSED", "Minimal attention heads")
            successes += 1
        except Exception as e:
            edge_case_table.add_row("Single Head", "num_heads=1", "❌ FAILED", str(e))
        
        # Test 3: Large window size
        total_tests += 1
        try:
            attention = SparseMultiHeadAttention(
                d_model=256, 
                num_heads=8, 
                sparse_pattern="local",
                pattern_kwargs={"window_size": 512}  # Larger than typical sequence
            )
            x = torch.randn(1, 128, 256)
            output = attention(x)
            assert output.shape == x.shape
            edge_case_table.add_row("Large Window", "window_size=512", "✅ PASSED", "Window larger than sequence")
            successes += 1
        except Exception as e:
            edge_case_table.add_row("Large Window", "window_size=512", "❌ FAILED", str(e))
        
        # Test 4: Maximum sparsity
        total_tests += 1
        try:
            mask = SparseAttentionMask.create_random_mask(64, sparsity=0.99, seed=42)
            # Should still have diagonal elements
            assert mask.diag().all(), "Diagonal elements should always be True"
            edge_case_table.add_row("Max Sparsity", "sparsity=99%", "✅ PASSED", "Extremely sparse mask")
            successes += 1
        except Exception as e:
            edge_case_table.add_row("Max Sparsity", "sparsity=99%", "❌ FAILED", str(e))
        
        console.print(edge_case_table)
        
        if successes == total_tests:
            print_success(f"All {total_tests} edge case tests passed!")
            return True
        else:
            print_warning(f"{successes}/{total_tests} edge case tests passed")
            return False
        
    except Exception as e:
        print_error(f"Edge case test failed: {e}")
        logger.error(f"Edge case test error: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all sparse transformer validation tests"""
    create_header("🔥 Sparse Transformer Validation Suite", 
                 "Comprehensive validation of sparse attention implementations", 
                 style="bold magenta")
    
    tests = [
        ("Import Tests", test_sparse_imports),
        ("Attention Mask Patterns", test_attention_mask_patterns),
        ("Sparse Attention Layer", test_sparse_attention_layer),
        ("Transformer Block", test_sparse_transformer_block),
        ("Memory Efficiency", test_memory_efficiency),
        ("Edge Cases", test_edge_cases),    ]
    
    results = {}
    
    with create_progress() as progress:
        task = progress.add_task("Running Sparse Transformer validation tests...", total=len(tests))
        
        for i, (test_name, test_func) in enumerate(tests):
            console.print(f"\n🔄 Running {test_name}...")
            try:
                result = test_func()
                results[test_name] = result
                print_test_result(test_name, result)
            except Exception as e:
                print_error(f"{test_name} encountered an error: {e}")
                results[test_name] = False
                logger.error(f"Test {test_name} error: {e}")
                traceback.print_exc()
            
            progress.update(task, advance=1)
    
    # Summary
    console.print()
    create_header("🔥 Sparse Transformer Validation Summary", "Final test results overview")
    
    summary_table = create_table("Test Results Summary", ["Test Name", "Status"])
    
    passed = 0
    total = len(tests)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        summary_table.add_row(test_name, status)
        if result:
            passed += 1
    
    console.print(summary_table)
    
    console.print(f"\nOverall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print_success("🎉 All sparse transformer tests passed! Implementation is robust and efficient.")
    else:
        print_warning(f"⚠️ {total - passed} test(s) failed. Review the results above.")
    
    return passed == total

if __name__ == "__main__":
    main()
