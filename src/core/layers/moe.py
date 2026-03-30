#!/usr/bin/env python3
r"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** July-29-2025
**Author:** ImpressionCore Team
**Tags:** #python #source_code #src/models/layers/moe.py
**Category:** Source Code
**Status:** Active
"""







# Moe

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:02
# Author:** ImpressionCore Team
# Tags:** #python #source_code #src/models/layers/moe.py
# Category:** Source Code
# Status:** Active

"""
Mixture of Experts (MoE) layer for ImpressionCore-b1.

Implements a simple gating mechanism to route inputs to expert sub-networks.
"""
import torch
import torch.nn as nn
import torch.nn.functional as F


class MoELayer(nn.Module):
    """
    Mixture of Experts layer with configurable number of experts and gating.
    Args:
        input_dim (int): Input feature dimension.
        output_dim (int): Output feature dimension.
        num_experts (int): Number of expert sub-networks.
        hidden_dim (int): Hidden dimension for each expert.
    """
    def __init__(self, input_dim: int, output_dim: int, num_experts: int = 4, hidden_dim: int = 128):
        super().__init__()
        self.num_experts = num_experts
        self.gate = nn.Linear(input_dim, num_experts)
        self.experts = nn.ModuleList([
            nn.Sequential(
                nn.Linear(input_dim, hidden_dim),
                nn.ReLU(),
                nn.Linear(hidden_dim, output_dim)
            ) for _ in range(num_experts)
        ])

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Compute gating weights
        gate_logits = self.gate(x)
        gate_weights = F.softmax(gate_logits, dim=-1)  # [batch, num_experts]
        # Compute expert outputs
        expert_outputs = torch.stack([expert(x) for expert in self.experts], dim=-1)  # [batch, output_dim, num_experts]
        # Weighted sum of expert outputs
        output = (expert_outputs * gate_weights.unsqueeze(1)).sum(dim=-1)
        return output
