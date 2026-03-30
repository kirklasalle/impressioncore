#!/usr/bin/env python3
"""Refine the dataset->embedding mapping by using batch/chunk filename prefixes and mapping ranges.

This script reads the existing mapping NDJSON, reads `batch_mapping_suggestions.json`,
and for each suggestion attempts to map unmapped dataset entries that match the prefix.
It writes a new NDJSON mapping file with additional inferred mappings (tagged as "inferred").
"""
from __future__ import annotations

import json
import os
import sys


def load_suggestions(path: str):
    with open(path, encoding="utf-8") as f:
        return json.load(f).get("suggestions", [])


def stream_ndjson(path: str):
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def basename_noext(p: str) -> str:
    return os.path.splitext(os.path.basename(p))[0]


def refine(mapping_in: str, suggestions_in: str, mapping_out: str):
    suggestions = load_suggestions(suggestions_in)
    # group suggestions by prefix -> list of embedding paths
    by_prefix: dict[str, list[str]] = {}
    for s in suggestions:
        pref = s.get("prefix")
        emb = s.get("embedding")
        if pref and emb:
            by_prefix.setdefault(pref, []).append(emb)

    out_f = open(mapping_out, "w", encoding="utf-8")
    added = 0
    for rec in stream_ndjson(mapping_in):
        ds = rec.get("dataset")
        emb_list = rec.get("embeddings") or []
        if emb_list:
            out_f.write(json.dumps(rec) + "\n")
            continue
        # attempt prefix match on basename of dataset
        b = basename_noext(ds)
        matched = False
        for pref, emb_paths in by_prefix.items():
            if b.startswith(pref) or pref in b:
                # attach first embedding for this prefix as inferred
                rec2 = {"dataset": ds, "embeddings": [emb_paths[0]], "inferred": True}
                out_f.write(json.dumps(rec2) + "\n")
                added += 1
                matched = True
                break
        if not matched:
            out_f.write(json.dumps(rec) + "\n")

    out_f.close()
    print(f"Wrote refined mapping to {mapping_out}; added inferred mappings={added}")


def main():
    mapping_in = "src/memlog/dataset_to_embedding_mapping.ndjson"
    suggestions_in = "src/memlog/batch_mapping_suggestions.json"
    mapping_out = "src/memlog/dataset_to_embedding_mapping_refined.ndjson"
    if len(sys.argv) > 1:
        mapping_in = sys.argv[1]
    if len(sys.argv) > 2:
        suggestions_in = sys.argv[2]
    if len(sys.argv) > 3:
        mapping_out = sys.argv[3]
    refine(mapping_in, suggestions_in, mapping_out)


if __name__ == "__main__":
    main()
