#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #cuda #memory_management #python #source_code #src/dev_tools/data_generation/b3_streaming_dataset.py #testing #tokenization #transformer
**Category:** Development Tools
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:01
# Author:** ImpressionCore Team
# Tags:** #cuda #memory_management #python #source_code #src\\dev_tools\\data_generation\\b3_streaming_dataset.py #testing #tokenization #transformer
# Category:** Development Tools
# Status:** Active

"""
ImpressionCore B3 Streaming Dataset System
==========================================
🌊 UNLIMITED EMBEDDING PROCESSING FOR FULL F: DRIVE
🎯 Handles 323K+ embeddings with GTX 1050 Ti optimization
⚡ Streaming pipeline with zero-memory constraints
"""

import gc
import pickle
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import torch
from rich.console import Console
from torch.utils.data import IterableDataset
from transformers import AutoTokenizer

console = Console()

@dataclass
class StreamingConfig:
    root_path: str = "F:/"
    max_seq_length: int = 512
    embedding_dim: int = 768
    num_workers: int = 4
    batch_size: int = 8
    memory_limit_gb: float = 3.5
    checkpoint_interval: int = 1000

class StreamingDataset(IterableDataset):
    """Memory-efficient streaming dataset for unlimited embeddings"""

    def __init__(self, config: StreamingConfig, tokenizer):
        self.config = config
        self.tokenizer = tokenizer
        self.root_path = Path(config.root_path)
        self.processed_files = set()
        self.failed_files = set()
        self.total_processed = 0

        # Load progress
        self._load_progress()

    def _load_progress(self):
        checkpoint_path = Path("checkpoints/streaming_progress.pkl")
        if checkpoint_path.exists():
            try:
                with open(checkpoint_path, 'rb') as f:
                    data = pickle.load(f)
                    self.processed_files = data.get('processed_files', set())
                    self.total_processed = data.get('total_processed', 0)
                console.print(f"[green]✅ Loaded progress: {self.total_processed} files[/green]")
            except Exception:
                pass

    def _save_progress(self):
        checkpoint_path = Path("checkpoints/streaming_progress.pkl")
        checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
        with open(checkpoint_path, 'wb') as f:
            pickle.dump({
                'processed_files': self.processed_files,
                'total_processed': self.total_processed
            }, f)

    def _process_file(self, file_path: Path) -> dict | None:
        """Process single embedding file with robust dimension handling"""
        try:
            if file_path.suffix != '.npy':
                return None

            # Memory-mapped loading
            embedding = np.load(file_path, mmap_mode='r')
            if embedding.size == 0:
                return None

            # Ensure correct shape and handle different dimensions
            embedding = np.array(embedding, dtype=np.float32)

            # Handle different input dimensions
            if embedding.ndim == 1:
                # 1D array - reshape to 2D
                embedding = embedding.reshape(1, -1)
            elif embedding.ndim == 3:
                # 3D array (e.g., video frames) - flatten to 2D
                original_shape = embedding.shape
                embedding = embedding.reshape(original_shape[0], -1)
            elif embedding.ndim == 4:
                # 4D array (e.g., batched video frames) - flatten to 2D
                original_shape = embedding.shape
                embedding = embedding.reshape(original_shape[0] * original_shape[1], -1)
            elif embedding.ndim > 4:
                # Higher dimensions - flatten completely then reshape
                embedding = embedding.flatten()
                embedding = embedding.reshape(1, -1)

            # Now we have a 2D array [seq_len, features]
            seq_len, features = embedding.shape

            # Pad/truncate to target dimension
            if features < self.config.embedding_dim:
                padding_shape = (seq_len, self.config.embedding_dim - features)
                padding = np.zeros(padding_shape, dtype=np.float32)
                embedding = np.concatenate([embedding, padding], axis=1)
            elif features > self.config.embedding_dim:
                embedding = embedding[:, :self.config.embedding_dim]

            # Ensure sequence length
            current_seq_len = embedding.shape[0]
            if current_seq_len < self.config.max_seq_length:
                padding_shape = (self.config.max_seq_length - current_seq_len, self.config.embedding_dim)
                padding = np.zeros(padding_shape, dtype=np.float32)
                embedding = np.concatenate([embedding, padding], axis=0)
            elif current_seq_len > self.config.max_seq_length:
                embedding = embedding[:self.config.max_seq_length, :]

            return {
                'file_path': str(file_path),
                'embedding': embedding,
                'tokens': self.tokenizer.encode(
                    f"Processing embedding from {file_path.stem}",
                    truncation=True,
                    max_length=self.config.max_seq_length,
                    padding='max_length'
                )
            }

        except Exception as e:
            console.print(f"[red]❌ Error processing {file_path}: {e}[/red]")
            self.failed_files.add(str(file_path))
            return None

    def __iter__(self):
        """Main streaming iterator"""
        console.print(f"[cyan]🔍 Starting streaming from {self.config.root_path}[/cyan]")

        # Discover files
        files = list(self.root_path.rglob("*.npy"))
        console.print(f"[cyan]📊 Found {len(files)} .npy files[/cyan]")

        # Process in parallel
        with ThreadPoolExecutor(max_workers=self.config.num_workers):
            for file_path in files:
                if str(file_path) in self.processed_files:
                    continue

                result = self._process_file(file_path)
                if result is not None:
                    yield {
                        'input_ids': torch.tensor(result['tokens']),
                        'labels': torch.tensor(result['tokens']),
                        'embeddings': torch.from_numpy(result['embedding']).float(),
                        'modality_type': torch.tensor([3] * self.config.max_seq_length)
                    }

                    self.processed_files.add(str(file_path))
                    self.total_processed += 1

                    if self.total_processed % self.config.checkpoint_interval == 0:
                        self._save_progress()
                        console.print(f"[green]✅ Checkpoint: {self.total_processed} files processed[/green]")

                        # Memory cleanup
                        gc.collect()
                        if torch.cuda.is_available():
                            torch.cuda.empty_cache()

# Usage example
if __name__ == "__main__":
    config = StreamingConfig(root_path="test_embeddings")
    tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-small")
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    dataset = StreamingDataset(config, tokenizer)

    count = 0
    for _sample in dataset:
        count += 1
        if count >= 10:
            break

    console.print(f"[bold green]✅ Test completed: {count} samples processed[/bold green]")
