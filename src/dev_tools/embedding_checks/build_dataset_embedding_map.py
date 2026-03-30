"""
Build a mapping from dataset files to embedding files.

Strategy:
- Prefer loading existing embedding catalog JSON files found under the embeddings root (contains lists of .npy paths).
- If none are found, the script can perform a full scan of the embeddings root when run with --full-scan (off by default).

Output is written as NDJSON to `--output` (default: `src/memlog/dataset_to_embedding_mapping.ndjson`).

This script is conservative by default to avoid walking huge folders unless explicitly requested.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict
from collections.abc import Iterable

DEFAULT_DATASET_CATALOG = "src/memlog/dataset_catalog_20250829.json"
DEFAULT_EMBEDDINGS_ROOT = os.path.join("F:", "data", "embeddings")
DEFAULT_OUTPUT = "src/memlog/dataset_to_embedding_mapping.ndjson"


def iter_json_lines(path: str):
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


def discover_embedding_catalogs(root: str) -> list[str]:
    catalogs = []
    if not os.path.exists(root):
        return catalogs
    # look for files with 'catalog' in name under root (one-level search)
    for dirpath, _dirnames, filenames in os.walk(root):
        for fn in filenames:
            if "catalog" in fn.lower() and fn.lower().endswith(".json"):
                catalogs.append(os.path.join(dirpath, fn))
        # limit search depth: avoid deep walk; only top-level and one level deeper
        # stop after first directory iteration to avoid full recursion
        break
    # also check directly under root
    for fn in os.listdir(root) if os.path.exists(root) else []:
        p = os.path.join(root, fn)
        if os.path.isfile(p) and "catalog" in fn.lower() and fn.lower().endswith(".json") and p not in catalogs:
            catalogs.append(p)
    return catalogs


def load_embedding_paths_from_catalogs(catalog_paths: Iterable[str]) -> list[str]:
    out = []
    for p in catalog_paths:
        if not os.path.exists(p):
            continue
        try:
            for obj in iter_json_lines(p):
                # attempt to find path fields
                if isinstance(obj, str):
                    out.append(obj)
                    continue
                for k in ("path", "full_path", "file_path", "filepath", "name"):
                    if k in obj and isinstance(obj[k], str):
                        out.append(obj[k])
                        break
        except Exception:
            continue
    # normalize separators
    normed = [s.replace("/", os.sep).replace("\\", os.sep) for s in out]
    return normed


def scan_embeddings_root(root: str) -> list[str]:
    if not os.path.exists(root):
        return []
    result = []
    for dirpath, _dirnames, filenames in os.walk(root):
        for fn in filenames:
            if fn.lower().endswith(".npy"):
                result.append(os.path.join(dirpath, fn))
    return result


def dataset_entries_from_catalog(path: str):
    if not os.path.exists(path):
        return
    yield from iter_json_lines(path)


def extract_path_from_entry(obj) -> str | None:
    for k in ("path", "full_path", "filePath", "file_path", "filepath", "name"):
        if k in obj and isinstance(obj[k], str):
            return obj[k]
    # fallback: try combine
    if "top_level" in obj and "relative_path" in obj:
        return os.path.join(obj.get("top_level"), obj.get("relative_path"))
    return None


def build_basename_index(embedding_paths: Iterable[str]) -> dict[str, list[str]]:
    idx = defaultdict(list)
    for p in embedding_paths:
        bn = os.path.basename(p)
        name_no_ext = os.path.splitext(bn)[0]
        idx[name_no_ext].append(p)
    return idx


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    p = argparse.ArgumentParser()
    p.add_argument("--dataset-catalog", default=DEFAULT_DATASET_CATALOG)
    p.add_argument("--embeddings-root", default=DEFAULT_EMBEDDINGS_ROOT)
    p.add_argument("--embeddings-catalogs", nargs="*", default=None, help="explicit embedding catalog JSON files to use (skips discovery)")
    p.add_argument("--output", default=DEFAULT_OUTPUT)
    p.add_argument("--full-scan", action="store_true", help="perform a full scan of embeddings root if no catalogs found (slow)")
    args = p.parse_args(argv)

    print(f"Dataset catalog: {args.dataset_catalog}")
    print(f"Embeddings root: {args.embeddings_root}")
    print(f"Output NDJSON: {args.output}")

    # discover embedding catalogs
    catalogs = args.embeddings_catalogs or discover_embedding_catalogs(args.embeddings_root)

    embedding_paths = []
    if catalogs:
        print(f"Loading embedding paths from {len(catalogs)} catalog(s)")
        embedding_paths = load_embedding_paths_from_catalogs(catalogs)
    else:
        print("No embedding catalogs found under embeddings root.")
        if args.full_scan:
            print("Performing full scan of embeddings root (this may take a while)...")
            embedding_paths = scan_embeddings_root(args.embeddings_root)
        else:
            print("Run with --full-scan to allow a full directory walk of the embeddings root.")

    print(f"Embedding paths collected: {len(embedding_paths)}")

    # build basename index
    basename_index = build_basename_index(embedding_paths)

    # open output
    out_dir = os.path.dirname(args.output)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    mapped = 0
    total = 0
    with open(args.output, "w", encoding="utf-8") as outf:
        for obj in dataset_entries_from_catalog(args.dataset_catalog):
            total += 1
            ds_path = extract_path_from_entry(obj)
            if not ds_path:
                continue
            # normalize
            ds_norm = ds_path.replace("/", os.sep).replace("\\", os.sep)

            found = []
            # heuristic 1: basename match
            base = os.path.splitext(os.path.basename(ds_norm))[0]
            if base in basename_index:
                found = basename_index[base][:]

            # heuristic 2: try replace datasets root with embeddings root and change extension to .npy
            if not found:
                try:
                    if ds_norm.startswith(os.path.join("F:", "data", "datasets")):
                        rel = os.path.relpath(ds_norm, os.path.join("F:", "data", "datasets"))
                        candidate = os.path.join(args.embeddings_root, rel)
                        candidate = os.path.splitext(candidate)[0] + ".npy"
                        if os.path.exists(candidate):
                            found.append(candidate)
                except Exception:
                    pass

            # heuristic 3: find any embedding path that contains the dataset base as substring
            if not found and embedding_paths:
                for pth in basename_index:
                    if base in pth:
                        found.extend(basename_index[pth])
                        break

            record = {"dataset": ds_norm, "embeddings": found, "mapped": bool(found)}
            outf.write(json.dumps(record) + "\n")
            if found:
                mapped += 1

    print(f"Wrote mapping for {total} dataset entries; mapped={mapped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
