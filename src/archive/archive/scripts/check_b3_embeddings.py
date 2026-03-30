#!/usr/bin/env python3
"""Check B3 39M embeddings"""

import numpy as np
from pathlib import Path

b3_dir = Path("F:/data/embeddings/b3_39m")
sample_file = next(b3_dir.glob("*.npy"))

print(f"Checking: {sample_file.name}")
emb = np.load(sample_file)
print(f"Shape: {emb.shape}")
print(f"Dtype: {emb.dtype}")

# Count total files
total = len(list(b3_dir.glob("*.npy")))
print(f"\nTotal B3 39M embeddings: {total:,} files")

# Estimate total vectors
total_vectors = total * emb.shape[0] if len(emb.shape) > 0 else total
print(f"Estimated vectors: ~{total_vectors:,}")
