#!/usr/bin/env python3
"""Run the B3 embedding processor on a manifest of dataset file paths."""
import argparse
import asyncio
import json
import random
import sys
from pathlib import Path
from typing import List

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.core.initialization.b3_full_embedding_processor import B3EmbeddingProcessor


def load_manifest(manifest_path: Path, path_field: str, limit: int | None, shuffle: bool) -> List[Path]:
    entries: List[Path] = []
    with manifest_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                continue
            value = payload.get(path_field)
            if not value:
                continue
            entries.append(Path(value))
            if limit and len(entries) >= limit:
                break

    if shuffle:
        random.shuffle(entries)

    return entries


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Execute embedding generation against a manifest")
    parser.add_argument("--manifest", required=True, help="Path to the JSONL manifest produced by generate_modality_manifest")
    parser.add_argument("--phase-name", default="manifest_run", help="Name used for logging and saved artifacts")
    parser.add_argument("--path-field", default="dataset", help="Field in each manifest record that contains the file path")
    parser.add_argument("--limit", type=int, help="Maximum number of paths to process")
    parser.add_argument("--shuffle", action="store_true", help="Shuffle paths before processing to distribute workload")
    return parser.parse_args()


async def run_manifest(args: argparse.Namespace) -> bool:
    manifest_path = Path(args.manifest)
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest not found: {manifest_path}")

    paths = load_manifest(manifest_path, args.path_field, args.limit, args.shuffle)
    if not paths:
        raise RuntimeError("Manifest did not yield any paths to process")

    processor = B3EmbeddingProcessor()
    return await processor.process_file_list(paths, phase_name=args.phase_name)


def main() -> int:
    args = parse_args()
    try:
        success = asyncio.run(run_manifest(args))
    except Exception as exc:
        print(f"Manifest run failed: {exc}")
        return 1
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
