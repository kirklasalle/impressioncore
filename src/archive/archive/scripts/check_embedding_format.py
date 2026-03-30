#!/usr/bin/env python3
"""Quick check of F: drive embedding file format"""

import numpy as np
from pathlib import Path

embedding_file = Path("F:/data/embeddings/sentence_transformers/conversational/embeddings.npy")

print(f"Loading: {embedding_file}")
print(f"File size: {embedding_file.stat().st_size / (1024**2):.2f} MB")

try:
    embeddings = np.load(embedding_file, allow_pickle=True)
    print(f"\n✅ Loaded successfully!")
    print(f"Type: {type(embeddings)}")
    print(f"Dtype: {embeddings.dtype}")
    print(f"Shape: {embeddings.shape}")

    if len(embeddings.shape) == 2:
        print(f"Num vectors: {embeddings.shape[0]}")
        print(f"Vector dim: {embeddings.shape[1]}")

    # Sample first vector
    if len(embeddings) > 0:
        print(f"\nFirst vector sample:")
        print(f"  Min: {embeddings[0].min():.4f}")
        print(f"  Max: {embeddings[0].max():.4f}")
        print(f"  Mean: {embeddings[0].mean():.4f}")
        print(f"  First 5 values: {embeddings[0][:5]}")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
