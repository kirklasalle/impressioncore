#!/usr/bin/env python3
"""Improve chunk heuristics by scanning the embeddings manifest and attempting stronger prefix+chunk -> dataset mappings.

Writes:
- src/memlog/chunk_index_dataset_range_map_improved.ndjson
- src/memlog/dataset_to_embedding_mapping_refined2.ndjson

This is a best-effort script; it attempts to mark many chunked embedding files as exact_1to1 when candidates match rows.
"""
from __future__ import annotations

import json
import os
import re
import sys
from collections import defaultdict

CHUNK_RE = re.compile(r"(?P<prefix>.+?)[_\-\.]chunk(?P<chunk>\d+)(?:[_\-\.]|$)", re.IGNORECASE)


def stream_ndjson(path: str):
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def load_embeddings_manifest(path: str):
    entries = []
    for rec in stream_ndjson(path):
        entries.append(rec)
    return entries


def build_prefix_index(emb_manifest):
    by_prefix = defaultdict(list)
    for rec in emb_manifest:
        emb = rec.get("embedding")
        m = CHUNK_RE.search(os.path.basename(emb)) if emb else None
        if m:
            prefix = m.group("prefix")
            chunk = int(m.group("chunk"))
            rec_meta = {"embedding": emb, "prefix": prefix, "chunk": chunk, "rows": rec.get("rows", 1)}
            by_prefix[prefix].append(rec_meta)
    # sort by chunk
    for p in list(by_prefix.keys()):
        by_prefix[p] = sorted(by_prefix[p], key=lambda x: x["chunk"])
    return by_prefix


def find_dataset_candidates(mapping_path: str):
    # build basename -> dataset path index
    basename_index = defaultdict(list)
    for rec in stream_ndjson(mapping_path):
        ds = rec.get("dataset")
        if not ds:
            continue
        b = os.path.splitext(os.path.basename(ds))[0]
        basename_index[b].append(ds)
    return basename_index


def improve(prefix_index: dict[str, list[dict]], basename_index: dict[str, list[str]]):
    improved_records = []
    refined_mapping_changes = 0
    for prefix, emb_list in prefix_index.items():
        # build candidate dataset list by searching basenames containing prefix
        candidates = []
        for b, paths in basename_index.items():
            if prefix in b:
                candidates.extend(paths)
        candidates = sorted(set(candidates))
        # attempt to align embeddings to candidate datasets
        # if total candidate count equals sum(rows) across emb_list and ordering seems consistent, mark exact
        total_rows = sum(e.get("rows", 1) for e in emb_list)
        if len(candidates) == total_rows and total_rows > 0:
            # assign sequentially
            idx = 0
            for e in emb_list:
                rows = int(e.get("rows", 1))
                assigned = candidates[idx: idx + rows]
                idx += rows
                improved_records.append({"embedding": e["embedding"], "rows": rows, "mapped_type": "exact_1to1", "dataset_paths": assigned})
                refined_mapping_changes += rows
        else:
            # try per-embedding chunk match by chunk number in candidate basenames
            for e in emb_list:
                cnum = e.get("chunk")
                rows = int(e.get("rows", 1))
                found = [p for p in candidates if f"chunk{cnum}" in os.path.splitext(os.path.basename(p))[0]]
                if len(found) == rows and rows > 0:
                    improved_records.append({"embedding": e["embedding"], "rows": rows, "mapped_type": "exact_1to1", "dataset_paths": found})
                    refined_mapping_changes += rows
                elif len(found) >= rows and rows > 0:
                    improved_records.append({"embedding": e["embedding"], "rows": rows, "mapped_type": "best_effort_prefix_ordered", "dataset_paths": found[:rows]})
                    refined_mapping_changes += rows
                else:
                    # fallback: leave as-is but include best-effort candidates
                    improved_records.append({"embedding": e["embedding"], "rows": rows, "mapped_type": "none_found", "dataset_paths": found})
    return improved_records, refined_mapping_changes


def write_improved(improved_records, out_chunk_map, mapping_in, mapping_out):
    # write improved chunk map
    with open(out_chunk_map, "w", encoding="utf-8") as cf:
        for rec in improved_records:
            cf.write(json.dumps(rec) + "\n")

    # apply exact mappings to create a new refined mapping
    # read original mapping and for any dataset that matches dataset_paths, update embeddings field
    dataset_to_embed = {}
    for rec in improved_records:
        emb = rec.get("embedding")
        for ds in rec.get("dataset_paths", []):
            dataset_to_embed[ds.replace("\\", "/")] = emb

    with open(mapping_out, "w", encoding="utf-8") as mo:
        for rec in stream_ndjson(mapping_in):
            ds = rec.get("dataset")
            if not ds:
                mo.write(json.dumps(rec) + "\n")
                continue
            dsn = ds.replace("\\", "/")
            if dsn in dataset_to_embed:
                newrec = {"dataset": ds, "embeddings": [dataset_to_embed[dsn]]}
                mo.write(json.dumps(newrec) + "\n")
            else:
                mo.write(json.dumps(rec) + "\n")


def main():
    emb_manifest = "src/memlog/embeddings_manifest.ndjson"
    mapping_in = "src/memlog/dataset_to_embedding_mapping_refined.ndjson"
    out_chunk_map = "src/memlog/chunk_index_dataset_range_map_improved.ndjson"
    mapping_out = "src/memlog/dataset_to_embedding_mapping_refined2.ndjson"
    if len(sys.argv) > 1:
        emb_manifest = sys.argv[1]
    if len(sys.argv) > 2:
        mapping_in = sys.argv[2]

    emb_entries = load_embeddings_manifest(emb_manifest)
    prefix_index = build_prefix_index(emb_entries)
    basename_index = find_dataset_candidates(mapping_in)
    improved_records, changes = improve(prefix_index, basename_index)
    write_improved(improved_records, out_chunk_map, mapping_in, mapping_out)
    print(f"Wrote improved chunk map to {out_chunk_map} and refined mapping to {mapping_out}; changes={changes}")


if __name__ == "__main__":
    main()
