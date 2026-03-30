from __future__ import annotations

import argparse
from pathlib import Path

from src.dev_tools.maintenance.convert_to_utf8 import convert


def is_utf8(path: Path) -> bool:
    try:
        _ = path.read_text(encoding="utf-8")
        return True
    except Exception:
        return False


def main() -> int:
    ap = argparse.ArgumentParser(description="Batch convert .log files to UTF-8 (with backups)")
    ap.add_argument("--root", default="docs/archive", help="Root directory to scan (default: docs/archive)")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    if not root.exists():
        print(f"[batch_convert_utf8] Root not found: {root}")
        return 0

    files = list(root.rglob("*.log"))
    converted = 0
    skipped = 0

    for f in files:
        if is_utf8(f):
            skipped += 1
            continue
        ok = convert(f)
        if ok:
            converted += 1

    print(f"[batch_convert_utf8] Scanned: {len(files)} | Converted: {converted} | Already UTF-8: {skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
