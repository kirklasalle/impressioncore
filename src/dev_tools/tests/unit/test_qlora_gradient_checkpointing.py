#!/usr/bin/env python3
"""
ImpressionCore: QLoRA Gradient Checkpointing Tests

Comprehensive test suite for QLoRA gradient checkpointing functionality.

File: tests/unit/test_qlora_gradient_checkpointing.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-06-01
Modified: 2025-06-01
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [testing, qlora, gradient-checkpointing, memory-optimization, 2025]
Dependencies: [torch, pytest]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
Comprehensive test suite for QLoRA gradient checkpointing functionality,
including selective checkpointing, mixed-precision handling, and memory optimization.
"""

import pytest
import torch
import torch.nn as nn
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.core.utils.gradient_checkpointing import (
    QLoRAGradientCheckpointing,
    CheckpointConfig,
    apply_gradient_checkpointing,
    apply_qlora_checkpointing,
    memory_efficient_checkpointing
)


class MockQuantizedLinear(nn.Module):
    """Mock quantized linear layer for testing."""
    
    def __init__(self, in_features: int, out_features: int):
        super().__init__()
        self.weight = nn.Parameter(torch.randn(out_features, in_features))
        self.weight.quant_type = "4bit"  # Mock quantization attribute
        self.in_features = in_features
        self.out_features = out_features
    
    def forward(self, x):
        return torch.matmul(x, self.weight.t())


class MockLoRALayer(nn.Module):
    """Mock LoRA layer for testing."""
    
    def __init__(self, in_features: int, out_features: int, rank: int = 8):
        super().__init__()
        self.base_layer = nn.Linear(in_features, out_features)
        self.lora_A = nn.Parameter(torch.randn(rank, in_features))
        self.lora_B = nn.Parameter(torch.randn(out_features, rank))
        self.lora_dropout = nn.Dropout(0.1)
        self.scaling = 1.0
    
    def forward(self, x):
        base_output = self.base_layer(x)
        lora_output = torch.matmul(torch.matmul(x, self.lora_A.t()), self.lora_B.t())
        return base_output + self.scaling * lora_output


class MockTransformerBlock(nn.Module):
    """Mock transformer block with various layer types."""
    
    def __init__(self, hidden_size: int = 768):
        super().__init__()
        # Use custom attention to handle mixed precision better
        self.self_attn = nn.Linear(hidden_size, hidden_size * 3)  # Combined QKV projection
        self.q_proj = MockQuantizedLinear(hidden_size, hidden_size)
        self.k_proj = MockQuantizedLinear(hidden_size, hidden_size)
        self.v_proj = MockQuantizedLinear(hidden_size, hidden_size)
        self.o_proj = MockLoRALayer(hidden_size, hidden_size)
        self.ffn = nn.Sequential(
            MockQuantizedLinear(hidden_size, hidden_size * 4),
            nn.ReLU(),
            MockLoRALayer(hidden_size * 4, hidden_size)
        )
        self.norm1 = nn.LayerNorm(hidden_size)
        self.norm2 = nn.LayerNorm(hidden_size)
    
    def forward(self, x):
        # Simple self-attention mechanism
        residual = x
        qkv = self.self_attn(x)
        q, k, v = qkv.chunk(3, dim=-1)
        
        # Scaled dot-product attention
        attn_weights = torch.matmul(q, k.transpose(-2, -1)) / (x.size(-1) ** 0.5)
        attn_weights = torch.softmax(attn_weights, dim=-1)
        attn_output = torch.matmul(attn_weights, v)
        
        x = self.norm1(residual + attn_output)
        
        # FFN block
        residual = x
        ffn_output = self.ffn(x)
        x = self.norm2(residual + ffn_output)
        
        return x


class TestCheckpointConfig:
    """Test CheckpointConfig dataclass."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = CheckpointConfig()
        
        assert config.enable_basic_checkpointing is True
        assert config.enable_qlora_optimizations is True
        assert config.selective_checkpointing is True
        assert config.quantized_layer_priority is True
        assert config.preserve_quantized_weights is True
        assert config.cpu_offload_during_checkpoint is False
        assert config.checkpoint_every_n_layers == 2
        assert config.mixed_precision_checkpointing is True
        assert config.dynamic_checkpoint_selection is True
        assert config.memory_threshold_mb == 3500.0
        assert config.checkpoint_activation_size_threshold_mb == 100.0
    
    def test_custom_config(self):
        """Test custom configuration creation."""
        config = CheckpointConfig(
            memory_threshold_mb=2000.0,
            checkpoint_every_n_layers=1,
            selective_checkpointing=False
        )
        
        assert config.memory_threshold_mb == 2000.0
        assert config.checkpoint_every_n_layers == 1
        assert config.selective_checkpointing is False
        # Other values should remain default
        assert config.enable_basic_checkpointing is True


class TestQLoRAGradientCheckpointing:
    """Test QLoRAGradientCheckpointing class."""
    
    @pytest.fixture
    def mock_model(self):
        """Create a mock model with various layer types."""
        model = nn.Sequential(
            MockTransformerBlock(768),
            MockTransformerBlock(768),
        )
        return model
    
    @pytest.fixture
    def checkpoint_manager(self, mock_model):
        """Create QLoRAGradientCheckpointing instance."""
        return QLoRAGradientCheckpointing(
            model=mock_model,
            quantized_layers=['q_proj', 'k_proj', 'v_proj'],
            lora_modules=['lora_A', 'lora_B', 'o_proj']
        )
    
    def test_initialization(self, mock_model):
        """Test QLoRAGradientCheckpointing initialization."""
        manager = QLoRAGradientCheckpointing(mock_model)
        
        assert manager.model is mock_model
        assert isinstance(manager.config, CheckpointConfig)
        assert isinstance(manager.checkpoint_stats, dict)
        assert "total_checkpoints" in manager.checkpoint_stats
        assert len(manager.checkpoint_candidates) > 0
    
    def test_model_structure_analysis(self, checkpoint_manager):
        """Test model structure analysis."""
        # Check that candidates were identified
        assert len(checkpoint_manager.checkpoint_candidates) > 0
        assert len(checkpoint_manager.quantized_candidates) > 0
        assert len(checkpoint_manager.lora_candidates) > 0
    
    def test_is_checkpoint_candidate(self, checkpoint_manager):
        """Test checkpoint candidate identification."""
        # Test with different module types
        linear_module = nn.Linear(768, 768)
        attention_module = nn.MultiheadAttention(768, 12)
        
        assert checkpoint_manager._is_checkpoint_candidate(linear_module, "test_linear")
        assert checkpoint_manager._is_checkpoint_candidate(attention_module, "test_attention")
        
        # Test with name-based detection
        assert checkpoint_manager._is_checkpoint_candidate(linear_module, "some_attention_layer")
        assert checkpoint_manager._is_checkpoint_candidate(linear_module, "ffn_layer")
    
    def test_is_quantized_layer(self, checkpoint_manager):
        """Test quantized layer identification."""
        quantized_module = MockQuantizedLinear(768, 768)
        regular_module = nn.Linear(768, 768)
        
        assert checkpoint_manager._is_quantized_layer(quantized_module, "q_proj")
        assert not checkpoint_manager._is_quantized_layer(regular_module, "regular_layer")
        
        # Test name-based detection
        assert checkpoint_manager._is_quantized_layer(regular_module, "q_proj")
    
    def test_is_lora_layer(self, checkpoint_manager):
        """Test LoRA layer identification."""
        lora_module = MockLoRALayer(768, 768)
        regular_module = nn.Linear(768, 768)
        
        assert checkpoint_manager._is_lora_layer(lora_module, "test_layer")
        assert not checkpoint_manager._is_lora_layer(regular_module, "regular_layer")
        
        # Test name-based detection
        assert checkpoint_manager._is_lora_layer(regular_module, "lora_A")
    
    def test_estimate_activation_memory(self, checkpoint_manager):
        """Test activation memory estimation."""
        module = nn.Linear(768, 768)
        input_shape = (32, 512, 768)  # batch_size, seq_len, hidden_size
        
        memory_estimate = checkpoint_manager._estimate_activation_memory(module, input_shape)
        assert isinstance(memory_estimate, float)
        assert memory_estimate > 0
    
    def test_should_checkpoint_module(self, checkpoint_manager):
        """Test module checkpointing decision logic."""
        quantized_module = MockQuantizedLinear(768, 768)
        regular_module = nn.Linear(768, 768)
        
        # Quantized modules should always be checkpointed if memory pressure exists
        with patch('torch.cuda.is_available', return_value=True), \
             patch('torch.cuda.memory_allocated', return_value=2000 * 1024 * 1024):  # 2GB - above threshold
            assert checkpoint_manager._should_checkpoint_module(quantized_module, "q_proj")
        
        # Regular modules depend on memory conditions
        with patch('torch.cuda.is_available', return_value=False):
            # Without CUDA, decision is based on activation size
            result = checkpoint_manager._should_checkpoint_module(regular_module, "large_layer")
            assert isinstance(result, bool)
    
    def test_selective_checkpointing_context(self, checkpoint_manager):
        """Test selective checkpointing context manager."""
        with checkpoint_manager.selective_checkpointing():
            # Context should be active
            pass
        
        # Verify statistics were updated
        # Note: In this test, no actual forward passes occur, so stats may be 0
        assert "total_checkpoints" in checkpoint_manager.checkpoint_stats
    
    def test_optimize_checkpoint_strategy(self, checkpoint_manager):
        """Test dynamic checkpoint strategy optimization."""
        # Test with dynamic optimization enabled
        checkpoint_manager.config.dynamic_checkpoint_selection = True
        
        with patch('torch.cuda.is_available', return_value=True), \
             patch('torch.cuda.memory_allocated', return_value=3000 * 1024 * 1024):  # 3GB
            
            result = checkpoint_manager.optimize_checkpoint_strategy()
            assert "strategy" in result
            assert "changes" in result
            assert result["strategy"] == "dynamic"
    
    def test_get_checkpoint_report(self, checkpoint_manager):
        """Test checkpoint report generation."""
        report = checkpoint_manager.get_checkpoint_report()
        
        assert "checkpoint_stats" in report
        assert "configuration" in report
        assert "model_analysis" in report
        assert "memory_efficiency" in report
        
        # Verify specific fields
        assert "total_checkpoints" in report["checkpoint_stats"]
        assert "selective_checkpointing" in report["configuration"]
        assert "total_checkpoint_candidates" in report["model_analysis"]


class TestUtilityFunctions:
    """Test utility functions."""
    
    def test_apply_gradient_checkpointing(self):
        """Test basic gradient checkpointing application."""
        model = nn.Sequential(
            nn.Linear(768, 768),
            nn.ReLU(),
            nn.Linear(768, 768)
        )
        
        # Add gradient_checkpointing attribute to one module
        model[0].gradient_checkpointing = False
        
        result_model = apply_gradient_checkpointing(model)
        
        assert result_model is model  # Should return same model
        assert model[0].gradient_checkpointing is True
    
    def test_apply_qlora_checkpointing(self):
        """Test QLoRA checkpointing application."""
        model = MockTransformerBlock(768)
        
        checkpoint_manager = apply_qlora_checkpointing(model)
        
        assert isinstance(checkpoint_manager, QLoRAGradientCheckpointing)
        assert checkpoint_manager.model is model
    
    def test_memory_efficient_checkpointing_context(self):
        """Test memory-efficient checkpointing context manager."""
        model = MockTransformerBlock(768)
        
        with memory_efficient_checkpointing(model, memory_threshold_mb=2000.0) as manager:
            assert isinstance(manager, QLoRAGradientCheckpointing)
            assert manager.config.memory_threshold_mb == 2000.0


class TestIntegration:
    """Integration tests for gradient checkpointing."""
    
    def test_full_forward_pass_with_checkpointing(self):
        """Test full forward pass with checkpointing enabled."""
        model = MockTransformerBlock(768)
        input_tensor = torch.randn(2, 10, 768)  # batch_size=2, seq_len=10, hidden_size=768
        
        checkpoint_manager = QLoRAGradientCheckpointing(model)
        
        with checkpoint_manager.selective_checkpointing():
            output = model(input_tensor)
        
        assert output.shape == input_tensor.shape
        assert not torch.isnan(output).any()
    
    def test_memory_efficiency_simulation(self):
        """Test memory efficiency under simulated conditions."""
        model = MockTransformerBlock(768)
        checkpoint_manager = QLoRAGradientCheckpointing(model)
        
        # Simulate high memory pressure
        with patch('torch.cuda.is_available', return_value=True), \
             patch('torch.cuda.memory_allocated', return_value=3200 * 1024 * 1024):  # 3.2GB
            
            with checkpoint_manager.selective_checkpointing():
                # Should apply more aggressive checkpointing
                pass
          # Verify that checkpointing was considered
        report = checkpoint_manager.get_checkpoint_report()
        assert "memory_efficiency" in report
    
    def test_mixed_precision_handling(self):
        """Test mixed precision checkpointing."""
        model = MockTransformerBlock(768)
        config = CheckpointConfig(mixed_precision_checkpointing=True)
        checkpoint_manager = QLoRAGradientCheckpointing(model, config=config)
        
        # Test with different input precisions
        input_fp32 = torch.randn(2, 10, 768, dtype=torch.float32)
        
        with checkpoint_manager.selective_checkpointing():
            output_fp32 = model(input_fp32)
            
            # For fp16 test, convert model to fp16 first to avoid dtype mismatch
            model_fp16 = model.half()
            input_fp16 = torch.randn(2, 10, 768, dtype=torch.float16)
            output_fp16 = model_fp16(input_fp16)
        
        assert output_fp32.dtype == torch.float32
        assert output_fp16.dtype == torch.float16


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_empty_model(self):
        """Test handling of empty or minimal models."""
        model = nn.Sequential()  # Empty model
        
        checkpoint_manager = QLoRAGradientCheckpointing(model)
        
        # Should not crash
        assert len(checkpoint_manager.checkpoint_candidates) == 0
        
        with checkpoint_manager.selective_checkpointing():
            pass  # Should work without errors
    
    def test_invalid_configuration(self):
        """Test handling of invalid configurations."""
        model = MockTransformerBlock(768)
        
        # Test with extreme values
        config = CheckpointConfig(
            memory_threshold_mb=-1000.0,  # Negative value
            checkpoint_every_n_layers=0   # Zero value
        )
        
        # Should not crash during initialization
        checkpoint_manager = QLoRAGradientCheckpointing(model, config=config)
        assert checkpoint_manager.config.memory_threshold_mb == -1000.0
    
    def test_cuda_not_available(self):
        """Test behavior when CUDA is not available."""
        model = MockTransformerBlock(768)
        checkpoint_manager = QLoRAGradientCheckpointing(model)
        
        with patch('torch.cuda.is_available', return_value=False):
            with checkpoint_manager.selective_checkpointing():
                pass  # Should work without CUDA
            
            # Strategy optimization should still work
            result = checkpoint_manager.optimize_checkpoint_strategy()
            assert result["strategy"] == "dynamic"


if __name__ == "__main__":
    # Run basic tests if executed directly
    pytest.main([__file__, "-v"])
