#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #multimodal #python #source_code #src/training/b2_multimodal/multimodal_dataset.py #testing #training
**Category:** Training System
**Status:** Active
"""









# Multimodal Dataset

# Created:** October 15, 2024
# Updated:** August 4, 2025
# Author:** ImpressionCore Team
# Tags:** #multimodal #python #source_code #src\\training\\b2_multimodal\\multimodal_dataset.py #testing #training
# Category:** Training System
# Status:** Active

"""
Minimal multimodal dataset for B2MultimodalTrainer integration test.
"""
import torch
from torch.utils.data import Dataset


class DummyMultimodalDataset(Dataset):
    def __init__(self, num_samples=10, vocab_size=50257, img_dim=32, audio_dim=16000, seq_len=32):
        self.num_samples = num_samples
        self.vocab_size = vocab_size
        self.img_dim = img_dim
        self.audio_dim = audio_dim
        self.seq_len = seq_len

    def __len__(self):
        return self.num_samples

    def __getitem__(self, idx):
        return {
            'text': torch.randint(0, self.vocab_size, (self.seq_len,)),
            'vision': torch.randn(3, self.img_dim, self.img_dim),
            'audio': torch.randn(self.audio_dim),
            'video': torch.randn(4, 3, self.img_dim, self.img_dim),
            'modality_type': None
        }
