"""
Sample embedding validator

Reads the line-delimited dataset catalog at `src/memlog/dataset_catalog_20250829.json` (created earlier)
and tries to validate a small sample of `.npy` embedding files by opening them with numpy (mmap_mode='r') to inspect shape and dtype.

This script is intentionally conservative: it never loads arrays fully into memory and will skip files that are inaccessible.

Usage: python src/dev_tools/embedding_checks/sample_embedding_validator.py --sample 20
"""
from __future__ import annotations

import argparse
import json
import os
import sys
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
                # try to parse as a JSON array (fallback)
                try:
                    data = json.loads(line)
                    if isinstance(data, list):
                        yield from data
                except Exception:
                    continue


def find_npy_paths(sample_limit: int) -> list[str]:
    results: list[str] = []
    for p in CATALOG_PATHS:
        if not os.path.exists(p):
            continue
        for obj in iter_catalog_lines(p):
            # Try common keys
            candidate = None
            for k in ("path", "full_path", "filePath", "file_path", "filepath", "name"):
                if k in obj:
                    candidate = obj[k]
                    break
            if candidate is None:
                # attempt to reconstruct
                if "top_level" in obj and "relative_path" in obj:
                    candidate = os.path.join(obj.get("top_level"), obj.get("relative_path"))
            if not candidate:
                continue
            if isinstance(candidate, str) and candidate.lower().endswith(".npy"):
                # normalize
                norm = candidate.replace("/", os.sep).replace("\\", os.sep)
                results.append(norm)
                if len(results) >= sample_limit:
                    return results
    return results


def try_inspect_npy(path: str) -> tuple[bool, str]:
    try:
        import numpy as np
    except Exception as e:
        return False, f"numpy import failed: {e!r}"

    try:
        # use mmap to avoid large memory usage
        arr = np.load(path, mmap_mode="r")
        shp = getattr(arr, "shape", None)
        dt = getattr(arr, "dtype", None)
        return True, f"ok shape={shp} dtype={dt} mode=mmap"
    except Exception as e:
        return False, f"load_failed: {e!r}"


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", "-n", type=int, default=20, help="number of .npy samples to validate")
    args = parser.parse_args(argv)

    sample_paths = find_npy_paths(args.sample)
    if not sample_paths:
        print("No line-delimited catalog found or no .npy entries discovered in the catalog paths:")
        for p in CATALOG_PATHS:
            print(" -", p)
        print("If your catalog is at a different path, pass it or create a small list file with absolute paths.")
        return 2

    print(f"Found {len(sample_paths)} .npy files to inspect (sample limit {args.sample})")

    summary = {"checked": 0, "ok": 0, "fail": 0, "details": []}
    for p in sample_paths:
        summary["checked"] += 1
        if not os.path.isabs(p):
            # try relative to workspace
            p_try = os.path.abspath(os.path.join(os.getcwd(), p))
        else:
            p_try = p
        if not os.path.exists(p_try):
            summary["fail"] += 1
            summary["details"].append({"path": p_try, "status": "missing"})
            print(f"MISSING: {p_try}")
            continue
        ok, msg = try_inspect_npy(p_try)
        if ok:
            summary["ok"] += 1
            print(f"OK: {p_try} -> {msg}")
            summary["details"].append({"path": p_try, "status": "ok", "note": msg})
        else:
            summary["fail"] += 1
            print(f"FAIL: {p_try} -> {msg}")
            summary["details"].append({"path": p_try, "status": "fail", "note": msg})

    print("\nSUMMARY:")
    print(json.dumps({k: summary[k] for k in ("checked", "ok", "fail")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
