#!/usr/bin/env python3
"""Build an embeddings manifest and a chunk-index -> dataset-range mapping.

Outputs:
- src/memlog/embeddings_manifest.ndjson
- src/memlog/chunk_index_dataset_range_map.ndjson

Heuristics:
- detect chunk patterns in embedding filenames (e.g., prefix_chunkNNN_...)
- match dataset basenames in the mapping to prefix and chunk number
- for 2D arrays (rows>1) attempt to align rows -> dataset entries
"""
from __future__ import annotations

import argparse
import json
import os
import re
from collections import defaultdict

import numpy as np

CHUNK_RE = re.compile(r"(?P<prefix>.+?)[_\-\.]chunk(?P<chunk>\d+)(?:[_\-\.]|$)", re.IGNORECASE)


def stream_ndjson(path: str):
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def normalize_embedding_path(p: str) -> str:
    # common normalization from earlier tooling
    if p.startswith("F:data"):
        p = p.replace("F:data", "F:/data")
    p = p.replace("\\", "/")
    return p


def build_indices(mapping_path: str):
    # collect unique embedding paths and a basename->dataset list
    emb_set = set()
    basename_to_datasets: dict[str, list[str]] = defaultdict(list)
    for rec in stream_ndjson(mapping_path):
        ds = rec.get("dataset")
        if ds:
            b = os.path.splitext(os.path.basename(ds))[0]
            basename_to_datasets[b].append(ds)
        for e in rec.get("embeddings") or []:
            emb_set.add(normalize_embedding_path(e))
    return sorted(emb_set), basename_to_datasets


def inspect_embeddings(emb_paths: list[str], basename_to_datasets: dict[str, list[str]], out_manifest: str, out_chunk_map: str):
    os.makedirs(os.path.dirname(out_manifest), exist_ok=True)
    mf = open(out_manifest, "w", encoding="utf-8")
    cf = open(out_chunk_map, "w", encoding="utf-8")
    for p in emb_paths:
        rec = {"embedding": p, "exists": False}
        try:
            if not os.path.exists(p):
                rec["note"] = "file_not_found"
                mf.write(json.dumps(rec) + "\n")
                continue
            rec["exists"] = True
            a = np.load(p, mmap_mode="r")
            rec["shape"] = a.shape
            rec["dtype"] = str(a.dtype)
            if a.ndim == 2:
                rows, cols = a.shape
            elif a.ndim == 1:
                rows, cols = 1, a.shape[0]
            else:
                rows = int(a.size)
                cols = 1
            rec["rows"] = int(rows)
            rec["cols"] = int(cols)

            # detect chunk prefix/index
            m = CHUNK_RE.search(os.path.basename(p))
            if m:
                prefix = m.group("prefix")
                chunk = int(m.group("chunk"))
                rec["chunk_prefix"] = prefix
                rec["chunk_index"] = chunk
            else:
                prefix = None
                chunk = None

            mf.write(json.dumps(rec) + "\n")

            # if batched (rows>1) attempt to match dataset basenames
            if rows > 1 and prefix:
                # find dataset basenames that contain prefix and chunk number
                candidates = []
                # quick check: dataset basenames may include 'prefix_chunk<chunk>' or prefix
                for b, paths in basename_to_datasets.items():
                    if prefix in b and (True):
                        for path in paths:
                            candidates.append(path)
                # sort candidates (best-effort)
                candidates = sorted(set(candidates))
                mapping_entry = {"embedding": p, "rows": int(rows), "cols": int(cols), "candidates_count": len(candidates)}
                # if candidate count equals rows, assume 1:1 mapping
                if len(candidates) == rows:
                    mapping_entry["mapped_type"] = "exact_1to1"
                    mapping_entry["dataset_paths"] = candidates
                elif len(candidates) >= 1:
                    # if more candidates than rows, take first 'rows' as probable mapping
                    mapping_entry["mapped_type"] = "best_effort_prefix_ordered"
                    mapping_entry["dataset_paths"] = candidates[: rows]
                else:
                    mapping_entry["mapped_type"] = "none_found"
                    mapping_entry["dataset_paths"] = []
                cf.write(json.dumps(mapping_entry) + "\n")

        except Exception as ex:
            rec["error"] = str(ex)
            mf.write(json.dumps(rec) + "\n")
    mf.close()
    cf.close()
    print("Wrote manifest to", out_manifest)
    print("Wrote chunk map to", out_chunk_map)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mapping", default="src/memlog/dataset_to_embedding_mapping_refined.ndjson")
    ap.add_argument("--out-manifest", default="src/memlog/embeddings_manifest.ndjson")
    ap.add_argument("--out-chunk-map", default="src/memlog/chunk_index_dataset_range_map.ndjson")
    args = ap.parse_args()

    emb_paths, basename_to_datasets = build_indices(args.mapping)
    print(f"Found {len(emb_paths)} unique embeddings in mapping")
    inspect_embeddings(emb_paths, basename_to_datasets, args.out_manifest, args.out_chunk_map)


if __name__ == "__main__":
    main()
