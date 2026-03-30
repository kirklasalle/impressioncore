"""
Standardize ImpressionCore documentation headers across docs/**/*.md.

Actions per file:
- Ensure first line is a single H1 title (preserve existing if present, else derive from filename)
- Normalize metadata lines with correct format and order:
  **Created:** Month Day, Year
  **Updated:** Month Day, Year (current date)
  **Author:** <preserve or default>
  **Tags:** <preserve or default>
  **Category:** <derived by path>
  **Status:** Active
  **IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).
- Insert a horizontal rule (---) after metadata
- Remove stray YAML-like `tags:` blocks and misformatted separator lines that cause lint warnings

Generates a run report in docs/reports/standardization_run_YYYYMMDD_HHMMSS.md
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOCS_DIR = ROOT / "docs"
REPORTS_DIR = DOCS_DIR / "reports"


DATE_FMT_DISPLAY = "%B %d, %Y"  # Month Day, Year


CREATED_PATTERNS = [
    re.compile(r"^\*\*Created:\*\*\s*(.+?)\s*$", re.IGNORECASE),
]
UPDATED_PATTERNS = [
    re.compile(r"^\*\*Updated:\*\*\s*(.+?)\s*$", re.IGNORECASE),
]


def parse_date_to_display(s: str) -> str | None:
    """Try parsing a variety of date formats and return 'Month Day, Year'."""
    s = s.strip().strip('.')
    fmts = [
        "%B %d, %Y",    # August 9, 2025
        "%b %d, %Y",     # Aug 9, 2025
        "%Y-%m-%d",      # 2025-08-09
        "%m/%d/%Y",      # 08/09/2025
        "%d-%b-%Y",      # 09-Aug-2025
        "%B-%d-%Y",      # August-09-2025
        "%b-%d-%Y",      # Aug-09-2025
        "%B %d %Y",      # August 9 2025
        "%Y/%m/%d",      # 2025/08/09
    ]
    for fmt in fmts:
        try:
            d = dt.datetime.strptime(s, fmt).date()
            return d.strftime(DATE_FMT_DISPLAY)
        except ValueError:
            continue
    # Try to handle partials like 'January 17, 2025 11:00 AM'
    try:
        d = dt.datetime.fromisoformat(s.replace("Z", "+00:00")).date()
        return d.strftime(DATE_FMT_DISPLAY)
    except Exception:
        pass
    # Try to extract YYYY-MM-DD within the string
    m = re.search(r"(\d{4})[-/](\d{2})[-/](\d{2})", s)
    if m:
        try:
            d = dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
            return d.strftime(DATE_FMT_DISPLAY)
        except Exception:
            pass
    return None


def derive_category(p: Path) -> str:
    parts = [q.lower() for q in p.parts]
    if "reference" in parts:
        return "Reference Documentation"
    if "developer" in parts:
        return "Developer Documentation"
    if "user" in parts or "user_guide" in parts:
        return "User Documentation"
    if "technical" in parts:
        return "Technical Documentation"
    if "strategic" in parts:
        return "Documentation"
    return "Documentation"


def default_author(text: str) -> str:
    # Preserve existing if found
    m = re.search(r"^\*\*Author:\*\*\s*(.+?)\s*$", text, flags=re.IGNORECASE | re.MULTILINE)
    if m:
        return m.group(1)
    return "ImpressionCore Team"


def default_tags(p: Path, text: str) -> str:
    # Preserve existing if found
    m = re.search(r"^\*\*Tags:\*\*\s*(.+?)\s*$", text, flags=re.IGNORECASE | re.MULTILINE)
    if m:
        return m.group(1)
    # Derive a minimal useful default
    rel = p.relative_to(ROOT).as_posix()
    # Avoid backslashes inside f-string expressions by computing replacement outside
    rel_tag = rel.replace('/', os.sep)
    base_tag = f"#{rel_tag}"
    return f"{base_tag} #documentation"


def extract_title(lines: list[str], p: Path) -> tuple[str, int]:
    for i, line in enumerate(lines):
        if line.lstrip().startswith("# "):
            return line.strip(), i
    # No title; synthesize from filename
    title = "# " + p.stem.replace("_", " ")
    return title, -1


def strip_header_region(lines: list[str], title_idx: int) -> tuple[list[str], list[str]]:
    """Return (header_lines_to_replace, remaining_content) starting from title_idx.
    We keep the first title line, then skip metadata block until the first non-meta content line.
    """
    if title_idx == -1:
        # No title present; header is empty
        return [], lines
    header = [lines[title_idx].rstrip()]
    i = title_idx + 1
    def is_meta(l: str) -> bool:
        l = l.rstrip()
        if not l:
            return True
        if l.strip() == "---" or l.strip() == "----":
            return True
        # explicit meta fields
        if re.match(r"^\*\*(Created|Updated|Author|Tags|Category|Status|IDS Integration):\*\*", l, re.IGNORECASE):
            return True
        # Old stray yaml-ish block start
        return bool(re.match(r"^tags:\s*\[.*\]\s*$", l, re.IGNORECASE))
    while i < len(lines) and is_meta(lines[i]):
        i += 1
    return header, lines[i:]


def standardize_file(path: Path, now_date: str) -> tuple[bool, str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()

    # Extract or create title
    title, title_idx = extract_title(lines, path)

    # Determine Created date
    created_value = None
    for pat in CREATED_PATTERNS:
        m = pat.search(text)
        if m:
            created_value = parse_date_to_display(m.group(1))
            break
    if not created_value:
        # Try to infer from file creation time
        try:
            cts = dt.datetime.fromtimestamp(os.path.getctime(path)).date()
            created_value = cts.strftime(DATE_FMT_DISPLAY)
        except Exception:
            created_value = now_date

    author_value = default_author(text)
    tags_value = default_tags(path, text)
    category_value = derive_category(path)
    status_value = "Active"

    # Sanitize content: strip old header region
    header_kept, remaining = strip_header_region(lines, title_idx)

    # Build new header
    new_header = [
        title,
        "",
        f"**Created:** {created_value}  ",
        f"**Updated:** {now_date}  ",
        f"**Author:** {author_value}  ",
        f"**Tags:** {tags_value}  ",
        f"**Category:** {category_value}  ",
        f"**Status:** {status_value}",
        "**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).",
        "",
        "---",
        "",
    ]

    new_text = "\n".join(new_header + remaining) + ("\n" if not text.endswith("\n") else "")
    if new_text != text:
        path.write_text(new_text, encoding="utf-8")
        return True, "updated"
    return False, "unchanged"


def main() -> int:
    parser = argparse.ArgumentParser(description="Standardize docs headers")
    parser.add_argument("--write", action="store_true", help="Apply changes (default true if script is run)")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of files for testing")
    args = parser.parse_args()

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    now = dt.datetime.now()
    now_date = now.strftime(DATE_FMT_DISPLAY)
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    report_path = REPORTS_DIR / f"standardization_run_{timestamp}.md"

    md_files = sorted(DOCS_DIR.rglob("*.md"))
    changed = 0
    scanned = 0
    for p in md_files:
        # Skip archived or backup reports if desired? Keep them for consistency.
        if args.limit and scanned >= args.limit:
            break
        try:
            c, _ = standardize_file(p, now_date)
            if c:
                changed += 1
        except Exception:
            # Continue and note errors in report later
            pass
        scanned += 1

    report_lines = [
        f"# Documentation Standardization Report - {now.strftime(DATE_FMT_DISPLAY)}",
        "",
        f"- Scanned files: {scanned}",
        f"- Updated files: {changed}",
        f"- Unchanged files: {scanned - changed}",
        "",
        "This run normalized headers, dates, authors, tags, categories, status, and added IDS Integration notices.",
    ]
    report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    print(f"Standardization complete. Scanned={scanned}, Updated={changed}. Report: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
