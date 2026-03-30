#!/usr/bin/env python3
"""Generate a text corpus for tokenizer training from conversation manifests."""

from __future__ import annotations

import argparse
import json
from collections.abc import Iterable
from pathlib import Path


def _load_text_directory(directory: Path) -> list[str]:
    entries: list[str] = []
    if not directory.exists():
        return entries

    for file_path in directory.rglob("*.txt"):
        try:
            content = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            content = file_path.read_text(encoding="latin-1")
        except Exception:
            continue

        for line in content.splitlines():
            if line.strip():
                entries.append(line.strip())

    return entries


def _load_manifest(path: Path) -> list[str]:
    entries: list[str] = []
    if not path.exists():
        return entries

    with path.open("r", encoding="utf-8") as handle:
        try:
            data = json.load(handle)
        except json.JSONDecodeError as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(f"Failed to parse manifest {path}: {exc}") from exc

    for record in data:
        text_fields = [
            record.get("user_input"),
            record.get("assistant_response"),
            record.get("text"),
        ]
        for field in text_fields:
            if isinstance(field, str) and field.strip():
                entries.append(field.strip())

    return entries


def build_corpus(
    manifest_paths: Iterable[Path],
    output_path: Path,
    supplemental_dirs: Iterable[Path] | None = None,
) -> None:
    collected: list[str] = []
    for manifest in manifest_paths:
        collected.extend(_load_manifest(manifest))

    if supplemental_dirs:
        for directory in supplemental_dirs:
            collected.extend(_load_text_directory(directory))

    # Deduplicate while preserving order
    seen = set()
    unique_lines: list[str] = []
    for line in collected:
        if line not in seen:
            seen.add(line)
            unique_lines.append(line)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        for line in unique_lines:
            handle.write(line + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build tokenizer corpus from manifests")
    parser.add_argument(
        "--manifests",
        nargs="+",
        type=Path,
        required=True,
        help="Paths to JSON manifest files",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Destination corpus file",
    )
    parser.add_argument(
        "--text-dirs",
        nargs="*",
        type=Path,
        default=[],
        help="Supplemental directories containing plain-text files",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    build_corpus(args.manifests, args.output, args.text_dirs)


if __name__ == "__main__":
    main()
