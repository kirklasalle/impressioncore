#!/usr/bin/env python3
"""
Markdown Lint Fixer (conservative, IDS-safe)

Purpose:
- Apply safe, mechanical fixes for common Markdown lint rules without altering content semantics.
- Focused rules:
  - MD022/MD032: Ensure blank lines around headings and lists (before and after blocks)
  - MD040: Add a language to opening fenced code blocks missing one (uses 'text')
- Explicitly skips MD041 (first line heading) to preserve ImpressionCore metadata blocks at top.
- Skips files that include "DO NOT CHANGE" or "Do NOT Edit or CHANGE this File" notices.

Usage:
  python src/dev_tools/markdown_lint_fix.py --path docs --report docs/reports

Notes:
- Operates only outside code fences when adjusting blank lines.
- Detects opening vs closing fences to avoid adding language to closing fences.
- Produces a run report with per-file change counts.

"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

SKIP_MARKERS = (
    "DO NOT CHANGE",
    "Do NOT Edit or CHANGE this File",
    "[DO NOT CHANGE",
)

FENCE = "```"

class FixStats:
    def __init__(self) -> None:
        self.files_scanned = 0
        self.files_updated = 0
        self.total_heading_blanks_added = 0
        self.total_list_blanks_added = 0
        self.total_fence_lang_added = 0
        self.changed_files: list[tuple[str, int, int, int]] = []  # (path, heading, list, fence)

    def add_file(self, path: Path, h: int, l: int, f: int) -> None:
        self.files_updated += 1
        self.total_heading_blanks_added += h
        self.total_list_blanks_added += l
        self.total_fence_lang_added += f
        self.changed_files.append((str(path), h, l, f))


def should_skip_file(text: str) -> bool:
    header_window = text.splitlines()[:50]
    hay = "\n".join(header_window)
    return any(marker in hay for marker in SKIP_MARKERS)


def is_heading(line: str) -> bool:
    s = line.lstrip()
    if not s.startswith("#"):  # noqa: SIM103
        return False
    # Must be ATX heading like '# ' or '##\t'
    # Avoid treating '#####' without space as heading (MD018), but many docs use it; still treat as heading
    return True


def is_list_item(line: str) -> bool:
    s = line.lstrip()
    if not s:
        return False
    # unordered
    if s.startswith(('- ', '* ', '+ ')):
        return True
    # ordered: '1. ', '23. '
    if len(s) > 2 and s[0].isdigit():
        i = 1
        while i < len(s) and s[i].isdigit():
            i += 1
        if i < len(s) and s[i:i+2] == '. ':
            return True
    return False


def add_blank_lines_around_blocks(lines: list[str]) -> tuple[list[str], int, int]:
    """Adds blank lines around headings and list blocks, skipping inside code fences.
    Returns new lines, (heading_adds, list_adds)
    """
    out: list[str] = []
    in_code = False
    heading_adds = 0
    list_adds = 0

    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        stripped = line.rstrip("\n")

        # Toggle code block state when encountering fence line
        if stripped.startswith(FENCE):
            # Determine if opening or closing
            stripped[len(FENCE):].strip()
            if not in_code:
                # opening
                in_code = True
            else:
                # closing
                in_code = False
            out.append(line)
            i += 1
            continue

        if not in_code:
            # Headings: ensure blank line before (unless at file start) and after
            if is_heading(stripped):
                # Before
                if len(out) > 0 and out[-1].strip() != "":
                    out.append("\n")
                    heading_adds += 1
                out.append(line)
                # After: look ahead to next non-EOF line
                nxt = lines[i+1] if i+1 < n else None
                if nxt is not None and nxt.strip() != "":
                    out.append("\n")
                    heading_adds += 1
                i += 1
                continue

            # Lists: treat consecutive list items as a block
            if is_list_item(stripped):
                # ensure blank line before block
                if len(out) > 0 and out[-1].strip() != "":
                    out.append("\n")
                    list_adds += 1
                # write the block
                while i < n and is_list_item(lines[i].rstrip("\n")):
                    out.append(lines[i])
                    i += 1
                # ensure blank line after block if next line exists and is not blank or EOF
                if i < n and lines[i].strip() != "":
                    out.append("\n")
                    list_adds += 1
                continue

        # default passthrough
        out.append(line)
        i += 1

    return out, heading_adds, list_adds


def add_language_to_fences(lines: list[str]) -> tuple[list[str], int]:
    """Adds 'text' language to opening fences without a language spec."""
    out: list[str] = []
    in_code = False
    lang_adds = 0

    for line in lines:
        stripped = line.rstrip("\n")
        if stripped.startswith(FENCE):
            rest = stripped[len(FENCE):]
            rest_stripped = rest.strip()
            if not in_code:
                # opening fence
                if rest_stripped == "":
                    out.append(f"{FENCE} text\n")
                    lang_adds += 1
                else:
                    out.append(line)
                in_code = True
            else:
                # closing fence, preserve as-is
                out.append(line)
                in_code = False
        else:
            out.append(line)

    return out, lang_adds


def process_file(path: Path) -> tuple[bool, int, int, int]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    if should_skip_file(text):
        return False, 0, 0, 0

    lines = [l if l.endswith("\n") else l + "\n" for l in text.splitlines()]

    # Step 1: blank lines around headings/lists (outside code)
    lines1, h_adds, l_adds = add_blank_lines_around_blocks(lines)
    # Step 2: add language to fences for MD040
    lines2, f_adds = add_language_to_fences(lines1)

    changed = (h_adds + l_adds + f_adds) > 0 and (lines2 != lines)
    if changed:
        new_text = "".join(lines2)
        # Avoid trailing extra newlines spike
        if not new_text.endswith("\n"):
            new_text += "\n"
        path.write_text(new_text, encoding="utf-8")
    return changed, h_adds, l_adds, f_adds


def _fmt_timestamp(dt_obj: datetime) -> str:
    """Return 'Month Day, Year HH:MM:SS AM/PM' with non-padded day."""
    return f"{dt_obj.strftime('%B')} {dt_obj.day}, {dt_obj.year} {dt_obj.strftime('%I:%M:%S %p')}"


def write_report(report_dir: Path, stats: FixStats, started_at: datetime, ended_at: datetime) -> Path:
    report_dir.mkdir(parents=True, exist_ok=True)
    ts = ended_at.strftime("%Y%m%d_%H%M%S")
    report_path = report_dir / f"markdown_lint_fix_run_{ts}.md"
    lines: list[str] = []
    lines.append("# Markdown Lint Fix Run Report\n\n")
    lines.append(f"**Started:** {_fmt_timestamp(started_at)}  \n")
    lines.append(f"**Ended:** {_fmt_timestamp(ended_at)}  \n")
    lines.append(f"**Files Scanned:** {stats.files_scanned}  \n")
    lines.append(f"**Files Updated:** {stats.files_updated}  \n")
    lines.append(f"**Heading Blanks Added:** {stats.total_heading_blanks_added}  \n")
    lines.append(f"**List Blanks Added:** {stats.total_list_blanks_added}  \n")
    lines.append(f"**Fence Languages Added:** {stats.total_fence_lang_added}  \n\n")

    if stats.changed_files:
        lines.append("## Files Updated\n\n")
        lines.append("Path | Heading Blanks | List Blanks | Fence Lang\n")
        lines.append("--- | ---:| ---:| ---:\n")
        for p, h, l, f in sorted(stats.changed_files):
            lines.append(f"{p} | {h} | {l} | {f}\n")
        lines.append("\n")

    lines.append("---\n\n")
    lines.append("IDS Integration: This report is indexed by the ImpressionCore Documentation System (IDS).\n")

    report_path.write_text("".join(lines), encoding="utf-8")
    return report_path


def main() -> int:
    ap = argparse.ArgumentParser(description="Conservative Markdown lint fixer for ImpressionCore docs")
    ap.add_argument("--path", default="docs", help="Directory to scan (default: docs)")
    ap.add_argument("--report", default="docs/reports", help="Directory to write reports (default: docs/reports)")
    args = ap.parse_args()

    root = Path(args.path)
    report_dir = Path(args.report)
    if not root.exists():
        print(f"ERROR: path not found: {root}", file=sys.stderr)
        return 2

    stats = FixStats()
    started_at = datetime.now()

    md_files = [p for p in root.rglob("*.md") if p.is_file()]
    # Process also the top-level docs/*.md or nested within; rglob already covers

    for p in md_files:
        # Skip images/ or other asset folders that might include .md placeholders
        stats.files_scanned += 1
        try:
            changed, h_adds, l_adds, f_adds = process_file(p)
        except Exception as e:
            print(f"WARN: failed to process {p}: {e}", file=sys.stderr)
            continue
        if changed:
            stats.add_file(p, h_adds, l_adds, f_adds)

    ended_at = datetime.now()
    report_path = write_report(report_dir, stats, started_at, ended_at)

    print(

            f"Markdown lint fix complete. Scanned={stats.files_scanned}, "
            f"Updated={stats.files_updated}. Report: {report_path}"

    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
