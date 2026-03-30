r"""
Pre-commit guard to enforce the "Never C:" policy and discourage raw tempfile usage.

- Fails if any staged file contains a hardcoded C:\ path.
- Flags Python files using tempfile.* without going through temp_paths utility.

Usage (pre-commit passes filenames):
  python src/dev_tools/precommit/no_c_guard.py <file1> <file2> ...
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


def is_text_file(p: Path) -> bool:
    try:
        with p.open('rb') as f:
            chunk = f.read(2048)
        # Heuristic: treat as text if it decodes in utf-8 with replacement
        chunk.decode('utf-8', errors='ignore')
        return True
    except Exception:
        return False

C_PATH_RE = re.compile(r"C:([\\/])", re.IGNORECASE)
TEMPFILE_PATTERNS = [
    re.compile(r"tempfile\.(gettempdir|gettempdirb|NamedTemporaryFile|TemporaryDirectory|mkdtemp)\s*\(")
]


def check_file(path: Path) -> list[str]:
    errors: list[str] = []
    if not path.exists() or not path.is_file():
        return errors
    if not is_text_file(path):
        return errors

    try:
        text = path.read_text(encoding='utf-8', errors='ignore')
    except Exception:
        return errors

    # 1) Hardcoded C: paths
    for i, line in enumerate(text.splitlines(), 1):
        if C_PATH_RE.search(line):
            errors.append(f"{path}: line {i}: Hardcoded C: path detected")

    # 2) Python tempfile usage without temp_paths import
    if path.suffix.lower() == '.py':
        if any(p.search(text) for p in TEMPFILE_PATTERNS):
            # Allow if the module uses the centralized temp_paths utility
            if 'core.utils.temp_paths' not in text and 'from core.utils.temp_paths' not in text and 'import temp_paths' not in text:
                errors.append(f"{path}: uses tempfile APIs without temp_paths guard (import core.utils.temp_paths and use get_temp_dir())")

    return errors


def main(argv: list[str]) -> int:
    if len(argv) <= 1:
        # No files; nothing to do
        return 0
    all_errors: list[str] = []
    for arg in argv[1:]:
        p = Path(arg)
        all_errors.extend(check_file(p))

    if all_errors:
        print("No-C guard violations:")
        for e in all_errors:
            print(f" - {e}")
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
