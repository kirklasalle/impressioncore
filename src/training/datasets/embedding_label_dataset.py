#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #python #source_code #src/training/datasets/embedding_label_dataset.py #training
**Category:** Training System
**Status:** Active
"""









# Embedding Label Dataset

# Created:** October 15, 2024
# Updated:** August 4, 2025
# Author:** ImpressionCore Team
# Tags:** #python #source_code #src\\training\\datasets\\embedding_label_dataset.py #training
# Category:** Training System
# Status:** Active

import json
from pathlib import Path

import torch
from torch.utils.data import Dataset


class EmbeddingLabelDataset(Dataset):
    """
    Loads embeddings and their sentiment/intent labels from a manifest JSON file.
    Each entry in the manifest should have: 'conversation_id', 'sentiment_label', 'intent_label'.
    Embedding files are loaded from embedding_root (default: F:/b2_embeddings/).
    """
    def __init__(self, manifest_path: str, embedding_root: str | None = None):
        self.manifest_path = Path(manifest_path)
        # Use F:/b2_embeddings/ as default if not specified
        if embedding_root is None:
            self.embedding_root = Path('F:/b2_embeddings/')
        else:
            self.embedding_root = Path(embedding_root)
        with open(self.manifest_path, encoding='utf-8') as f:
            self.samples = json.load(f)

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        sample = self.samples[idx]
        # Try to get embedding_path, else construct from conversation_id
        if 'embedding_path' in sample:
            emb_path = Path(sample['embedding_path'])
        else:
            # Assume embeddings are stored as embeddings/{conversation_id}.npy
            emb_name = f"{sample['conversation_id']}.npy"
            emb_path = Path('embeddings') / emb_name
        if self.embedding_root and not emb_path.is_absolute():
            emb_path = self.embedding_root / emb_path
        import numpy as np
        emb = torch.tensor(np.load(emb_path), dtype=torch.float32)
        sentiment = int(sample['sentiment_label'])
        intent = int(sample['intent_label'])
        return {
            'embeddings': emb,
            'sentiment_labels': sentiment,
            'intent_labels': intent
        }
