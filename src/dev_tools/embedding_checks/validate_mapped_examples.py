#!/usr/bin/env python3
"""Validate the mapped examples NDJSON: check embedding file exists and inspect shape/dtype/size."""
from __future__ import annotations

import json
import os
import sys

import numpy as np


def stream_ndjson(path):
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def validate(in_path: str, out_path: str):
    results: list[dict] = []
    for rec in stream_ndjson(in_path):
        ds = rec.get("dataset")
        emb = rec.get("embeddings") or []
        entry = {"dataset": ds, "embeddings": []}
        for e in emb:
            info = {"path": e, "exists": False}
            # normalize path (many embeddings use 'F:data\' style from earlier tooling)
            p = e
            if p.startswith("F:data"):
                p = p.replace("F:data", "F:/data")
            if os.path.exists(p):
                info["exists"] = True
                try:
                    a = np.load(p, mmap_mode="r")
                    info.update({"shape": a.shape, "dtype": str(a.dtype), "bytes": os.path.getsize(p)})
                except Exception as ex:
                    info.update({"error": str(ex)})
            else:
                info["note"] = "path_not_found"
            entry["embeddings"].append(info)
        results.append(entry)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print("Wrote validated examples to", out_path)


def main():
    in_path = "src/memlog/mapped_examples_50.ndjson"
    out_path = "src/memlog/mapped_examples_50_validated.json"
    if len(sys.argv) > 1:
        in_path = sys.argv[1]
    if len(sys.argv) > 2:
        out_path = sys.argv[2]
    validate(in_path, out_path)


if __name__ == "__main__":
    main()
