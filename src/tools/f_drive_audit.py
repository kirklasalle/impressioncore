from __future__ import annotations

import os
import shutil
from pathlib import Path


def dir_size_bytes(path: Path) -> int:
    total = 0
    for root, _dirs, files in os.walk(path):
        for name in files:
            file_path = Path(root) / name
            try:
                if not file_path.is_symlink():
                    total += file_path.stat().st_size
            except OSError:
                continue
    return total


def format_gb(value: int) -> str:
    return f"{value / (1024 ** 3):.2f}"


def summarize_root(root: Path) -> list[tuple[str, int]]:
    rows: list[tuple[str, int]] = []
    for child in sorted(root.iterdir(), key=lambda p: p.name.lower()):
        if child.is_dir():
            rows.append((child.name, dir_size_bytes(child)))
    return rows


def main() -> None:
    roots = [Path("F:/data"), Path("F:/models")]
    for root in roots:
        if not root.exists():
            print(f"ROOT={root};MISSING")
            continue
        total = dir_size_bytes(root)
        print(f"ROOT={root};TOTAL_GB={format_gb(total)}")
        for name, size in summarize_root(root):
            print(f"SUB={name};GB={format_gb(size)}")

    total, used, free = shutil.disk_usage("F:/")
    print(f"DRIVE_TOTAL_GB={total / (1024 ** 3):.2f}")
    print(f"DRIVE_USED_GB={used / (1024 ** 3):.2f}")
    print(f"DRIVE_FREE_GB={free / (1024 ** 3):.2f}")


if __name__ == "__main__":
    main()
