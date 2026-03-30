#!/usr/bin/env python3
"""Generate coverage report, mapped examples, batch-mapping suggestions, and optional FAISS index.

Writes output files under ``src/memlog/``:
- mapping_coverage_by_modality.json
- mapped_examples_50.ndjson
- batch_mapping_suggestions.json
- faiss_sample.index (optional)
- faiss_sample_ids.ndjson (optional)

This script streams the mapping NDJSON to avoid loading large files in memory.
"""
from __future__ import annotations

import argparse
import json
import os
import re
from collections import defaultdict

import numpy as np


def stream_ndjson(path):
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except Exception:
                # try to recover if file contains a JSON array
                try:
                    arr = json.loads(line)
                    if isinstance(arr, list):
                        yield from arr
                except Exception:
                    continue


def top_level_dir(path: str) -> str:
    # normalize and get first component after drive/root
    p = path.replace("\\", "/")
    parts = [p for p in p.split("/") if p]
    # if path starts with a drive like F:, the first part may be 'F:'
    if parts and parts[0].endswith(":") and len(parts) > 1:
        return parts[1]
    return parts[0] if parts else "<root>"


def detect_modality_from_dataset_path(path: str) -> str:
    # Expect paths like F:/data/datasets/<modality>/... or .../datasets/<modality>/...
    p = path.replace("\\", "/")
    parts = [x for x in p.split("/") if x]
    # find 'datasets' and return the following segment if present
    for i, part in enumerate(parts):
        if part.lower() == "datasets" and i + 1 < len(parts):
            return parts[i + 1]
    # fallback to top-level
    return top_level_dir(path)


CHUNK_RE = re.compile(r"(?P<prefix>.+?)(?:[_\-\.])(?:chunk|part|batch)(?P<idx>\d+)(?:\.|_|$)", re.IGNORECASE)


def detect_batch_pattern(fname: str):
    m = CHUNK_RE.search(os.path.basename(fname))
    if m:
        return m.group("prefix"), int(m.group("idx"))
    return None


def build_coverage_and_examples(mapping_path: str, catalog_path: str | None, examples_out: str, coverage_out: str,
                                suggestions_out: str, examples_limit: int = 50, aggressive: bool = False):
    totals = defaultdict(int)
    mapped = defaultdict(int)
    modality_totals = defaultdict(int)
    modality_mapped = defaultdict(int)
    examples = []
    suggestions = []

    # If a small dataset catalog summary exists, read totals per top-level
    summary = {}
    if catalog_path and os.path.exists(catalog_path):
        try:
            with open(catalog_path, encoding="utf-8") as f:
                summary = json.load(f)
        except Exception:
            summary = {}

    # stream mapping ndjson
    for rec in stream_ndjson(mapping_path):
        ds = rec.get("dataset") or rec.get("file") or ""
        tl = top_level_dir(ds)
        totals[tl] += 1
        modality = detect_modality_from_dataset_path(ds)
        modality_totals[modality] += 1
        emb_list = rec.get("embeddings") or []
        if emb_list:
            mapped[tl] += 1
            modality_mapped[modality] += 1
            if len(examples) < examples_limit:
                examples.append({"dataset": ds, "embeddings": emb_list})

        # inspect embedding filenames for batch patterns and collect suggestions
        for e in emb_list:
            bp = detect_batch_pattern(e)
            if bp:
                prefix, idx = bp
                suggestions.append({"embedding": e, "prefix": prefix, "index": idx, "dataset_example_prefix": prefix})
            elif aggressive:
                # looser heuristic: look for numeric suffixes separated by underscores
                name = os.path.basename(e)
                m = re.search(r"(?P<prefix>.+?)[_\-\.](?P<idx>\d{2,5})(?:\.|_|$)", name)
                if m:
                    prefix = m.group("prefix")
                    try:
                        idx = int(m.group("idx"))
                    except Exception:
                        idx = 0
                    suggestions.append({"embedding": e, "prefix": prefix, "index": idx, "dataset_example_prefix": prefix, "heuristic": "aggressive"})

    # Combine totals with summary if available for missing modalities
    if summary and "by_top_level_dir" in summary:
        for k, v in summary["by_top_level_dir"].items():
            if k not in totals:
                totals[k] = v

    coverage = {}
    for k in sorted(totals.keys()):
        coverage[k] = {"total": int(totals[k]), "mapped": int(mapped.get(k, 0)), "mapped_pct": 0.0}
        if totals[k] > 0:
            coverage[k]["mapped_pct"] = round(100.0 * coverage[k]["mapped"] / totals[k], 4)

    # modality coverage
    modality_coverage = {}
    for m in sorted(modality_totals.keys()):
        modality_coverage[m] = {"total": int(modality_totals[m]), "mapped": int(modality_mapped.get(m, 0)), "mapped_pct": 0.0}
        if modality_totals[m] > 0:
            modality_coverage[m]["mapped_pct"] = round(100.0 * modality_coverage[m]["mapped"] / modality_totals[m], 4)

    # write outputs
    os.makedirs(os.path.dirname(coverage_out), exist_ok=True)
    with open(coverage_out, "w", encoding="utf-8") as f:
        json.dump({"coverage": coverage, "modality_coverage": modality_coverage}, f, indent=2)

    with open(examples_out, "w", encoding="utf-8") as f:
        for ex in examples:
            f.write(json.dumps(ex) + "\n")

    with open(suggestions_out, "w", encoding="utf-8") as f:
        json.dump({"suggestions_count": len(suggestions), "suggestions": suggestions[:500]}, f, indent=2)

    return coverage, examples, suggestions


def export_markdown_report(coverage: dict, modality_coverage: dict, out_md: str):
    lines = []
    lines.append("# Coverage summary")
    lines.append("")
    lines.append("## Top-level coverage")
    lines.append("")
    for k, v in coverage.items():
        lines.append(f"- **{k}** — {v['mapped']} / {v['total']} ({v['mapped_pct']}%)")
    lines.append("")
    lines.append("## Modality coverage")
    lines.append("")
    for m, v in modality_coverage.items():
        lines.append(f"- **{m}** — {v['mapped']} / {v['total']} ({v['mapped_pct']}%)")

    os.makedirs(os.path.dirname(out_md), exist_ok=True)
    with open(out_md, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def build_faiss_index(mapping_path: str, out_index: str, out_ids: str, sample_size: int = 2000, metric: str = "l2"):
    try:
        import faiss
    except Exception as e:
        print("faiss not available:", e)
        return False

    # collect candidate embedding paths (mapping where embeddings list non-empty)
    candidates = []
    for rec in stream_ndjson(mapping_path):
        emb_list = rec.get("embeddings") or []
        if emb_list:
            for e in emb_list:
                candidates.append(e)
        if len(candidates) >= sample_size:
            break

    if not candidates:
        print("No candidate embeddings found to build FAISS index.")
        return False

    # determine most common dimension among a small prefix of candidates
    dim_counts: dict[int, int] = {}
    dims_for_path: dict[str, int] = {}
    preview = candidates[: min(len(candidates), 2000)]
    for p in preview:
        try:
            a = np.load(p, mmap_mode="r")
        except Exception:
            continue
        if a.ndim == 2:
            d = a.shape[1]
        elif a.ndim == 1:
            d = a.shape[0]
        else:
            d = int(np.prod(a.shape))
        dims_for_path[p] = d
        dim_counts[d] = dim_counts.get(d, 0) + 1

    if not dim_counts:
        print("No usable embeddings found among candidates")
        return False

    # choose the most common dim
    chosen_dim = max(dim_counts.items(), key=lambda x: x[1])[0]
    print(f"Chosen embedding dimension for FAISS index: {chosen_dim} (counts: {dim_counts.get(chosen_dim)})")

    # filter candidates to those matching chosen_dim
    matching = [p for p in candidates if dims_for_path.get(p) == chosen_dim]
    skipped = len(candidates) - len(matching)
    if not matching:
        print("No matching embeddings with chosen dimension found.")
        return False

    to_take = min(sample_size, len(matching))
    X = np.zeros((to_take, chosen_dim), dtype=np.float32)
    ids = []
    loaded = 0
    for _i, p in enumerate(matching[:to_take]):
        try:
            a = np.load(p, mmap_mode="r")
        except Exception:
            continue
        if a.ndim == 2:
            v = a.mean(axis=0)
        elif a.ndim == 1:
            v = a
        else:
            v = a.reshape(-1)
        v = np.asarray(v, dtype=np.float32).reshape(-1)
        if v.size < chosen_dim:
            # pad with zeros
            vv = np.zeros((chosen_dim,), dtype=np.float32)
            vv[: v.size] = v
            v = vv
        elif v.size > chosen_dim:
            v = v[:chosen_dim]
        X[loaded] = v
        ids.append({"id": loaded, "path": p})
        loaded += 1
    if loaded < to_take:
        X = X[:loaded]
        # reassign ids to match loaded
        ids = ids[:loaded]

    # build index
    index = faiss.IndexFlatIP(chosen_dim) if metric.lower() == "ip" else faiss.IndexFlatL2(chosen_dim)
    index.add(X)
    faiss.write_index(index, out_index)

    with open(out_ids, "w", encoding="utf-8") as f:
        for rec in ids:
            f.write(json.dumps(rec) + "\n")

    print(f"FAISS: wrote index with {len(ids)} vectors (skipped {skipped} candidates)")
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mapping", default="src/memlog/dataset_to_embedding_mapping.ndjson")
    ap.add_argument("--catalog-summary", default="src/memlog/dataset_catalog_summary_20250829.json")
    ap.add_argument("--examples-out", default="src/memlog/mapped_examples_50.ndjson")
    ap.add_argument("--coverage-out", default="src/memlog/mapping_coverage_by_modality.json")
    ap.add_argument("--suggestions-out", default="src/memlog/batch_mapping_suggestions.json")
    ap.add_argument("--examples", type=int, default=50)
    ap.add_argument("--build-faiss", action="store_true")
    ap.add_argument("--faiss-sample", type=int, default=2000)
    ap.add_argument("--faiss-index-out", default="src/memlog/faiss_sample.index")
    ap.add_argument("--faiss-ids-out", default="src/memlog/faiss_sample_ids.ndjson")
    ap.add_argument("--aggressive-heuristics", dest="aggressive", action="store_true", help="Run an additional aggressive filename heuristic pass to infer batch/chunk prefixes")
    ap.add_argument("--export-md", nargs='?', const="src/memlog/mapping_coverage_summary.md", help="Export a compact markdown coverage summary (optional filename)")
    args = ap.parse_args()

    mapping_path = args.mapping
    if not os.path.exists(mapping_path):
        print("Mapping file not found:", mapping_path)
        return 2

    coverage, examples, suggestions = build_coverage_and_examples(mapping_path, args.catalog_summary,
                                                                  args.examples_out, args.coverage_out,
                                                                  args.suggestions_out, args.examples, aggressive=args.aggressive)

    print("Wrote coverage to", args.coverage_out)
    print("Wrote examples to", args.examples_out)
    print("Wrote suggestions to", args.suggestions_out)

    if args.build_faiss:
        ok = build_faiss_index(mapping_path, args.faiss_index_out, args.faiss_ids_out, args.faiss_sample)
        if ok:
            print("FAISS index written to", args.faiss_index_out)
        else:
            print("FAISS index build failed or faiss not available.")

    # optional markdown export
    if args.export_md:
        try:
            md_out = args.export_md if isinstance(args.export_md, str) and args.export_md else "src/memlog/mapping_coverage_summary.md"
            # open the coverage file we just wrote
            try:
                with open(args.coverage_out, encoding="utf-8") as f:
                    cov_json = json.load(f)
            except Exception:
                cov_json = {"coverage": {}, "modality_coverage": {}}
            export_markdown_report(cov_json.get("coverage", {}), cov_json.get("modality_coverage", {}), md_out)
            print("Wrote markdown coverage summary to", md_out)
        except Exception as e:
            print("Failed to write markdown export:", e)


if __name__ == "__main__":
    main()
