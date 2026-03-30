#!/usr/bin/env python3
"""
Test suite for QLoRA Model Implementation

Tests the QLoRA (Quantized Low-Rank Adaptation) model functionality
including quantization, LoRA adaptation, and memory efficiency.
"""

import pytest
import torch
import torch.nn as nn
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from models.lora.qlora_model import QLoRAModel, QLoRALinear, apply_qlora, estimate_qlora_memory_savings
from models.lora.config import EnhancedLoRAConfig


class SimpleTransformer(nn.Module):
    """Simple transformer model for testing."""
    
    def __init__(self, hidden_size=768, num_layers=2):
        super().__init__()
        self.hidden_size = hidden_size
        
        # Create transformer layers with attention projections
        self.layers = nn.ModuleList()
        for _ in range(num_layers):
            layer = nn.ModuleDict({
                'attention': nn.ModuleDict({
                    'q_proj': nn.Linear(hidden_size, hidden_size),
                    'k_proj': nn.Linear(hidden_size, hidden_size),
                    'v_proj': nn.Linear(hidden_size, hidden_size),
                    'o_proj': nn.Linear(hidden_size, hidden_size),
                }),
                'mlp': nn.ModuleDict({
                    'gate_proj': nn.Linear(hidden_size, hidden_size * 4),
                    'up_proj': nn.Linear(hidden_size, hidden_size * 4),
                    'down_proj': nn.Linear(hidden_size * 4, hidden_size),
                })
            })
            self.layers.append(layer)
    
    def forward(self, x):
        for layer in self.layers:
            # Simple forward pass (not a real transformer)
            q = layer['attention']['q_proj'](x)
            k = layer['attention']['k_proj'](x)
            v = layer['attention']['v_proj'](x)
            attn_out = layer['attention']['o_proj'](q + k + v)
            
            mlp_gate = layer['mlp']['gate_proj'](attn_out)
            mlp_up = layer['mlp']['up_proj'](attn_out)
            mlp_out = layer['mlp']['down_proj'](mlp_gate * mlp_up)
            
            x = attn_out + mlp_out
        
        return x


class TestQLoRALinear:
    """Test the QLoRALinear layer implementation."""
    
    def test_qlora_linear_initialization(self):
        """Test QLoRA linear layer initialization."""
        base_layer = nn.Linear(768, 768)
        
        qlora_layer = QLoRALinear(
            base_layer=base_layer,
            rank=8,
            alpha=16.0,
            quantization_bits=4,
            quantization_scheme="nf4"
        )
        
        assert qlora_layer.rank == 8
        assert qlora_layer.alpha == 16.0
        assert qlora_layer.quantization_bits == 4
        assert qlora_layer.quantization_scheme == "nf4"
        assert hasattr(qlora_layer, 'quantized_weight')
        
        # Check that base weights are frozen
        assert not qlora_layer.base_layer.weight.requires_grad
    
    def test_qlora_linear_forward(self):
        """Test QLoRA linear layer forward pass."""
        base_layer = nn.Linear(768, 768)
        qlora_layer = QLoRALinear(base_layer, rank=8, alpha=16.0)
        
        # Test forward pass
        x = torch.randn(10, 768)
        output = qlora_layer(x)
        
        assert output.shape == (10, 768)
        assert not torch.isnan(output).any()
        assert not torch.isinf(output).any()
    
    def test_qlora_linear_memory_stats(self):
        """Test memory statistics calculation."""
        base_layer = nn.Linear(768, 768)
        qlora_layer = QLoRALinear(base_layer, rank=8, quantization_bits=4)
        
        stats = qlora_layer.get_memory_stats()
        
        # Check required fields
        required_fields = ["original_mb", "quantized_mb", "lora_mb", "total_mb", "memory_saved_mb", "compression_ratio"]
        for field in required_fields:
            assert field in stats
            assert isinstance(stats[field], (int, float))
        
        # Memory savings should be positive
        assert stats["memory_saved_mb"] > 0
        assert stats["compression_ratio"] > 1.0
    
    def test_quantization_schemes(self):
        """Test different quantization schemes."""
        base_layer = nn.Linear(768, 768)
        
        schemes = ["nf4", "fp4"]
        for scheme in schemes:
            qlora_layer = QLoRALinear(
                base_layer, 
                rank=8, 
                quantization_bits=4, 
                quantization_scheme=scheme
            )
            
            assert qlora_layer.quantization_scheme == scheme
            
            # Test forward pass works
            x = torch.randn(5, 768)
            output = qlora_layer(x)
            assert output.shape == (5, 768)


class TestQLoRAModel:
    """Test the QLoRAModel implementation."""
    
    @pytest.fixture
    def simple_model(self):
        """Create a simple model for testing."""
        return SimpleTransformer(hidden_size=512, num_layers=2)
    
    @pytest.fixture
    def qlora_config(self):
        """Create QLoRA configuration for testing."""
        return EnhancedLoRAConfig(
            rank=8,
            alpha=16.0,
            dropout_p=0.1,
            quantization_bits=4,
            quantization_scheme="nf4",
            target_modules=["q_proj", "k_proj", "v_proj", "o_proj"]
        )
    
    def test_qlora_model_initialization(self, simple_model, qlora_config):
        """Test QLoRA model initialization."""
        qlora_model = QLoRAModel(simple_model, qlora_config)
        
        assert qlora_model.config == qlora_config
        assert qlora_model.base_model == simple_model
        assert hasattr(qlora_model, 'stats')
        
        # Check that some modules were replaced
        assert qlora_model.stats.lora_params > 0
        assert qlora_model.stats.quantized_params > 0
    
    def test_qlora_model_forward(self, simple_model, qlora_config):
        """Test QLoRA model forward pass."""
        qlora_model = QLoRAModel(simple_model, qlora_config)
        
        # Test forward pass
        x = torch.randn(5, 512)
        output = qlora_model(x)
        
        assert output.shape == (5, 512)
        assert not torch.isnan(output).any()
        assert not torch.isinf(output).any()
    
    def test_qlora_model_memory_stats(self, simple_model, qlora_config):
        """Test QLoRA model memory statistics."""
        qlora_model = QLoRAModel(simple_model, qlora_config)
        
        stats = qlora_model.get_memory_stats()
        
        # Check required top-level keys
        assert "layer_statistics" in stats
        assert "total_statistics" in stats
        assert "model_statistics" in stats
        
        # Check that we have layer statistics
        assert len(stats["layer_statistics"]) > 0
        
        # Check model statistics
        model_stats = stats["model_statistics"]
        assert model_stats["total_parameters"] > 0
        assert model_stats["lora_parameters"] > 0
        assert model_stats["compression_ratio"] > 1.0
    
    def test_qlora_merge_and_unload(self, simple_model, qlora_config):
        """Test merging LoRA weights and unloading."""
        qlora_model = QLoRAModel(simple_model, qlora_config)
        
        # Test merge and unload
        merged_model = qlora_model.merge_and_unload()
        
        assert merged_model is not None
        assert isinstance(merged_model, nn.Module)
        
        # Test that merged model works
        x = torch.randn(5, 512)
        output = merged_model(x)
        assert output.shape == (5, 512)
    
    def test_target_module_selection(self, simple_model):
        """Test that only target modules are adapted."""
        # Only target attention modules
        config = EnhancedLoRAConfig(
            rank=8,
            target_modules=["q_proj", "k_proj"]
        )
        
        qlora_model = QLoRAModel(simple_model, config, target_modules=["q_proj", "k_proj"])
        
        # Count QLoRA layers
        qlora_count = 0
        total_linear_count = 0
        
        for name, module in qlora_model.base_model.named_modules():
            if isinstance(module, QLoRALinear):
                qlora_count += 1
                assert any(target in name for target in ["q_proj", "k_proj"])
            elif isinstance(module, nn.Linear):
                total_linear_count += 1
        
        # Should have QLoRA layers but not for all linear layers
        assert qlora_count > 0
        assert qlora_count < total_linear_count + qlora_count


class TestQLoRAUtilities:
    """Test QLoRA utility functions."""
    
    def test_apply_qlora_function(self):
        """Test the apply_qlora utility function."""
        model = SimpleTransformer(hidden_size=256, num_layers=1)
        
        # Test with default configuration
        qlora_model = apply_qlora(model)
        
        assert isinstance(qlora_model, QLoRAModel)
        assert qlora_model.stats.lora_params > 0
    
    def test_apply_qlora_with_kwargs(self):
        """Test apply_qlora with keyword arguments."""
        model = SimpleTransformer(hidden_size=256, num_layers=1)
        
        qlora_model = apply_qlora(
            model,
            rank=16,
            alpha=32.0,
            quantization_bits=8,
            quantization_scheme="fp4"        )
        
        assert qlora_model.config.rank == 16
        assert qlora_model.config.alpha == 32.0
        assert qlora_model.config.bits == 8
        assert qlora_model.config.quantization_scheme == "fp4"
    
    def test_memory_estimation(self):
        """Test memory estimation utility."""
        model = SimpleTransformer(hidden_size=512, num_layers=2)
        
        estimates = estimate_qlora_memory_savings(model)
        
        # Check required fields
        required_fields = [
            "original_memory_mb", "qlora_memory_mb", "memory_saved_mb",
            "compression_ratio", "adaptable_params", "total_params"
        ]
        
        for field in required_fields:
            assert field in estimates
            assert isinstance(estimates[field], (int, float))
        
        # Memory savings should be positive
        assert estimates["memory_saved_mb"] > 0
        assert estimates["compression_ratio"] > 1.0
        assert estimates["adaptable_params"] > 0
        assert estimates["total_params"] >= estimates["adaptable_params"]


class TestQLoRAIntegration:
    """Integration tests for QLoRA functionality."""
    
    def test_end_to_end_workflow(self):
        """Test complete QLoRA workflow."""
        # Create model
        model = SimpleTransformer(hidden_size=384, num_layers=1)
        
        # Estimate memory savings
        estimates = estimate_qlora_memory_savings(model)
        assert estimates["memory_saved_mb"] > 0
        
        # Apply QLoRA
        config = EnhancedLoRAConfig(
            rank=8,
            alpha=16.0,
            quantization_bits=4,
            quantization_scheme="nf4"
        )
        
        qlora_model = apply_qlora(model, config)
        
        # Test forward pass
        x = torch.randn(3, 384)
        output = qlora_model(x)
        assert output.shape == (3, 384)
        
        # Get memory statistics
        stats = qlora_model.get_memory_stats()
        assert stats["total_statistics"]["memory_saved_mb"] > 0
        
        # Merge and unload
        merged_model = qlora_model.merge_and_unload()
        
        # Test merged model
        merged_output = merged_model(x)
        assert merged_output.shape == (3, 384)
        
        # Outputs should be similar (but not identical due to quantization)
        diff = torch.abs(output - merged_output).mean()
        assert diff < 1.0  # Allow for quantization differences
    
    def test_memory_efficiency_validation(self):
        """Test that QLoRA actually saves memory."""
        model = SimpleTransformer(hidden_size=512, num_layers=2)
        
        # Count original parameters
        original_params = sum(p.numel() for p in model.parameters())
        original_memory = original_params * 4 / (1024 * 1024)  # MB
        
        # Apply QLoRA
        qlora_model = apply_qlora(model, quantization_bits=4)
        
        # Get memory statistics
        stats = qlora_model.get_memory_stats()
        qlora_memory = stats["total_statistics"]["total_mb"]
        
        # QLoRA should use less memory
        assert qlora_memory < original_memory
        
        # Compression ratio should be reasonable
        compression_ratio = original_memory / qlora_memory
        assert compression_ratio > 1.5  # At least 1.5x compression
    
    def test_gradient_flow(self):
        """Test that gradients flow correctly through QLoRA layers."""
        model = SimpleTransformer(hidden_size=256, num_layers=1)
        qlora_model = apply_qlora(model, rank=8)
        
        # Create dummy input and target
        x = torch.randn(2, 256)
        target = torch.randn(2, 256)
        
        # Forward pass
        output = qlora_model(x)
        loss = nn.functional.mse_loss(output, target)
        
        # Backward pass
        loss.backward()
        
        # Check that LoRA parameters have gradients
        lora_grad_count = 0
        for name, param in qlora_model.named_parameters():
            if param.requires_grad and param.grad is not None:
                if 'lora' in name:
                    lora_grad_count += 1
                    assert not torch.isnan(param.grad).any()
        
        # Should have gradients for LoRA parameters
        assert lora_grad_count > 0


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
