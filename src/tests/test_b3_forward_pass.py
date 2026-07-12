#!/usr/bin/env python3
"""
Test B3 Foundation model forward pass on CPU.
"""
import pytest
import torch

from src.core.models.b3_foundation_architecture import B3FoundationConfig
from src.core.models.b3_foundation import B3Foundation


def test_b3_foundation_cpu_forward_pass():
    # Initialize configuration with small dimensions for faster testing
    config = B3FoundationConfig()
    
    # Instantiate model
    model = B3Foundation(config)
    
    # Ensure model is on CPU
    model.cpu()
    
    # Generate dummy input ids (batch_size=2, seq_len=16)
    batch_size = 2
    seq_len = 16
    input_ids = torch.randint(0, config.vocab_size, (batch_size, seq_len))
    
    # Disable gradient tracking for smoke test
    with torch.no_grad():
        logits, aux_outputs = model(input_ids, return_aux_outputs=True)
        
    # Assert output shapes
    assert logits is not None
    assert logits.shape == (batch_size, seq_len, config.vocab_size)
    
    # Assert auxiliary outputs
    assert aux_outputs is not None
    assert "router" in aux_outputs
    assert "assembly_of_experts" in aux_outputs
    assert "attention" in aux_outputs
    assert "brainsim_adapter" in aux_outputs
    assert "load_balancing_loss" in aux_outputs
    
    # Check that loss is a scalar tensor
    loss = aux_outputs["load_balancing_loss"]
    assert isinstance(loss, torch.Tensor)
    assert loss.dim() == 0  # scalar
