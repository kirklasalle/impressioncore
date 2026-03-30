#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #multimodal #python #source_code #src/training/b2_multimodal/real_dataset_loader.py #training
**Category:** Training System
**Status:** Active
"""









# Real Dataset Loader

# Created:** October 15, 2024
# Updated:** August 4, 2025
# Author:** ImpressionCore Team
# Tags:** #multimodal #python #source_code #src\\training\\b2_multimodal\\real_dataset_loader.py #training
# Category:** Training System
# Status:** Active

"""
real_dataset_loader.py
Loader for real multimodal datasets for B2 training.
"""

from torch.utils.data import Dataset

from src.training.datasets.data_loading import (
    create_multimodal_dataset,
    load_audio_data,
    load_image_data,
    load_text_data,
)


class RealMultimodalDataset(Dataset):
    """
    Loads and aligns real multimodal data for B2 training.
    Args:
        text_path: Path to text data (file or dir)
        image_path: Path to image data (file or dir)
        audio_path: Path to audio data (file or dir)
        max_samples: Max samples to load
        alignment_strategy: How to align modalities
    Returns:
        torch.utils.data.Dataset
    """
    def __init__(self, text_path: str, image_path: str, audio_path: str, max_samples: int | None = None, alignment_strategy: str = "round_robin"):
        text_data = load_text_data(text_path, max_samples=max_samples)
        image_data = load_image_data(image_path, max_samples=max_samples)
        audio_data = load_audio_data(audio_path, max_samples=max_samples)
        self.samples = create_multimodal_dataset(text_data, image_data, audio_data, alignment_strategy=alignment_strategy)

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        # Returns a dict with available modalities for the sample
        return self.samples[idx]
