#!/usr/bin/env python3
"""
ImpressionCore: Test Mock Models

Utility module for creating mock models for testing purposes.

File: tests/utils/mock_models.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-06-01
Modified: 2025-06-01
Version: 1.0.0

Authors:
- GitHub Copilot
- Development Team

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [testing, utilities, mock, models, 2025]
Dependencies: [torch]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
Utility functions for creating mock models for testing purposes.
Provides standardized test models with configurable parameters.
"""

import torch
import torch.nn as nn
from typing import Optional


class MockTransformerLayer(nn.Module):
    """Mock transformer layer for testing."""
    
    def __init__(self, hidden_size: int, num_heads: int, intermediate_size: int):
        super().__init__()
        self.hidden_size = hidden_size
        self.num_heads = num_heads
        self.intermediate_size = intermediate_size
        
        # Attention layers
        self.q_proj = nn.Linear(hidden_size, hidden_size)
        self.k_proj = nn.Linear(hidden_size, hidden_size)
        self.v_proj = nn.Linear(hidden_size, hidden_size)
        self.o_proj = nn.Linear(hidden_size, hidden_size)
        
        # Feed-forward layers
        self.up_proj = nn.Linear(hidden_size, intermediate_size)
        self.down_proj = nn.Linear(intermediate_size, hidden_size)
        self.gate_proj = nn.Linear(hidden_size, intermediate_size)
        
        # Layer norms
        self.input_layernorm = nn.LayerNorm(hidden_size)
        self.post_attention_layernorm = nn.LayerNorm(hidden_size)
        
        # Dropout
        self.dropout = nn.Dropout(0.1)
    
    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        """Forward pass through mock transformer layer."""
        # Self-attention
        residual = hidden_states
        hidden_states = self.input_layernorm(hidden_states)
        
        # Mock attention computation
        q = self.q_proj(hidden_states)
        k = self.k_proj(hidden_states)
        v = self.v_proj(hidden_states)
        
        # Simplified attention (not actual multi-head)
        attention_output = torch.matmul(q, k.transpose(-2, -1))
        attention_output = torch.softmax(attention_output, dim=-1)
        attention_output = torch.matmul(attention_output, v)
        attention_output = self.o_proj(attention_output)
        
        hidden_states = residual + self.dropout(attention_output)
        
        # Feed-forward
        residual = hidden_states
        hidden_states = self.post_attention_layernorm(hidden_states)
        
        up_states = self.up_proj(hidden_states)
        gate_states = self.gate_proj(hidden_states)
        hidden_states = self.down_proj(torch.nn.functional.silu(gate_states) * up_states)
        
        hidden_states = residual + self.dropout(hidden_states)
        
        return hidden_states


class MockTransformerModel(nn.Module):
    """Mock transformer model for testing."""
    
    def __init__(
        self,
        hidden_size: int = 768,
        num_layers: int = 12,
        num_heads: int = 12,
        intermediate_size: int = 3072,
        vocab_size: int = 50000
    ):
        super().__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.num_heads = num_heads
        self.intermediate_size = intermediate_size
        self.vocab_size = vocab_size
        
        # Embedding layers
        self.embed_tokens = nn.Embedding(vocab_size, hidden_size)
        self.embed_positions = nn.Embedding(2048, hidden_size)  # Max seq len 2048
        
        # Transformer layers
        self.layers = nn.ModuleList([
            MockTransformerLayer(hidden_size, num_heads, intermediate_size)
            for _ in range(num_layers)
        ])
        
        # Output layers
        self.norm = nn.LayerNorm(hidden_size)
        self.lm_head = nn.Linear(hidden_size, vocab_size, bias=False)
        
        # Initialize weights
        self._init_weights()
    
    def _init_weights(self):
        """Initialize model weights."""
        for module in self.modules():
            if isinstance(module, nn.Linear):
                nn.init.normal_(module.weight, mean=0.0, std=0.02)
                if module.bias is not None:
                    nn.init.zeros_(module.bias)
            elif isinstance(module, nn.Embedding):
                nn.init.normal_(module.weight, mean=0.0, std=0.02)
            elif isinstance(module, nn.LayerNorm):
                nn.init.ones_(module.weight)
                nn.init.zeros_(module.bias)
    
    def forward(
        self, 
        input_ids: torch.Tensor,
        position_ids: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """Forward pass through mock transformer."""
        batch_size, seq_len = input_ids.shape
        
        if position_ids is None:
            position_ids = torch.arange(seq_len, device=input_ids.device).unsqueeze(0)
        
        # Embeddings
        hidden_states = self.embed_tokens(input_ids)
        hidden_states = hidden_states + self.embed_positions(position_ids)
        
        # Transformer layers
        for layer in self.layers:
            hidden_states = layer(hidden_states)
        
        # Output
        hidden_states = self.norm(hidden_states)
        logits = self.lm_head(hidden_states)
        
        return logits


def create_test_model(
    hidden_size: int = 768,
    num_layers: int = 12,
    num_heads: int = 12,
    intermediate_size: int = 3072,
    vocab_size: int = 50000
) -> MockTransformerModel:
    """
    Create a test model for testing purposes.
    
    Args:
        hidden_size: Hidden dimension size
        num_layers: Number of transformer layers
        num_heads: Number of attention heads
        intermediate_size: Feed-forward intermediate size
        vocab_size: Vocabulary size
        
    Returns:
        MockTransformerModel: Test model instance
    """
    model = MockTransformerModel(
        hidden_size=hidden_size,
        num_layers=num_layers,
        num_heads=num_heads,
        intermediate_size=intermediate_size,
        vocab_size=vocab_size
    )
    
    return model


def create_small_test_model() -> MockTransformerModel:
    """Create a small test model for memory-constrained testing."""
    return create_test_model(
        hidden_size=256,
        num_layers=6,
        num_heads=8,
        intermediate_size=1024,
        vocab_size=10000
    )


def create_large_test_model() -> MockTransformerModel:
    """Create a large test model for stress testing."""
    return create_test_model(
        hidden_size=1024,
        num_layers=24,
        num_heads=16,
        intermediate_size=4096,
        vocab_size=50000
    )


def get_model_parameter_count(model: nn.Module) -> int:
    """Get total parameter count for a model."""
    return sum(p.numel() for p in model.parameters())


def get_model_memory_footprint(model: nn.Module) -> int:
    """Get approximate memory footprint in bytes."""
    param_count = get_model_parameter_count(model)
    # Assume float32 = 4 bytes per parameter
    return param_count * 4
