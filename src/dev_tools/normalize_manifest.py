"""
Normalize an NDJSON manifest: canonicalize keys, convert 'dataset' values that are file paths into 'path'.

Usage:
  python src/dev_tools/normalize_manifest.py --in src/memlog/dataset_to_embedding_training_manifest.ndjson --out src/memlog/dataset_to_embedding_training_manifest.normalized.ndjson
"""
from __future__ import annotations

import argparse
import json
import os


def looks_like_path(s: str) -> bool:
    if not isinstance(s, str):
        return False
    # heuristic: contains a drive letter or separators or file extension
    if os.path.isabs(s):
        return True
    if any(sep in s for sep in ("/", "\\")):
        return True
    return bool(s.endswith(".npy") or s.endswith(".npz") or s.endswith(".txt"))


def normalize_record(rec: dict) -> dict:
    out = dict(rec)
    if "path" not in out and "dataset" in out and looks_like_path(out["dataset"]):
        out["path"] = out["dataset"]
    # further normalizations could go here (e.g., normalize slashes)
    return out


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--in", dest="inpath", required=True)
    p.add_argument("--out", dest="outpath", required=True)
    args = p.parse_args(argv)

    with open(args.inpath, encoding="utf-8") as inf, open(args.outpath, "w", encoding="utf-8") as outf:
        for line in inf:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except Exception:
                continue
            n = normalize_record(rec)
            outf.write(json.dumps(n) + "\n")


if __name__ == "__main__":
    main()
