#!/usr/bin/env python3
"""
Performance optimization test fixes for ImpressionCore.

This file contains corrected test implementations to address the issues
found when running the comprehensive test suite.
"""

import torch
import torch.nn as nn
import pytest
import time
import logging
from typing import Dict, Any
import traceback
import gc
import psutil

# ImpressionCore imports  
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.utils.memory_optimization.fused_attention import (
    FusedMultiHeadAttention,
    FusedCrossModalAttention,
    FusedExpertAttention
)
from core.utils.memory_optimization.quantization import (
    QuantizationManager,
    AdaptivePrecisionManager,
    EnhancedQuantizationManager,
    QuantizationPrecision
)
from modules.attention.attention_manager import AttentionManager

logger = logging.getLogger(__name__)

class FixedFusedAttentionTests:
    """Fixed fused attention tests with correct parameters."""
    
    def test_fused_multihead_attention_creation(self):
        """Test that fused multi-head attention can be created with correct attributes"""
        hidden_size, num_heads = 512, 8
        
        fused_attention = FusedMultiHeadAttention(
            hidden_size=hidden_size,
            num_heads=num_heads,
            use_flash_attention=False  # Disable for testing
        )
        
        assert fused_attention.hidden_size == hidden_size
        assert fused_attention.num_heads == num_heads
        assert hasattr(fused_attention, 'qkv_proj')  # Correct attribute name
        assert hasattr(fused_attention, 'out_proj')
        
    def test_fused_attention_forward_pass(self):
        """Test that fused attention forward pass works correctly"""
        hidden_size, num_heads = 512, 8
        batch_size, seq_len = 2, 64
        
        fused_attention = FusedMultiHeadAttention(
            hidden_size=hidden_size,
            num_heads=num_heads,
            use_flash_attention=False
        )
        
        input_tensor = torch.randn(batch_size, seq_len, hidden_size)
        # No attention mask for simplicity - the module should handle None
        
        output = fused_attention(input_tensor)
        
        # Validate output shape
        assert output.shape == input_tensor.shape
        assert output.dtype == input_tensor.dtype
        
    def test_fused_cross_modal_attention(self):
        """Test cross-modal fused attention functionality"""
        query_dim, key_dim, embed_dim = 512, 512, 512
        num_heads = 8
        batch_size, query_len, key_len = 2, 32, 64
        
        cross_modal_attention = FusedCrossModalAttention(
            query_dim=query_dim,
            key_dim=key_dim,
            embed_dim=embed_dim,
            num_heads=num_heads,
            use_flash_attention=False
        )
        
        # Create different modality inputs
        query_input = torch.randn(batch_size, query_len, query_dim)
        key_input = torch.randn(batch_size, key_len, key_dim)
        value_input = torch.randn(batch_size, key_len, key_dim)
        
        output = cross_modal_attention(
            query=query_input,
            key=key_input,
            value=value_input
        )
        
        assert output.shape == (batch_size, query_len, embed_dim)
        
    def test_fused_expert_attention(self):
        """Test expert attention functionality"""
        hidden_size, num_experts = 512, 4
        batch_size, seq_len = 2, 32
        
        expert_attention = FusedExpertAttention(
            hidden_size=hidden_size,
            num_experts=num_experts,
            num_heads=8,
            capacity_factor=2.0,
            use_flash_attention=False
        )
        
        input_tensor = torch.randn(batch_size, seq_len, hidden_size)
        
        output = expert_attention(input_tensor)
        
        assert output.shape == input_tensor.shape
        assert output.dtype == input_tensor.dtype

def run_fixed_tests():
    """Run the fixed tests to validate performance optimizations."""
    test_suite = FixedFusedAttentionTests()
    
    tests = [
        "test_fused_multihead_attention_creation",
        "test_fused_attention_forward_pass", 
        "test_fused_cross_modal_attention",
        "test_fused_expert_attention"
    ]
    
    results = {}
    
    for test_name in tests:
        try:
            print(f"Running {test_name}...")
            test_method = getattr(test_suite, test_name)
            test_method()
            results[test_name] = "PASSED"
            print(f"✅ {test_name} PASSED")
        except Exception as e:
            results[test_name] = f"FAILED: {str(e)}"
            print(f"❌ {test_name} FAILED: {str(e)}")
            
    return results

if __name__ == "__main__":
    print("Running fixed performance optimization tests...")
    results = run_fixed_tests()
    
    passed = sum(1 for r in results.values() if r == "PASSED")
    total = len(results)
    
    print(f"\n=== Test Results ===")
    print(f"Passed: {passed}/{total}")
    
    for test_name, result in results.items():
        status = "✅" if result == "PASSED" else "❌"
        print(f"{status} {test_name}: {result}")
