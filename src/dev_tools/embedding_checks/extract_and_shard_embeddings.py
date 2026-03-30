#!/usr/bin/env python3
"""Extract embeddings from training manifest and shard into numpy memmap files for training.

Outputs:
- src/memlog/shards/shard_000.npy (float32 matrix)
- src/memlog/shards/index.jsonl (NDJSON: dataset -> shard, offset)

Notes:
- This script reads `dataset_to_embedding_training_manifest.ndjson` and writes compact shards.
- It will only include entries that point to a single embedding file + row_index.
"""
from __future__ import annotations

import argparse
import json
import math
import os

import numpy as np


def stream_ndjson(path: str):
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def extract(manifest_path: str, shards_dir: str, shard_size: int = 10000):
    ensure_dir(shards_dir)
    entries = []
    dims = None
    # first pass: collect entries with existing embedding files
    for rec in stream_ndjson(manifest_path):
        emb = rec.get("embedding")
        row = rec.get("row_index")
        ds = rec.get("dataset")
        if emb and row is not None:
            embp = emb.replace("\\", "/")
            if not os.path.exists(embp):
                continue
            arr = np.load(embp, mmap_mode="r")
            vec = arr[int(row)] if arr.ndim == 2 else arr
            vec = np.asarray(vec, dtype=np.float32).reshape(-1)
            if dims is None:
                dims = vec.shape[0]
            if vec.shape[0] != dims:
                continue
            entries.append({"dataset": ds, "vector": vec})

    total = len(entries)
    if total == 0:
        print("No entries to shard.")
        return

    shards_needed = math.ceil(total / shard_size)
    index_path = os.path.join(shards_dir, "index.jsonl")
    # write shards
    idx = 0
    for s in range(shards_needed):
        take = min(shard_size, total - s * shard_size)
        shard_matrix = np.zeros((take, dims), dtype=np.float32)
        for i in range(take):
            shard_matrix[i] = entries[idx]["vector"]
            idx += 1
        shard_file = os.path.join(shards_dir, f"shard_{s:03d}.npy")
        np.save(shard_file, shard_matrix)
        print(f"Wrote shard {shard_file} with {take} vectors")

    # write index mapping (dataset -> shard, offset)
    with open(index_path, "w", encoding="utf-8") as f:
        pos = 0
        for s in range(shards_needed):
            shard_count = min(shard_size, total - s * shard_size)
            for i in range(shard_count):
                rec = entries[pos]
                f.write(json.dumps({"dataset": rec["dataset"], "shard": s, "offset": i}) + "\n")
                pos += 1

    print(f"Wrote {shards_needed} shards, index at {index_path}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", default="src/memlog/dataset_to_embedding_training_manifest.ndjson")
    ap.add_argument("--shards-dir", default="src/memlog/shards")
    ap.add_argument("--shard-size", type=int, default=10000)
    args = ap.parse_args()
    extract(args.manifest, args.shards_dir, args.shard_size)


if __name__ == "__main__":
    main()
