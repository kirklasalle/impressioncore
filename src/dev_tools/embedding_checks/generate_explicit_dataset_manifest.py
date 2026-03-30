#!/usr/bin/env python3
"""Generate an explicit per-dataset-entry embedding manifest suitable for training.

Outputs:
- src/memlog/dataset_to_embedding_explicit.ndjson  # all dataset entries with mapping (inferred or exact)
- src/memlog/dataset_to_embedding_training_manifest.ndjson  # only mapped entries

Heuristics:
- use chunk map exact_1to1 and best_effort mappings to produce reverse lookup
- fallback: for single-row embedding files map dataset -> (file, row=0)
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np


def stream_ndjson(path: str):
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def load_chunk_map(path: str) -> dict[str, dict]:
    d = {}
    for rec in stream_ndjson(path):
        emb = rec.get("embedding") or rec.get("embedding")
        if emb:
            d[emb] = rec
    return d


def normalize_path(p: str) -> str:
    if p.startswith("F:data"):
        p = p.replace("F:data", "F:/data")
    return p.replace("\\", "/")


def build_reverse_from_chunk_map(chunk_map: dict[str, dict]):
    rev = {}
    for emb, rec in chunk_map.items():
        embn = normalize_path(emb)
        typ = rec.get("mapped_type")
        paths = rec.get("dataset_paths") or []
        # assign dataset -> (emb, row, inferred)
        for i, ds in enumerate(paths):
            dsn = ds.replace("\\", "/")
            if typ == "exact_1to1":
                rev[dsn] = {"embedding": embn, "row_index": i, "inferred": False, "source": "chunk_exact"}
            else:
                rev[dsn] = {"embedding": embn, "row_index": i, "inferred": True, "source": "chunk_best_effort"}
    return rev


def main():
    mapping_refined = "src/memlog/dataset_to_embedding_mapping_refined.ndjson"
    chunk_map_path = "src/memlog/chunk_index_dataset_range_map.ndjson"
    out_explicit = "src/memlog/dataset_to_embedding_explicit.ndjson"
    out_training = "src/memlog/dataset_to_embedding_training_manifest.ndjson"
    if len(sys.argv) > 1:
        mapping_refined = sys.argv[1]
    if len(sys.argv) > 2:
        chunk_map_path = sys.argv[2]

    chunk_map = {}
    if os.path.exists(chunk_map_path):
        chunk_map = load_chunk_map(chunk_map_path)
    reverse = build_reverse_from_chunk_map(chunk_map)

    os.makedirs(os.path.dirname(out_explicit), exist_ok=True)
    fout_all = open(out_explicit, "w", encoding="utf-8")
    fout_train = open(out_training, "w", encoding="utf-8")

    counts = {"total_dataset_entries": 0, "mapped": 0, "inferred": 0, "exact_chunk": 0, "single_row": 0}

    for rec in stream_ndjson(mapping_refined):
        ds = rec.get("dataset")
        if not ds:
            continue
        counts["total_dataset_entries"] += 1
        dsn = ds.replace("\\", "/")

        mapped = None
        # first, check reverse chunk map
        if dsn in reverse:
            mapped = reverse[dsn].copy()
            mapped.update({"dataset": dsn})
            if mapped.get("inferred"):
                counts["inferred"] += 1
            else:
                counts["exact_chunk"] += 1

        # second, if mapping record has embeddings and file is single-row, use it
        if not mapped:
            emb_list = rec.get("embeddings") or []
            if emb_list:
                # prefer first embedding
                e = normalize_path(emb_list[0])
                try:
                    if os.path.exists(e):
                        arr = np.load(e, mmap_mode="r")
                        if arr.ndim == 1:
                            mapped = {"dataset": dsn, "embedding": e, "row_index": 0, "inferred": False, "source": "refined_mapping_single_row"}
                            counts["single_row"] += 1
                        elif arr.ndim == 2 and arr.shape[0] == 1:
                            mapped = {"dataset": dsn, "embedding": e, "row_index": 0, "inferred": False, "source": "refined_mapping_single_row2d"}
                            counts["single_row"] += 1
                        else:
                            # 2D but multi-row: if chunk_map contains emb, will be caught earlier; otherwise mark as inferred 0
                            mapped = {"dataset": dsn, "embedding": e, "row_index": 0, "inferred": True, "source": "refined_mapping_multiro\n"}
                            counts["inferred"] += 1
                    else:
                        mapped = None
                except Exception:
                    mapped = None

        if mapped:
            counts["mapped"] += 1
            fout_all.write(json.dumps(mapped) + "\n")
            fout_train.write(json.dumps(mapped) + "\n")
        else:
            # leave unmapped out of training manifest, but still write explicit with nulls
            fout_all.write(json.dumps({"dataset": dsn, "embedding": None, "row_index": None, "inferred": True, "source": "unmapped"}) + "\n")

    fout_all.close()
    fout_train.close()

    print("Wrote explicit manifest to", out_explicit)
    print("Wrote training manifest to", out_training)
    print("Counts:", counts)


if __name__ == "__main__":
    main()
