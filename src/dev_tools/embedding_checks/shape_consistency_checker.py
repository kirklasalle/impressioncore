"""
Shape consistency checker for .npy embeddings

Scans the repository's line-delimited dataset catalog(s) and inspects up to --limit .npy files,
using numpy mmap_mode='r' to avoid loading arrays into memory.

Outputs a compact JSON report of unique (shape, dtype) observed with a representative example
path and counts per unique signature.

Usage:
  python src/dev_tools/embedding_checks/shape_consistency_checker.py --limit 1000 --output src/memlog/embedding_shape_report.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from collections import defaultdict
from collections.abc import Iterator

CATALOG_PATHS = [
    "src/memlog/dataset_catalog_20250829.json",
    "src/memlog/dataset_catalog.json",
]


def iter_catalog_lines(path: str) -> Iterator[dict]:
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except Exception:
                try:
                    data = json.loads(line)
                    if isinstance(data, list):
                        yield from data
                except Exception:
                    continue


def find_npy_paths(limit: int) -> list[str]:
    results: list[str] = []
    for p in CATALOG_PATHS:
        if not os.path.exists(p):
            continue
        for obj in iter_catalog_lines(p):
            candidate = None
            for k in ("path", "full_path", "filePath", "file_path", "filepath", "name"):
                if k in obj:
                    candidate = obj[k]
                    break
            if candidate is None and "top_level" in obj and "relative_path" in obj:
                candidate = os.path.join(obj.get("top_level"), obj.get("relative_path"))
            if not candidate:
                continue
            if isinstance(candidate, str) and candidate.lower().endswith(".npy"):
                norm = candidate.replace("/", os.sep).replace("\\", os.sep)
                results.append(norm)
                if len(results) >= limit:
                    return results
    return results


def inspect_npy(path: str):
    import numpy as np

    try:
        arr = np.load(path, mmap_mode="r")
        return getattr(arr, "shape", None), getattr(arr, "dtype", None), None
    except Exception as e:
        return None, None, str(e)


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    p = argparse.ArgumentParser()
    p.add_argument("--limit", type=int, default=1000, help="maximum number of .npy files to inspect")
    p.add_argument("--output", type=str, default="src/memlog/embedding_shape_report.json", help="output report path")
    args = p.parse_args(argv)

    paths = find_npy_paths(args.limit)
    if not paths:
        print("No .npy files found in known catalog paths. Check CATALOG_PATHS inside the script.")
        return 2

    report = {"inspected": 0, "unique": {}, "errors": []}
    counts = defaultdict(int)
    examples: dict[str, str] = {}

    for path in paths:
        report["inspected"] += 1
        path_abs = os.path.abspath(os.path.join(os.getcwd(), path)) if not os.path.isabs(path) else path
        if not os.path.exists(path_abs):
            report["errors"].append({"path": path_abs, "error": "missing"})
            continue
        shape, dtype, err = inspect_npy(path_abs)
        if err:
            report["errors"].append({"path": path_abs, "error": err})
            continue
        key = f"shape={shape}|dtype={dtype}"
        counts[key] += 1
        if key not in examples:
            examples[key] = path_abs

    unique = []
    for k, cnt in counts.items():
        # split to fields
        try:
            left, right = k.split("|", 1)
            left.replace("shape=", "")
            right.replace("dtype=", "")
        except Exception:
            pass
        unique.append({"signature": k, "count": cnt, "example": examples.get(k)})

    report["unique"] = unique
    report["timestamp"] = time.strftime("%Y-%m-%dT%H:%M:%S")

    out_dir = os.path.dirname(args.output)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    with open(args.output, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)

    print(f"Wrote report to {args.output}; inspected={report['inspected']}; unique_signatures={len(unique)}; errors={len(report['errors'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
