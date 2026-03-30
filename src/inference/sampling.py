#!/usr/bin/env python3
r"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #inference #python #source_code #src/inference/sampling.py
**Category:** Source Code
**Status:** Active
"""









# Sampling

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:01
# Author:** ImpressionCore Team
# Tags:** #inference #python #source_code #src/inference/sampling.py
# Category:** Source Code
# Status:** Active

"""
Sampling engine for ImpressionCore-b1.

Implements top-k, top-p, temperature, and other decoding strategies.
"""
from typing import Any


class SamplingParams:
    """
    Sampling configuration for inference.
    """
    def __init__(self, temperature: float = 1.0, top_k: int = 0, top_p: float = 1.0, max_tokens: int = 256):
        self.temperature = temperature
        self.top_k = top_k
        self.top_p = top_p
        self.max_tokens = max_tokens

class Sampler:
    """
    Sampling engine for decoding model outputs.
    Implements top-k, top-p, and temperature sampling.
    """
    def __init__(self, params: SamplingParams):
        self.params = params

    def sample(self, logits: Any) -> Any:
        """
        Sample from logits using top-k, top-p, and temperature strategies.
        Args:
            logits (Any): Model output logits or probabilities.
        Returns:
            Any: Sampled output (e.g., token IDs or text).
        """
        import torch
        if not isinstance(logits, torch.Tensor):
            return logits
        logits = logits / max(self.params.temperature, 1e-6)
        probs = torch.softmax(logits, dim=-1)
        # Top-k
        if self.params.top_k > 0:
            top_k = min(self.params.top_k, probs.size(-1))
            topk_probs, topk_indices = torch.topk(probs, top_k, dim=-1)
            probs = torch.zeros_like(probs).scatter_(-1, topk_indices, topk_probs)
        # Top-p (nucleus)
        if self.params.top_p < 1.0:
            sorted_probs, sorted_indices = torch.sort(probs, descending=True, dim=-1)
            cumulative_probs = torch.cumsum(sorted_probs, dim=-1)
            mask = cumulative_probs > self.params.top_p
            sorted_probs[mask] = 0
            probs = torch.zeros_like(probs).scatter_(-1, sorted_indices, sorted_probs)
        # Normalize
        probs = probs / (probs.sum(dim=-1, keepdim=True) + 1e-8)
        # Sample
        sampled = torch.multinomial(probs, num_samples=1)
        return sampled.squeeze(-1)
