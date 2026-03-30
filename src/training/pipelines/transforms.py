"""Data Transform Pipeline Components (Initial Skeleton)
Created: August 22, 2025
Author: GitHub Copilot

Purpose: Modular transform callables for text, image, audio embedding augmentation.
Categories Covered: 5 (Enrichment & Augmentation), partially 2 (Performance via fp16 casting).
"""
from __future__ import annotations

import random

import torch


class SpanMaskingTransform:
    """Randomly masks contiguous spans of token ids for denoising-style training."""
    def __init__(self, mask_prob: float = 0.15, avg_span: int = 3, mask_token_id: int = 50256):
        self.mask_prob = mask_prob
        self.avg_span = avg_span
        self.mask_token_id = mask_token_id

    def __call__(self, sample: dict[str, torch.Tensor]) -> dict[str, torch.Tensor]:
        input_ids = sample['input_ids']
        if random.random() > self.mask_prob:
            return sample
        length = input_ids.shape[-1]
        span = max(1, int(random.expovariate(1 / self.avg_span)))
        start = random.randint(0, max(0, length - span))
        input_ids[..., start:start+span] = self.mask_token_id
        sample['input_ids'] = input_ids
        return sample

class EmbeddingNoiseTransform:
    """Adds low magnitude Gaussian noise to modality embeddings (image/audio)."""
    def __init__(self, std: float = 0.01):
        self.std = std

    def __call__(self, sample: dict[str, torch.Tensor]) -> dict[str, torch.Tensor]:
        for key in ('image_embeddings', 'audio_embeddings'):
            if key in sample:
                sample[key] = sample[key] + torch.randn_like(sample[key]) * self.std
        return sample

class ModalityDropoutTransform:
    """Randomly drop (zero) a modality embedding to improve robustness."""
    def __init__(self, drop_prob: float = 0.1):
        self.drop_prob = drop_prob

    def __call__(self, sample: dict[str, torch.Tensor]) -> dict[str, torch.Tensor]:
        for key in ('image_embeddings', 'audio_embeddings'):
            if key in sample and random.random() < self.drop_prob:
                sample[key] = torch.zeros_like(sample[key])
                sample[f'{key}_dropped'] = torch.tensor(1, dtype=torch.uint8)
            else:
                sample[f'{key}_dropped'] = torch.tensor(0, dtype=torch.uint8)
        return sample

class ProjectionSummaryTransform:
    """Appends a simple learned linear projection summary token (placeholder)."""
    def __init__(self, embed_dim: int):
        self.proj = torch.nn.Linear(embed_dim, embed_dim)

    def __call__(self, sample: dict[str, torch.Tensor]) -> dict[str, torch.Tensor]:
        if 'image_embeddings' in sample:
            summary = self.proj(sample['image_embeddings']).unsqueeze(1)
            # Expect input_ids is [B, T]; we add a dummy summary id at end by cloning last
            sample['image_summary'] = summary.mean(dim=0)
        return sample

# Registry helper
DEFAULT_TRANSFORMS = [
    SpanMaskingTransform(mask_prob=0.05),
    EmbeddingNoiseTransform(std=0.005),
    ModalityDropoutTransform(drop_prob=0.05),
]
