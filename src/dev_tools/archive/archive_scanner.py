"""Archive Scanner and Enforcer

Scans the src/ tree for deprecated / archived markers and proposes or applies
moves into the structured archive/ hierarchy.

Usage:
    python -m dev_tools.archive.archive_scanner --report
    python -m dev_tools.archive.archive_scanner --apply [--shim]

Markers Detected (case-insensitive substring match):
    1. "DEPRECATED / ARCHIVED"
    2. "Status:** Archived"
    3. "Status: Archived"
    4. docstring line starting with or containing "Archived" in first 10 lines

Outputs:
    - Dry report to stdout (default)
    - Updates ARCHIVE_INDEX.md & relocation_plan.md when --apply provided
    - Optionally writes lightweight shim (DeprecationWarning) at original path when --shim

Safety:
    - Skips any path already under src/archive/
    - Only processes .py files
    - Does not delete content; writes stub and moves original content into archive/ preserving relative path

Date Standard:
    - Uses Month Day, Year (e.g., August 23, 2025)
"""
from __future__ import annotations

import argparse
import datetime as _dt
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]  # .../impressioncore
SRC_ROOT = REPO_ROOT / "src"
ARCHIVE_ROOT = SRC_ROOT / "archive"
DOCS_ROOT = REPO_ROOT / "docs"
ARCHIVE_INDEX = DOCS_ROOT / "ARCHIVE_INDEX.md"
RELOCATION_PLAN = SRC_ROOT / "management" / "relocation_plan.md"
ARCHIVE_LOG = DOCS_ROOT / "archive" / "archive_log.jsonl"
DATE_STR = _dt.datetime.now().strftime("%B %e, %Y").replace("  ", " ")

MARKER_PATTERNS = [
    re.compile(r"DEPRECATED\s*/\s*ARCHIVED", re.IGNORECASE),
    re.compile(r"Status:\*\*? Archived", re.IGNORECASE),
    re.compile(r"Status:\s*Archived", re.IGNORECASE),
]


def detect_markers(text: str | Path) -> bool:
    """Detect archive / deprecation markers.

    Accepts either raw text or a Path. Only the first 10 lines are
    inspected for performance; patterns are case-insensitive.
    Returns True if any marker pattern or the word 'Archived' appears.
    """
    if isinstance(text, Path):
        if not text.exists():
            return False
        try:
            raw = text.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return False
    else:
        raw = text
    head = "\n".join(raw.splitlines()[:10])
    if "Archived" in head:
        return True
    return any(p.search(head) for p in MARKER_PATTERNS)


def find_candidates() -> list[Path]:
    candidates: list[Path] = []
    for path in SRC_ROOT.rglob("*.py"):
        if ARCHIVE_ROOT in path.parents:
            continue
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        if detect_markers(content):
            candidates.append(path)
    return candidates


def compute_archive_path(original: Path) -> Path:
    rel = original.relative_to(SRC_ROOT)
    return ARCHIVE_ROOT / rel


def ensure_parent(p: Path) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)


def write_shim(original: Path, archive_rel: Path) -> None:
    header = (
        "\"\"\"Shim: Archived Module\n\n"
        f"Original relocated to `{archive_rel.as_posix()}` on {DATE_STR}.\n"
        "\"\"\"\n"
    )
    body = (
        "from __future__ import annotations\n"
        "import warnings as _warnings\n"
        "_warnings.warn(\n"
        f"    \"{original.stem} is archived; see {archive_rel.as_posix()}\",\n"
        "    DeprecationWarning,\n"
        "    stacklevel=2,\n"
        ")\n"
        "__all__ = []\n"
    )
    shim = header + body
    original.write_text(shim, encoding="utf-8")


def update_archive_index(records: list[dict[str, str]]) -> None:
    if not records:
        return
    if not ARCHIVE_INDEX.exists():
        return
    lines = ARCHIVE_INDEX.read_text(encoding="utf-8").splitlines()
    table_start = None
    for i, ln in enumerate(lines):
        if ln.startswith("| Date | Original Path"):
            table_start = i + 2  # skip header + separator
            break
    if table_start is None:
        # append new section
        lines.append("\n## Recent Archive Moves (Appended)\n")
        lines.append("| Date | Original Path | Archived Path | Reason | Method |")
        lines.append("|------|---------------|---------------|--------|--------|")
        table_start = len(lines)
    insertion_index = table_start
    new_rows = [
        f"| {r['archived_on']} | {r['original_path']} | {r['archived_path']} | {r['reason']} | automated |"
        for r in records
    ]
    lines[insertion_index:insertion_index] = new_rows
    ARCHIVE_INDEX.write_text("\n".join(lines) + "\n", encoding="utf-8")

def append_ledger(records: list[dict[str, str]]) -> None:
    if not records:
        return
    ARCHIVE_LOG.parent.mkdir(parents=True, exist_ok=True)
    with ARCHIVE_LOG.open("a", encoding="utf-8") as f:
        for r in records:
            import json
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def update_relocation_plan(records: list[dict[str, str]]) -> None:
    if not RELOCATION_PLAN.exists() or not records:
        return
    text = RELOCATION_PLAN.read_text(encoding="utf-8")
    # Append rows if not already present
    for r in records:
        if r['original_path'] in text:
            continue
        row = f"| {Path(r['original_path']).name} | archive | {r['archived_path'].replace('src/','')} | archived |"
        # Insert before 'Next Steps:' section
        if '\nNext Steps:' in text:
            parts = text.split('\nNext Steps:')
            text = parts[0].rstrip() + f"\n{row}\n\nNext Steps:" + parts[1]
        else:
            text += f"\n{row}\n"
    RELOCATION_PLAN.write_text(text, encoding="utf-8")


def apply_moves(candidates: list[Path], shim: bool) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for original in candidates:
        archive_path = compute_archive_path(original)
        ensure_parent(archive_path)
        # Move original content
        content = original.read_text(encoding="utf-8", errors="ignore")
        archive_path.write_text(content, encoding="utf-8")
        # Replace original with shim or leave removal stub
        if shim:
            write_shim(original, archive_path.relative_to(SRC_ROOT))
        else:
            original.write_text(
                f"# Archived on {DATE_STR} -> {archive_path.relative_to(SRC_ROOT).as_posix()}\n",
                encoding="utf-8",
            )
        records.append({
            "original_path": f"src/{original.relative_to(SRC_ROOT).as_posix()}",
            "archived_path": f"src/{archive_path.relative_to(SRC_ROOT).as_posix()}",
            "archived_on": DATE_STR,
            "reason": "Superseded",
            "detection": "auto"
        })
    return records


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan and archive deprecated modules")
    parser.add_argument("--apply", action="store_true", help="Apply archival moves")
    parser.add_argument("--shim", action="store_true", help="Insert deprecation shim at original path")
    parser.add_argument("--report", action="store_true", help="Print report of candidates")
    args = parser.parse_args()

    candidates = find_candidates()
    print(f"[archive-scanner] scan complete: {len(candidates)} candidate(s) found")
    if args.report and not args.apply:
        for c in candidates:
            print(" -", c.relative_to(SRC_ROOT))
        # exit code 2 if any candidates (signals work to do), else 0
        return 2 if candidates else 0

    if not args.apply:
        # no apply, treat as noop success
        return 0

    if not candidates:
        print("[archive-scanner] no candidates to archive")
        return 0

    records: list[dict[str, str]] = apply_moves(candidates, shim=args.shim)
    update_archive_index(records)
    update_relocation_plan(records)
    append_ledger(records)
    print(f"[archive-scanner] archived {len(records)} file(s)")
    # exit code 0 success, >0 reserved for future validation mismatches
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
