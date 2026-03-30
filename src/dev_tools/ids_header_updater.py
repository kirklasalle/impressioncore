"""
IDS Header Updater (Stub)

Provides a no-op/dry-run header standardization endpoint so IDS tools can execute
without failing when the real updater is unavailable. This script will scan for
Markdown files and report counts only. It does not modify files.
"""
from __future__ import annotations

import argparse
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="IDS Header Updater (dry run)")
    parser.add_argument("--target_directory", default=".", help="Directory to process")
    # Accept both --dry_run and --dry-run for compatibility with IDS tool
    parser.add_argument("--dry_run", dest="dry_run", action="store_true", default=False, help="Report only, no changes")
    parser.add_argument("--dry-run", dest="dry_run", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)

    root = _repo_root()
    target = (root / args.target_directory).resolve()
    md_files = list(target.rglob("*.md")) if target.exists() else []

    print(f"[ids_header_updater] Dry run: scanned {len(md_files)} Markdown files under {target}")
    print("[ids_header_updater] No changes applied.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
