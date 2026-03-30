#!/usr/bin/env python3
r"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** July-29-2025
**Author:** ImpressionCore Team
**Tags:** #attention_mechanism #python #source_code #src/models/layers/latent_attention.py #transformer
**Category:** Source Code
**Status:** Active
"""







# Latent Attention

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:02
# Author:** ImpressionCore Team
# Tags:** #attention_mechanism #python #source_code #src/models/layers/latent_attention.py #transformer
# Category:** Source Code
# Status:** Active

"""
Latent Attention Head module for ImpressionCore-b1.

Implements a transformer attention layer with support for latent (dynamically activated) heads.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F


class LatentMultiheadAttention(nn.Module):
    """
    Multihead attention with latent (selectively activated) heads.
    Args:
        embed_dim (int): Embedding dimension.
        num_heads (int): Total number of attention heads.
        latent_mask (Optional[torch.Tensor]): Boolean mask for latent heads (1=active, 0=latent).
    """
    def __init__(self, embed_dim: int, num_heads: int, latent_mask: torch.Tensor | None = None):
        super().__init__()
        self.embed_dim = embed_dim
        self.num_heads = num_heads
        self.head_dim = embed_dim // num_heads
        assert self.head_dim * num_heads == embed_dim, "embed_dim must be divisible by num_heads"
        self.qkv_proj = nn.Linear(embed_dim, 3 * embed_dim)
        self.out_proj = nn.Linear(embed_dim, embed_dim)
        self.latent_mask = latent_mask  # [num_heads] or None

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B, T, C = x.shape
        qkv = self.qkv_proj(x).reshape(B, T, 3, self.num_heads, self.head_dim)
        q, k, v = qkv.unbind(dim=2)  # Each: [B, T, num_heads, head_dim]
        attn_scores = (q @ k.transpose(-2, -1)) / (self.head_dim ** 0.5)  # [B, T, num_heads, T]
        attn_weights = F.softmax(attn_scores, dim=-1)
        # Apply latent mask if provided
        if self.latent_mask is not None:
            attn_weights = attn_weights * self.latent_mask.view(1, 1, -1, 1)
        attn_output = (attn_weights @ v).transpose(1, 2).reshape(B, T, C)
        return self.out_proj(attn_output)
