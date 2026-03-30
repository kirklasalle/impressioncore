"""Summarize an F: drive catalog CSV.

Computes aggregate metrics by top-level directory and file extension to help
planning data utilization.
"""

from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from collections.abc import Iterable, Sequence
from pathlib import Path


def load_catalog(path: Path) -> Iterable[dict[str, str]]:
    with path.open("r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        yield from reader


def summarize(path: Path, *, group_depth: int, first_filters: Sequence[str] | None = None):
    totals: dict[str, int] = defaultdict(int)
    counts: dict[str, int] = defaultdict(int)
    ext_sizes: Counter[str] = Counter()

    for row in load_catalog(path):
        if row["type"] != "file":
            continue
        rel_path = row.get("relative_path", "").strip()
        if not rel_path:
            continue
        size = int(row["size_bytes"])
        path_obj = Path(rel_path)
        parts = path_obj.parts
        if not parts:
            key_parts: tuple[str, ...] = tuple()
            top = "<root>"
        else:
            key_parts = tuple(parts[:group_depth])
            top = "/".join(key_parts) if key_parts else parts[0]
        if first_filters and key_parts and key_parts[0] not in first_filters:
            continue
        totals[top] += size
        counts[top] += 1
        ext = path_obj.suffix.lower() or "<none>"
        ext_sizes[ext] += size

    return totals, counts, ext_sizes


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize F: drive catalog CSV")
    parser.add_argument("catalog", type=Path, help="Path to the catalog CSV file")
    parser.add_argument("--top-ext", type=int, default=10, help="Number of top extensions to list")
    parser.add_argument(
        "--group-depth",
        type=int,
        default=1,
        help="Number of leading path segments to use when grouping (default: 1)",
    )
    parser.add_argument(
        "--first-filter",
        action="append",
        default=None,
        help="Optional first-level directory names to include (repeatable)",
    )
    args = parser.parse_args()

    totals, counts, ext_sizes = summarize(
        args.catalog, group_depth=max(args.group_depth, 1), first_filters=args.first_filter
    )

    print("Top-level directory summary:")
    for top, size in sorted(totals.items(), key=lambda item: item[1], reverse=True):
        print(f"- {top:25s} files={counts[top]:>10,} size={size:>15,} bytes")

    print("\nFile extension summary:")
    for ext, size in ext_sizes.most_common(args.top_ext):
        print(f"- {ext:10s} size={size:>15,} bytes")


if __name__ == "__main__":
    main()
