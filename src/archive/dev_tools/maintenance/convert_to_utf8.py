"""
Convert file to UTF-8 with BOM/legacy encodings handling.
Creates a .bak backup beside the file, then rewrites in UTF-8.
"""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path


CANDIDATE_ENCODINGS = [
    'utf-8', 'utf-8-sig', 'cp1252', 'latin-1', 'iso-8859-1', 'utf-16', 'utf-16-le', 'utf-16-be'
]


def convert(path: Path) -> bool:
    if not path.exists() or not path.is_file():
        print(f"[convert_to_utf8] Skipping non-file: {path}")
        return False
    data = None
    for enc in CANDIDATE_ENCODINGS:
        try:
            data = path.read_text(encoding=enc)
            print(f"[convert_to_utf8] Read with encoding={enc}")
            break
        except Exception:
            continue
    if data is None:
        print(f"[convert_to_utf8] Failed to read {path} with candidate encodings")
        return False
    backup = path.with_suffix(path.suffix + '.bak')
    shutil.copy2(path, backup)
    path.write_text(data, encoding='utf-8')
    print(f"[convert_to_utf8] Wrote UTF-8 and created backup: {backup}")
    return True


def main() -> int:
    ap = argparse.ArgumentParser(description='Convert a file to UTF-8 with backup')
    ap.add_argument('file', help='Path to the file to convert')
    args = ap.parse_args()
    ok = convert(Path(args.file))
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
