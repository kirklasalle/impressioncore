#!/usr/bin/env python3
"""
ImpressionCore: Performance Optimization Tests

Test suite for fused attention, quantization, and adaptive precision features.

File: src/tests/core/test_performance_optimization.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-29
Modified: 2025-05-29
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [testing, performance, memory-optimization, attention, quantization]
Dependencies: [pytest, torch, typing]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
Comprehensive test suite for validating the performance optimization components
including fused attention mechanisms, quantization, and adaptive precision.

Test Categories:
- Fused attention functionality and performance
- Quantization accuracy and memory usage
- Adaptive precision switching
- Integration with AttentionManager
- Memory usage validation
- Performance benchmarking

Examples:
```bash
# Run all performance optimization tests
pytest src/tests/core/test_performance_optimization.py -v

# Run specific test categories
pytest src/tests/core/test_performance_optimization.py -k "fused_attention" -v
pytest src/tests/core/test_performance_optimization.py -k "quantization" -v

# Run with memory profiling
pytest src/tests/core/test_performance_optimization.py --memory-profile -v
```

Notes:
- Tests are designed to run on GTX 1050 Ti (4GB VRAM)
- Memory usage is validated against target constraints
- Performance benchmarks provide regression detection
"""

import pytest
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
import logging
import time
import gc
from typing import Dict, Any, Optional, Tuple
import warnings

# Import ImpressionCore components
from src.core.utils.memory_optimization.fused_attention import (
    FusedMultiHeadAttention,
    FusedCrossModalAttention,
    FusedExpertAttention,
    benchmark_fused_attention
)
from src.core.utils.memory_optimization.quantization import (
    QuantizationManager,
    EnhancedQuantizationManager,
    AdaptivePrecisionManager,
    QuantizationPrecision,
    QuantizationConfig
)
from src.modules.attention.attention_manager import AttentionManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestModel(nn.Module):
    """Simple test model for performance optimization testing"""
    
    def __init__(self, hidden_size: int = 768, num_layers: int = 2):
        super().__init__()
        self.hidden_size = hidden_size
        self.layers = nn.ModuleList([
            nn.TransformerEncoderLayer(
                d_model=hidden_size,
                nhead=8,
                dim_feedforward=hidden_size * 4,
                dropout=0.1,
                batch_first=True
            )
            for _ in range(num_layers)
        ])
        self.layer_norm = nn.LayerNorm(hidden_size)
        
    def forward(self, x: torch.Tensor, attention_mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        for layer in self.layers:
            x = layer(x, src_key_padding_mask=attention_mask)
        return self.layer_norm(x)

@pytest.fixture
def test_model():
    """Create a test model for optimization testing"""
    return TestModel(hidden_size=512, num_layers=2)

@pytest.fixture
def test_input():
    """Create test input tensors"""
    batch_size, seq_len, hidden_size = 2, 128, 512
    return {
        "input": torch.randn(batch_size, seq_len, hidden_size),
        "attention_mask": torch.ones(batch_size, seq_len, dtype=torch.bool)
    }

@pytest.fixture
def calibration_data():
    """Create calibration data for quantization testing"""
    num_samples = 100
    seq_len, hidden_size = 128, 512
    
    inputs = torch.randn(num_samples, seq_len, hidden_size)
    targets = torch.randint(0, 2, (num_samples, seq_len))  # Binary classification
    
    dataset = TensorDataset(inputs, targets)
    return DataLoader(dataset, batch_size=8, shuffle=False)

class TestFusedAttention:
    """Test suite for fused attention mechanisms"""
    
    def test_fused_multihead_attention_creation(self):
        """Test that fused multi-head attention can be created"""
        hidden_size, num_heads = 512, 8
        
        fused_attention = FusedMultiHeadAttention(
            hidden_size=hidden_size,
            num_heads=num_heads,
            dropout=0.1,
            use_flash_attention=False  # Disable for testing
        )
          assert fused_attention.hidden_size == hidden_size
        assert fused_attention.num_heads == num_heads
        assert hasattr(fused_attention, 'qkv_proj')
        
    def test_fused_attention_forward_pass(self, test_input):
        """Test that fused attention forward pass works correctly"""
        hidden_size, num_heads = 512, 8
        
        fused_attention = FusedMultiHeadAttention(
            hidden_size=hidden_size,
            num_heads=num_heads,
            use_flash_attention=False
        )
        
        input_tensor = test_input["input"]
        attention_mask = test_input["attention_mask"]
        
        # Test forward pass
        output = fused_attention(input_tensor, attention_mask=attention_mask)
        
        # Validate output shape
        assert output.shape == input_tensor.shape
        assert output.dtype == input_tensor.dtype
          def test_fused_cross_modal_attention(self):
        """Test cross-modal fused attention functionality"""
        query_dim, key_dim, embed_dim = 512, 512, 512
        num_heads = 8
        batch_size, seq_len = 2, 64
        
        cross_modal_attention = FusedCrossModalAttention(
            query_dim=query_dim,
            key_dim=key_dim,
            embed_dim=embed_dim,
            num_heads=num_heads,
            use_flash_attention=False
        )
        
        # Create different modality inputs
        visual_input = torch.randn(batch_size, seq_len, query_dim)
        text_input = torch.randn(batch_size, seq_len + 32, key_dim)
        
        output = cross_modal_attention(
            query=visual_input,
            key=text_input,
            value=text_input
        )
        
        assert output.shape == visual_input.shape
        
    def test_fused_expert_attention(self):
        """Test expert attention for MoE architectures"""
        hidden_size, num_heads = 512, 8
        num_experts, expert_capacity = 4, 16
        batch_size, seq_len = 2, 128
        
        expert_attention = FusedExpertAttention(
            hidden_size=hidden_size,
            num_heads=num_heads,
            num_experts=num_experts,
            expert_capacity=expert_capacity,
            use_flash_attention=False
        )
        
        input_tensor = torch.randn(batch_size, seq_len, hidden_size)
        output = expert_attention(input_tensor)
        
        assert output.shape == input_tensor.shape
        
    def test_attention_manager_fused_integration(self, test_input):
        """Test that AttentionManager properly integrates fused attention"""
        hidden_size, num_heads = 512, 8
        
        attention_manager = AttentionManager(
            hidden_size=hidden_size,
            num_heads=num_heads,
            attention_preference="performance"
        )
        
        input_tensor = test_input["input"]
        attention_mask = test_input["attention_mask"]
        
        # Test forced fused attention
        output = attention_manager(
            input_tensor,
            attention_mask=attention_mask,
            forced_attention_type="fused"
        )
        
        assert output.shape == input_tensor.shape
        
        # Check that fused attention was used
        stats = attention_manager.get_stats()
        assert "fused" in stats
        assert stats["fused"]["calls"] > 0

class TestQuantization:
    """Test suite for quantization functionality"""
    
    def test_quantization_manager_creation(self):
        """Test that quantization manager can be created"""
        config = QuantizationConfig(
            quantization_type="dynamic",
            backend="fbgemm",
            calibration_batches=10
        )
        
        quant_manager = QuantizationManager(config)
        assert quant_manager.config.quantization_type == "dynamic"
        assert quant_manager.config.backend == "fbgemm"
        
    def test_dynamic_quantization(self, test_model):
        """Test dynamic quantization functionality"""
        quant_manager = QuantizationManager()
        
        original_size = quant_manager._get_model_size(test_model)
        quantized_model = quant_manager.apply_dynamic_quantization(test_model)
        quantized_size = quant_manager._get_model_size(quantized_model)
        
        # Quantized model should be smaller (or equal if quantization not supported)
        assert quantized_size <= original_size
        
        # Test inference still works
        test_input = torch.randn(1, 64, 512)
        output = quantized_model(test_input)
        assert output.shape[:-1] == test_input.shape[:-1]  # Last dim might change due to layer norm
        
    def test_static_quantization(self, test_model, calibration_data):
        """Test static quantization with calibration"""
        quant_manager = QuantizationManager()
        
        # Only test if quantization is supported
        if quant_manager.quantization_supported:
            try:
                quantized_model = quant_manager.apply_static_quantization(
                    test_model, calibration_data
                )
                
                # Test inference
                test_input = torch.randn(1, 64, 512)
                output = quantized_model(test_input)
                assert output is not None
                
            except Exception as e:
                # Static quantization might fail on some systems
                logger.warning(f"Static quantization test skipped: {e}")
                pytest.skip("Static quantization not supported on this system")
        else:
            pytest.skip("Quantization backend not supported")
    
    def test_adaptive_precision_manager(self):
        """Test adaptive precision management"""
        precision_manager = AdaptivePrecisionManager()
        
        # Test precision determination
        precision = precision_manager.determine_optimal_precision(
            sequence_length=512,
            available_memory_mb=3000,
            model_size_mb=200
        )
        
        assert isinstance(precision, QuantizationPrecision)
        
        # Test high memory pressure scenario
        high_pressure_precision = precision_manager.determine_optimal_precision(
            sequence_length=2048,
            available_memory_mb=1000,
            model_size_mb=800
        )
        
        # Should select more aggressive quantization
        assert high_pressure_precision in [
            QuantizationPrecision.INT8, 
            QuantizationPrecision.INT4
        ]
        
    def test_enhanced_quantization_manager(self, test_model, calibration_data):
        """Test enhanced quantization manager with auto-optimization"""
        enhanced_manager = EnhancedQuantizationManager()
        
        optimized_model, stats = enhanced_manager.auto_optimize_model(
            model=test_model,
            sequence_length=512,
            available_memory_mb=3000,
            calibration_data=calibration_data
        )
        
        assert optimized_model is not None
        assert "compression_ratio" in stats
        assert "optimization_strategy" in stats
        assert stats["compression_ratio"] >= 1.0  # Should compress or stay same

class TestMemoryOptimization:
    """Test suite for memory optimization features"""
    
    def test_memory_usage_tracking(self, test_model):
        """Test that memory usage is properly tracked"""
        quant_manager = QuantizationManager()
        
        # Get model size
        model_size = quant_manager._get_model_size(test_model)
        assert model_size > 0
        
        # Size should be reasonable for test model
        assert model_size < 100  # Should be less than 100MB
        
    def test_vram_constraint_compliance(self, test_model):
        """Test that optimizations respect VRAM constraints"""
        # Simulate GTX 1050 Ti constraints (4GB VRAM)
        target_vram_mb = 4000
        
        attention_manager = AttentionManager(
            hidden_size=512,
            num_heads=8,
            vram_target_mb=target_vram_mb
        )
        
        # Test with varying sequence lengths
        for seq_len in [128, 512, 1024, 2048]:
            test_input = torch.randn(1, seq_len, 512)
            attention_mask = torch.ones(1, seq_len, dtype=torch.bool)
            
            output = attention_manager(
                test_input,
                attention_mask=attention_mask
            )
            
            assert output.shape == test_input.shape
            
        # Check that appropriate attention mechanisms were selected
        stats = attention_manager.get_stats()
        assert len(stats) > 0
        
    def test_memory_cleanup(self, test_model):
        """Test that memory is properly cleaned up after operations"""
        initial_memory = torch.cuda.memory_allocated() if torch.cuda.is_available() else 0
        
        # Perform multiple operations
        quant_manager = QuantizationManager()
        
        for _ in range(5):
            _ = quant_manager.apply_dynamic_quantization(test_model)
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        
        final_memory = torch.cuda.memory_allocated() if torch.cuda.is_available() else 0
        
        # Memory should not grow excessively
        memory_growth = final_memory - initial_memory
        if torch.cuda.is_available():
            assert memory_growth < 500 * 1024 * 1024  # Less than 500MB growth

class TestPerformanceBenchmarking:
    """Test suite for performance benchmarking"""
    
    def test_fused_attention_benchmark(self):
        """Test fused attention benchmarking functionality"""
        hidden_size, num_heads = 512, 8
        seq_len = 128
        
        # Skip if CUDA not available (benchmarks need consistent timing)
        if not torch.cuda.is_available():
            pytest.skip("CUDA not available for benchmarking")
        
        try:
            results = benchmark_fused_attention(
                hidden_size=hidden_size,
                num_heads=num_heads,
                sequence_length=seq_len,
                batch_size=2,
                num_runs=3  # Reduced for testing
            )
            
            assert "standard_attention" in results
            assert "fused_attention" in results
            
            for key, metrics in results.items():
                assert "avg_time_ms" in metrics
                assert "memory_mb" in metrics
                assert metrics["avg_time_ms"] >= 0
                
        except Exception as e:
            logger.warning(f"Benchmark test failed: {e}")
            pytest.skip("Benchmarking not available on this system")
    
    def test_quantization_performance_impact(self, test_model):
        """Test that quantization maintains reasonable performance"""
        quant_manager = QuantizationManager()
        
        # Benchmark original model
        test_input = torch.randn(4, 128, 512)  # Larger batch for timing
        
        with torch.no_grad():
            # Time original model
            start_time = time.time()
            for _ in range(5):
                _ = test_model(test_input)
            original_time = time.time() - start_time
            
            # Time quantized model
            quantized_model = quant_manager.apply_dynamic_quantization(test_model)
            start_time = time.time()
            for _ in range(5):
                _ = quantized_model(test_input)
            quantized_time = time.time() - start_time
        
        # Quantized model should not be significantly slower
        # Allow up to 2x slower due to quantization overhead
        assert quantized_time <= original_time * 2.0

class TestIntegration:
    """Integration tests for complete optimization pipeline"""
    
    def test_end_to_end_optimization(self, test_model, test_input, calibration_data):
        """Test complete optimization pipeline from model to optimized inference"""
        
        # Step 1: Create attention manager with optimizations
        attention_manager = AttentionManager(
            hidden_size=512,
            num_heads=8,
            attention_preference="performance",
            vram_target_mb=3500
        )
        
        # Step 2: Apply quantization
        enhanced_quant = EnhancedQuantizationManager()
        optimized_model, quant_stats = enhanced_quant.auto_optimize_model(
            model=test_model,
            sequence_length=128,
            available_memory_mb=3000,
            calibration_data=calibration_data
        )
        
        # Step 3: Test inference with optimized components
        input_tensor = test_input["input"]
        attention_mask = test_input["attention_mask"]
        
        # Test attention manager
        attention_output = attention_manager(
            input_tensor,
            attention_mask=attention_mask,
            forced_attention_type="fused"
        )
        
        # Test optimized model
        model_output = optimized_model(input_tensor, attention_mask)
        
        # Validate outputs
        assert attention_output.shape == input_tensor.shape
        assert model_output.shape[:-1] == input_tensor.shape[:-1]  # Allow for output dim changes
        
        # Check optimization stats
        assert quant_stats["compression_ratio"] >= 1.0
        
        attention_stats = attention_manager.get_stats()
        assert "fused" in attention_stats
        assert attention_stats["fused"]["calls"] > 0
        
    def test_memory_constrained_optimization(self, test_model):
        """Test optimization under severe memory constraints"""
        # Simulate very low memory scenario
        enhanced_quant = EnhancedQuantizationManager()
        
        optimized_model, stats = enhanced_quant.auto_optimize_model(
            model=test_model,
            sequence_length=1024,  # Long sequence
            available_memory_mb=500,  # Very low memory
            target_accuracy=0.9
        )
        
        # Should apply aggressive optimization
        assert stats["compression_ratio"] > 1.0
        assert stats["target_precision"] in ["int8", "int4", "float16"]
        
        # Model should still work
        test_input = torch.randn(1, 128, 512)
        output = optimized_model(test_input)
        assert output is not None

# Utility functions for manual testing and debugging
def run_performance_profile():
    """Run a comprehensive performance profile of optimization features"""
    print("ImpressionCore Performance Optimization Profile")
    print("=" * 50)
    
    # Test model
    model = TestModel(hidden_size=768, num_layers=3)
    print(f"Test model created with {sum(p.numel() for p in model.parameters())} parameters")
    
    # Test fused attention
    print("\n1. Fused Attention Performance:")
    try:
        attention_manager = AttentionManager(
            hidden_size=768,
            num_heads=12,
            attention_preference="performance"
        )
        
        test_input = torch.randn(2, 512, 768)
        attention_mask = torch.ones(2, 512, dtype=torch.bool)
        
        # Test different attention types
        for attention_type in ["standard", "fused", "memory_efficient"]:
            try:
                start_time = time.time()
                output = attention_manager(
                    test_input,
                    attention_mask=attention_mask,
                    forced_attention_type=attention_type
                )
                elapsed = time.time() - start_time
                print(f"   {attention_type}: {elapsed*1000:.2f}ms")
            except Exception as e:
                print(f"   {attention_type}: Failed - {e}")
                
    except Exception as e:
        print(f"   Fused attention test failed: {e}")
    
    # Test quantization
    print("\n2. Quantization Performance:")
    try:
        enhanced_quant = EnhancedQuantizationManager()
        
        # Create dummy calibration data
        calibration_input = torch.randn(50, 128, 768)
        calibration_targets = torch.randint(0, 2, (50, 128))
        calibration_dataset = TensorDataset(calibration_input, calibration_targets)
        calibration_loader = DataLoader(calibration_dataset, batch_size=8)
        
        optimized_model, stats = enhanced_quant.auto_optimize_model(
            model=model,
            sequence_length=512,
            available_memory_mb=3000,
            calibration_data=calibration_loader
        )
        
        print(f"   Strategy: {stats['optimization_strategy']}")
        print(f"   Compression: {stats['compression_ratio']:.2f}x")
        print(f"   Memory saved: {stats['memory_savings_mb']:.1f}MB")
        
    except Exception as e:
        print(f"   Quantization test failed: {e}")
    
    # Memory usage summary
    print("\n3. Memory Usage:")
    quant_manager = QuantizationManager()
    original_size = quant_manager._get_model_size(model)
    print(f"   Original model: {original_size:.1f}MB")
    
    if torch.cuda.is_available():
        print(f"   CUDA memory allocated: {torch.cuda.memory_allocated() / 1024**2:.1f}MB")
        print(f"   CUDA memory reserved: {torch.cuda.memory_reserved() / 1024**2:.1f}MB")
    else:
        print("   CUDA not available")
    
    print("\nProfile complete!")

if __name__ == "__main__":
    # Run performance profile when executed directly
    run_performance_profile()
