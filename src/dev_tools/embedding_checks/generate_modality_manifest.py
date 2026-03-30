#!/usr/bin/env python3
"""Build a manifest of dataset paths for a specific modality.

The manifest can be consumed by embedding generation runners to process only the
unmapped entries for a modality. It streams the mapping file to avoid high memory
usage and writes one JSON object per line with at minimum a ``dataset`` field.
"""
from __future__ import annotations

import argparse
import json
from collections.abc import Iterable
from datetime import datetime
from pathlib import Path


def stream_ndjson(path: Path) -> Iterable[dict]:
    with path.open("r", encoding="utf-8") as handle:
        for raw in handle:
            raw = raw.strip()
            if not raw:
                continue
            try:
                yield json.loads(raw)
            except json.JSONDecodeError:
                try:
                    payload = json.loads(raw)
                except Exception:
                    continue
                if isinstance(payload, list):
                    for item in payload:
                        if isinstance(item, dict):
                            yield item


def detect_modality(dataset_path: str) -> str:
    parts = [segment for segment in dataset_path.replace("\\", "/").split("/") if segment]
    for index, segment in enumerate(parts):
        if segment.lower() == "datasets" and index + 1 < len(parts):
            return parts[index + 1]
    if parts and parts[0].endswith(":") and len(parts) > 1:
        return parts[1]
    return parts[0] if parts else "<root>"


def build_manifest(mapping_path: Path, modality: str, include_mapped: bool, limit: int | None,
                   dedupe: bool) -> list[dict]:
    manifest: list[dict] = []
    seen: set[str] = set()

    for record in stream_ndjson(mapping_path):
        dataset = record.get("dataset") or record.get("file")
        if not dataset:
            continue

        if detect_modality(dataset) != modality:
            continue

        embeddings = record.get("embeddings") or []

        if not include_mapped and embeddings:
            continue

        if dedupe and dataset in seen:
            continue

        manifest.append({
            "dataset": dataset,
            "has_embeddings": bool(embeddings),
            "embeddings": embeddings
        })
        seen.add(dataset)

        if limit and len(manifest) >= limit:
            break

    return manifest


def write_manifest(entries: list[dict], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as handle:
        for entry in entries:
            handle.write(json.dumps(entry) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a modality-specific dataset manifest")
    parser.add_argument("--mapping", default="src/memlog/dataset_to_embedding_mapping_refined2.ndjson",
                        help="Path to the dataset-to-embedding mapping NDJSON")
    parser.add_argument("--modality", required=True, help="Modality name to extract (e.g. text, audio, vision)")
    parser.add_argument("--out", help="Output manifest path (defaults to src/memlog/<modality>_embedding_manifest_<timestamp>.jsonl)")
    parser.add_argument("--include-mapped", action="store_true", help="Include entries that already have embeddings")
    parser.add_argument("--limit", type=int, help="Optional maximum number of records to write")
    parser.add_argument("--no-dedupe", action="store_true", help="Do not deduplicate dataset paths")
    args = parser.parse_args()

    mapping_path = Path(args.mapping)
    if not mapping_path.exists():
        raise FileNotFoundError(f"Mapping file not found: {mapping_path}")

    if args.out:
        out_path = Path(args.out)
    else:
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        out_path = Path(f"src/memlog/{args.modality}_embedding_manifest_{timestamp}.jsonl")

    manifest_entries = build_manifest(mapping_path, args.modality, args.include_mapped, args.limit,
                                      dedupe=not args.no_dedupe)

    if not manifest_entries:
        print("No entries matched the requested modality")
        return 1

    write_manifest(manifest_entries, out_path)

    print(f"Wrote {len(manifest_entries)} entries to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
