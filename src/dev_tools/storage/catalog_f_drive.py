"""F: drive cataloguing utility.

This script walks a target directory (defaults to the root of F:/) and collects
metadata for each file or subdirectory. It can either write the catalogue to a
CSV file or emit a preview of the first *n* entries to stdout for quick checks.

The script intentionally keeps memory usage low so it can scale to the full
476GB ImpressionCore storage tree. It streams entries incrementally rather than
loading entire directory listings into memory.

Example preview:
    python src/dev_tools/storage/catalog_f_drive.py --root F:/data/datasets --limit 50 --preview 10 --summary

Example full export:
    python src/dev_tools/storage/catalog_f_drive.py --output F:/catalogs/f_drive_catalog_20251108.csv
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
from collections import deque
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class Entry:
    """Catalogued filesystem entry."""

    path: Path
    is_dir: bool
    size: int
    modified: datetime

    def to_row(self, root: Path) -> list[str]:
        """Return a CSV row relative to *root*."""
        rel_path = self.path.relative_to(root)
        return [
            str(rel_path),
            "directory" if self.is_dir else "file",
            str(self.size),
            self.modified.isoformat(timespec="seconds"),
        ]


def iter_entries(root: Path, limit: int | None = None) -> Iterator[Entry]:
    """Yield entries breadth-first from *root* up to *limit* items."""

    queue: deque[Path] = deque([root])
    count = 0

    while queue:
        current = queue.popleft()
        try:
            stat = current.stat()
        except OSError as exc:
            print(f"[warn] unable to stat {current}: {exc}", file=sys.stderr)
            continue

        entry = Entry(
            path=current,
            is_dir=current.is_dir(),
            size=stat.st_size if current.is_file() else 0,
            modified=datetime.fromtimestamp(stat.st_mtime),
        )
        yield entry
        count += 1
        if limit is not None and count >= limit:
            return

        if entry.is_dir:
            try:
                with os.scandir(current) as iterator:
                    for child in iterator:
                        queue.append(Path(child.path))
            except OSError as exc:
                print(f"[warn] unable to list {current}: {exc}", file=sys.stderr)
                continue


def write_catalog(entries: Iterable[Entry], root: Path, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["relative_path", "type", "size_bytes", "modified"])
        for entry in entries:
            writer.writerow(entry.to_row(root))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Catalog the F: drive (or subset) to CSV.")
    parser.add_argument("--root", default="F:/", help="Root directory to scan (default: F:/)")
    parser.add_argument(
        "--output",
        help="Optional CSV output path. If omitted, only previews/summary are shown.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Optional maximum number of entries to visit (for smoke tests).",
    )
    parser.add_argument(
        "--preview",
        type=int,
        default=0,
        help="Print the first N rows to stdout for quick inspection.",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print aggregate statistics (counts and total file size).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = Path(args.root).resolve()
    if not root.exists():
        print(f"Root path does not exist: {root}")
        sys.exit(2)

    entries = list(iter_entries(root, limit=args.limit))

    if args.preview:
        print("relative_path,type,size_bytes,modified")
        for entry in entries[: args.preview]:
            print(",".join(entry.to_row(root)))

    if args.summary:
        file_count = sum(1 for e in entries if not e.is_dir)
        dir_count = sum(1 for e in entries if e.is_dir)
        total_size = sum(e.size for e in entries)
        print(
            f"Summary: files={file_count:,} directories={dir_count:,} total_size={total_size:,} bytes"
        )

    if args.output:
        output_path = Path(args.output)
        write_catalog(entries, root, output_path)
        print(f"Catalog written to {output_path}")

    if not args.output and not args.preview and not args.summary:
        print("No output requested; use --preview, --summary, or --output to see results.")


if __name__ == "__main__":
    main()
