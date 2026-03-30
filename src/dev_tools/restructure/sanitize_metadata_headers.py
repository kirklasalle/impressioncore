"""Metadata / Header Sanitizer

Purpose:
  Convert stray markdown-style metadata lines (e.g. **Created:**, **Updated:**,
  **Tags:**, etc.) that were injected directly into Python source files (often
  at line ~24 in many test / training modules) into safe Python comments to
  eliminate SyntaxError and invalid escape sequence warnings.

Strategy:
  - Scan all *.py files under src/ excluding noisy or legacy snapshots:
      * deployment/
      * archive/
      * logs/
      * __pycache__
  - For each line not inside a triple-quoted string literal that begins with
    optional whitespace + **Word:**, replace leading markup with a comment.
  - Normalize timestamps like 10_27_02 -> 10:27:02.
  - Escape single backslashes in converted metadata lines (src/path -> src/path)
    to silence invalid escape sequence warnings.
  - Dry-run mode (default) only reports proposed changes.

Usage:
  python -m dev_tools.restructure.sanitize_metadata_headers --apply
  python -m dev_tools.restructure.sanitize_metadata_headers --apply --limit tests

Notes:
  This is an incremental hygiene step (Options 1 + 3 from earlier plan):
    1) Automated sanitizer
    3) Skips large legacy / deployment snapshots
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]  # points to src/

EXCLUDE_DIR_NAMES = {
    'deployment',
    'archive',
    'logs',
    '__pycache__',
}

METADATA_PATTERN = re.compile(r"^(?P<indent>\s*)\*\*[A-Za-z_]+:?\s*")
TIME_UNDERSCORE_PATTERN = re.compile(r"\b(\d{2})_(\d{2})_(\d{2})\b")


def should_skip(path: Path, limit: str | None) -> bool:
    if any(part in EXCLUDE_DIR_NAMES for part in path.parts):
        return True
    return bool(limit == 'tests' and 'tests' not in path.parts)


def transform_line(line: str) -> tuple[str, bool]:
    """Return (possibly transformed line, changed?)."""
    m = METADATA_PATTERN.match(line)
    if not m:
        return line, False
    indent = m.group('indent')
    content = line.strip().lstrip('*')  # remove leading asterisks
    content = content.strip()
    # Normalize underscores in HH_MM_SS
    content = TIME_UNDERSCORE_PATTERN.sub(lambda x: f"{x.group(1)}:{x.group(2)}:{x.group(3)}", content)
    # Escape single backslashes (but avoid doubling already doubled sequences)
    content = re.sub(r"(?<!\\)\\(?!\\)", r"\\\\", content)
    return f"{indent}# {content}\n", True


def process_file(path: Path) -> tuple[int, int]:
    try:
        original = path.read_text(encoding='utf-8')
    except Exception:
        return 0, 0
    changed_lines = 0
    lines = original.splitlines(keepends=True)
    new_lines = []
    in_triple = False
    triple_delim = None
    for line in lines:
        stripped = line.strip()
        # Track entry/exit of triple-quoted strings so we do not modify inside them
        if not in_triple and (stripped.startswith('"""') or stripped.startswith("'''")):
            # Single-line docstring case
            if (stripped.count('"""') == 2) or (stripped.count("'''") == 2):
                new_lines.append(line)
                continue
            in_triple = True
            triple_delim = stripped[:3]
            new_lines.append(line)
            continue
        elif in_triple and triple_delim and triple_delim in stripped:
            in_triple = False
            triple_delim = None
            new_lines.append(line)
            continue
        if in_triple:
            new_lines.append(line)
            continue
        new_line, changed = transform_line(line)
        if changed:
            changed_lines += 1
            new_lines.append(new_line)
        else:
            new_lines.append(line)
    if changed_lines == 0:
        return 0, 0
    new_content = ''.join(new_lines)
    if new_content != original:
        path.write_text(new_content, encoding='utf-8')
    return changed_lines, 1


def collect_targets(limit: str | None) -> list[Path]:
    return [p for p in ROOT.rglob('*.py') if not should_skip(p.relative_to(ROOT), limit)]


def dry_run(limit: str | None) -> None:
    files = collect_targets(limit)
    total_files = 0
    total_lines = 0
    for f in files:
        try:
            text = f.read_text(encoding='utf-8')
        except Exception:
            continue
        for line in text.splitlines():
            if METADATA_PATTERN.match(line):
                total_files += 1
                total_lines += 1
                break
    print(f"[DRY-RUN] Files with metadata lines: {total_files}; first-pass line hits: {total_lines}")


def apply(limit: str | None) -> None:
    files = collect_targets(limit)
    changed_files = 0
    changed_lines = 0
    for f in files:
        c_lines, c_files = process_file(f)
        changed_lines += c_lines
        changed_files += c_files
    print(f"[APPLY] Updated {changed_lines} lines across {changed_files} files.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Sanitize stray metadata lines in Python files.")
    parser.add_argument('--apply', action='store_true', help='Apply changes (otherwise dry-run).')
    parser.add_argument('--limit', choices=['tests'], help='Limit scope (e.g., tests).')
    args = parser.parse_args()
    if args.apply:
        apply(args.limit)
    else:
        dry_run(args.limit)


if __name__ == '__main__':
    main()
