"""
Docs Management & Analysis Toolkit

Purpose: Provide inventory, index reconciliation, and basic content analysis
for the documentation corpus. Outputs JSON and Markdown reports for quick review.

Usage:
    python -m src.dev_tools.docs_management.docs_manager --help

Commands:
    inventory           Build a file inventory of docs/ (paths, sizes, timestamps, metadata)
    reconcile           Compare DOCUMENTATION_INDEX.md links vs actual files
    analyze             Run basic content checks (headers, tags, dates)
    refactor            Propose (dry-run) or apply IDS-standard header fixes (prepends minimal block)
    dedup-headers       Merge and de-duplicate repeated header lines (Created/Updated/Author/Tags/Category/Status)
    fix-missing-links   Generate and apply replacements for missing links in DOCUMENTATION_INDEX.md (safe heuristics)
    apply-index         Append index suggestions into DOCUMENTATION_INDEX.md (Unclassified Additions)
    categorize-index    Move Unclassified Additions into appropriate sections based on path heuristics
    apply-all           Apply IDS-standard headers and index suggestions
    all                 Run inventory + reconcile + analyze

Outputs:
  docs/reports/docs_inventory.json
  docs/reports/docs_reconciliation.json
  docs/reports/docs_analysis.md
"""

from __future__ import annotations

import argparse
import difflib
import json
import os
import re
from dataclasses import asdict, dataclass
from datetime import datetime

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
DEFAULT_DOCS_ROOT = os.path.join(REPO_ROOT, "docs")
INDEX_PATH = os.path.join(DEFAULT_DOCS_ROOT, "DOCUMENTATION_INDEX.md")
REPORTS_DIR = os.path.join(DEFAULT_DOCS_ROOT, "reports")

# Markdown link pattern that supports parentheses inside href (one level)
MD_LINK_RE = re.compile(r"\[([^\]]+)\]\(((?:[^()]+|\([^()]*\))+?)\)")

# Header line regex: supports "Key:" or "**Key:**"
HEADER_KEYS = ["Created", "Updated", "Author", "Tags", "Category", "Status"]
HEADER_RE = re.compile(r"^\s*(?:\*\*)?\s*(Created|Updated|Author|Tags|Category|Status)\s*:?\s*(?:\*\*)?\s*(.*)$",
                       re.IGNORECASE)


@dataclass
class DocMeta:
    created: str | None = None
    updated: str | None = None
    author: str | None = None
    tags: str | None = None
    category: str | None = None
    status: str | None = None


@dataclass
class DocRecord:
    path: str
    size: int
    mtime: str
    meta: DocMeta


def _ensure_reports_dir() -> None:
    os.makedirs(REPORTS_DIR, exist_ok=True)


def _iter_markdown_files(root: str) -> list[str]:
    md_files: list[str] = []
    for dirpath, _, filenames in os.walk(root):
        # Skip some heavy or generated locations if present
        try:
            rel = os.path.relpath(dirpath, REPO_ROOT).replace("\\", "/")
        except ValueError:
            # Different drive, use absolute normalized path for filtering
            rel = os.path.abspath(dirpath).replace("\\", "/")
        if any(part.lower() in {".git", "__pycache__"} for part in rel.split("/")):
            continue
        for fn in filenames:
            if fn.lower().endswith(".md"):
                md_files.append(os.path.join(dirpath, fn))
    return md_files


def _read_text_head(path: str, max_bytes: int = 16384) -> str:
    with open(path, encoding="utf-8", errors="ignore") as f:
        return f.read(max_bytes)


def _parse_metadata(md_text: str) -> DocMeta:
    # Look for common header fields in the first ~16KB
    header = md_text.split("\n\n", 1)[0]
    def get(key):
        return _extract_line_value(header, key)
    return DocMeta(
        created=get("Created:") or get("**Created:**"),
        updated=get("Updated:") or get("**Updated:**"),
        author=get("Author:") or get("**Author:**"),
        tags=get("Tags:") or get("**Tags:**"),
        category=get("Category:") or get("**Category:**"),
        status=get("Status:") or get("**Status:**"),
    )


def _extract_line_value(text: str, prefix: str) -> str | None:
    for line in text.splitlines():
        if line.strip().startswith(prefix):
            return line.split(prefix, 1)[1].strip()
    return None


def build_inventory(root: str) -> list[DocRecord]:
    records: list[DocRecord] = []
    for path in _iter_markdown_files(root):
        try:
            st = os.stat(path)
            head = _read_text_head(path)
            meta = _parse_metadata(head)
            try:
                rel = os.path.relpath(path, REPO_ROOT).replace("\\", "/")
            except ValueError:
                # Different drive (e.g., F:\ vs D:\) — use absolute normalized path
                rel = os.path.abspath(path).replace("\\", "/")
            records.append(
                DocRecord(
                    path=rel,
                    size=st.st_size,
                    mtime=datetime.fromtimestamp(st.st_mtime).isoformat(timespec="seconds"),
                    meta=meta,
                )
            )
        except Exception:
            # Keep going; robustness over perfection
            continue
    return records


def parse_index_links(index_path: str = INDEX_PATH) -> list[tuple[str, str]]:
    links: list[tuple[str, str]] = []
    try:
        text = _read_text_head(index_path, max_bytes=2_000_000)
    except FileNotFoundError:
        return links
    for m in MD_LINK_RE.finditer(text):
        title, href = m.group(1), m.group(2)
        # Only capture project-local doc links
        if href.startswith("docs/") or href.startswith(".mcp/") or href.startswith("src/") or href.startswith("backups/"):
            links.append((title.strip(), href.strip()))
    return links


def reconcile_index(inventory: list[DocRecord], links: list[tuple[str, str]]):
    """Reconcile index links vs actual files.
    - Missing targets: computed by checking on-disk existence across the entire repo, not just docs/ MDs.
    - Unindexed files: limited to docs/ tree (Markdown and others present in inventory), not present in index links.
    """
    files_set_docs = {rec.path for rec in inventory}  # docs/ inventory only
    link_paths = set()
    for _, href in links:
        # Normalize link to repo-root relative
        norm = href
        if norm.startswith("./"):
            norm = os.path.normpath(os.path.join("docs/reference", norm[2:])).replace("\\", "/")
        link_paths.add(norm)

    # Determine missing by filesystem existence (covers docs/, .mcp/, src/, backups/, etc.)
    missing_targets: list[str] = []
    for p in sorted(link_paths):
        abs_p = os.path.join(REPO_ROOT, p)
        if not os.path.exists(abs_p):
            missing_targets.append(p)

    # Unindexed: docs/ files from inventory not referenced in links
    unindexed_files = sorted([p for p in files_set_docs if p.startswith("docs/") and p not in link_paths])
    return {
        "linked_count": len(link_paths),
        "files_count": len(files_set_docs),
        "missing_targets": missing_targets,
        "unindexed_files": unindexed_files,
    }


def analyze_content(inventory: list[DocRecord]) -> dict[str, object]:
    """Basic checks: header presence, status, and date fields."""
    problems = []
    for rec in inventory:
        meta = rec.meta
        missing = []
        if not meta.created:
            missing.append("Created")
        if not meta.updated:
            missing.append("Updated")
        if not meta.category:
            missing.append("Category")
        if not meta.status:
            missing.append("Status")
        if missing:
            problems.append({"path": rec.path, "missing_fields": missing})
    summary = {
        "total": len(inventory),
        "with_problems": len(problems),
    }
    return {"summary": summary, "problems": problems}


def _infer_category_from_path(path: str) -> str:
    p = path.replace("\\", "/").lower()
    if "/docs/reference/" in p:
        return "Reference Documentation"
    if "/docs/reports/" in p:
        return "Report"
    if "/docs/strategic/" in p:
        return "Strategic"
    if "/docs/process/" in p:
        return "Process"
    return "Documentation"


def propose_header_fix(rec: DocRecord) -> str | None:
    missing = []
    if not rec.meta.created:
        missing.append("Created")
    if not rec.meta.updated:
        missing.append("Updated")
    if not rec.meta.author:
        missing.append("Author")
    if not rec.meta.tags:
        missing.append("Tags")
    if not rec.meta.category:
        missing.append("Category")
    if not rec.meta.status:
        missing.append("Status")
    if not missing:
        return None

    created = rec.meta.created or datetime.fromisoformat(rec.mtime).strftime("%B %d, %Y")
    updated = datetime.now().strftime("%B %d, %Y")
    author = rec.meta.author or "Kirk LaSalle; GitHub Copilot"
    # Derive a minimal path-based tag and mark standardization
    path_tag = (rec.path if os.path.isabs(rec.path) else rec.path).replace("/", "\\")  # noqa: RUF034
    tags = rec.meta.tags or f"#ids #standardized_header #{path_tag}"
    category = rec.meta.category or _infer_category_from_path(rec.path)
    status = rec.meta.status or ("Archived" if "/archive/" in rec.path.replace("\\", "/").lower() else "Active")

    block = (
        f"**Created:** {created}\n"
        f"**Updated:** {updated}\n"
        f"**Author:** {author}\n"
        f"**Tags:** {tags}\n"
        f"**Category:** {category}\n"
        f"**Status:** {status}\n\n"
    )
    return block


def refactor_headers(inventory: list[DocRecord], apply: bool = False, limit: int = 0) -> dict[str, object]:
    """Prepend minimal metadata blocks for docs missing key fields.
    Dry-run by default (apply=False). If limit>0, cap applied changes.
    """
    changed = []
    proposed = []
    applied = 0
    for rec in inventory:
        block = propose_header_fix(rec)
        if not block:
            continue
        proposed.append({"path": rec.path, "block": block})
        if apply and (limit == 0 or applied < limit):
            # If rec.path is absolute (cross-drive), use as-is; else join to repo root
            abs_path = rec.path if os.path.isabs(rec.path) else os.path.join(REPO_ROOT, rec.path)
            try:
                with open(abs_path, encoding="utf-8", errors="ignore") as f:
                    original = f.read()
                # If file already has a header block, we still prepend the missing fields block for simplicity
                with open(abs_path, "w", encoding="utf-8") as f:
                    f.write(block + original)
                changed.append(rec.path)
                applied += 1
            except Exception:
                continue
    # Write suggestions file for review
    _ensure_reports_dir()
    suggestions_path = os.path.join(REPO_ROOT, "docs", "reports", "docs_header_suggestions.md")
    with open(suggestions_path, "w", encoding="utf-8") as f:
        f.write("# Header Suggestions (dry-run by default)\n\n")
        f.write(f"Generated: {datetime.now().isoformat(timespec='seconds')}\n\n")
        for p in proposed:
            f.write(f"## {p['path']}\n\n")
            f.write(p["block"])  # already includes trailing blank line
    return {"proposed": len(proposed), "changed": len(changed), "limit": limit, "applied": applied}


def _parse_header_lines(text: str, scan_lines: int = 120) -> tuple[dict[str, list[tuple[int, str]]], int]:
    """Scan the first N lines and collect occurrences of header key lines.
    Returns a mapping key -> list of (line_index, value) and the index after the first blank line
    which typically delimits the header block.
    """
    lines = text.splitlines()
    limit = min(len(lines), scan_lines)
    occurrences: dict[str, list[tuple[int, str]]] = {k: [] for k in HEADER_KEYS}
    first_blank_after = limit
    for i in range(limit):
        line = lines[i]
        m = HEADER_RE.match(line)
        if m:
            key = m.group(1).capitalize()
            val = m.group(2).strip()
            if key in occurrences:
                occurrences[key].append((i, val))
        if line.strip() == "" and first_blank_after == limit:
            # mark first blank line position
            first_blank_after = i
    return occurrences, first_blank_after


def _normalize_date(date_str: str) -> str:
    """Normalize dates to 'Month Day, Year' when possible."""
    date_str = date_str.strip().strip("*")
    fmts = [
        "%B %d, %Y",  # August 10, 2025
        "%Y-%m-%d",   # 2025-08-10
        "%m/%d/%Y",   # 08/10/2025
        "%d-%b-%Y",   # 10-Aug-2025
        "%Y/%m/%d",
    ]
    for fmt in fmts:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime("%B %d, %Y")
        except Exception:
            continue
    # Try ISO with time
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", ""))
        return dt.strftime("%B %d, %Y")
    except Exception:
        return date_str  # leave as-is if unknown


def _merge_header_values(occ: dict[str, list[tuple[int, str]]]) -> dict[str, str]:
    """Merge duplicate header values with simple rules:
    - Created: keep first occurrence, normalize date
    - Updated: choose the latest parseable date among occurrences, else first
    - Author: keep first
    - Category/Status: keep first
    - Tags: union of all tokens preserving order
    """
    merged: dict[str, str] = {}
    # Created
    if occ["Created"]:
        merged["Created"] = _normalize_date(occ["Created"][0][1])
    # Updated
    if occ["Updated"]:
        best_val = occ["Updated"][0][1]
        best_dt: datetime | None = None
        for _, v in occ["Updated"]:
            nv = _normalize_date(v)
            try:
                dt = datetime.strptime(nv, "%B %d, %Y")
                if not best_dt or dt > best_dt:
                    best_dt = dt
                    best_val = nv
            except Exception:
                # keep textual fallback if unparsable
                if not best_dt:
                    best_val = nv
        merged["Updated"] = best_val
    # Author / Category / Status
    for k in ("Author", "Category", "Status"):
        if occ[k]:
            merged[k] = occ[k][0][1]
    # Tags union
    if occ["Tags"]:
        seen = set()
        ordered: list[str] = []
        for _, v in occ["Tags"]:
            parts = v.split()
            for p in parts:
                if p not in seen:
                    seen.add(p)
                    ordered.append(p)
        merged["Tags"] = " ".join(ordered)
    return merged


def dedup_headers(inventory: list[DocRecord], apply: bool = True, scan_lines: int = 120) -> dict[str, int]:
    """Remove duplicate header lines within the first N lines and rebuild a single normalized block.
    Writes a JSON report with counts and touched files.
    """
    changed = 0
    touched: list[str] = []
    for rec in inventory:
        abs_path = rec.path if os.path.isabs(rec.path) else os.path.join(REPO_ROOT, rec.path)
        if not abs_path.lower().endswith(".md"):
            continue
        try:
            content = _load_file(abs_path)
        except Exception:
            continue
        # Skip YAML front-matter
        if content.lstrip().startswith("---\n"):
            continue

        occ, first_blank = _parse_header_lines(content, scan_lines=scan_lines)
        # Count total occurrences
        total_occ = sum(len(v) for v in occ.values())
        if total_occ <= 1:
            # nothing to dedup
            continue
        merged = _merge_header_values(occ)
        if not merged:
            continue
        # Build normalized header block
        header_lines = []
        for k in HEADER_KEYS:
            if k in merged:
                header_lines.append(f"**{k}:** {merged[k]}")
        new_block = "\n".join(header_lines) + "\n\n"

        # Remove all header lines within scan window and replace with single block at file start
        lines = content.splitlines()
        limit = min(len(lines), scan_lines)
        keep_lines: list[str] = []
        # remove header lines only in the initial header block (up to first blank line)
        header_window = min(first_blank + 1, limit)
        for i in range(header_window):
            line = lines[i]
            if HEADER_RE.match(line):
                continue
            keep_lines.append(line)
        # append the rest of the file unchanged
        keep_lines.extend(lines[header_window:])
        new_content = new_block + "\n".join(keep_lines).lstrip("\n")
        if apply and new_content != content:
            try:
                _save_file(abs_path, new_content)
                changed += 1
                touched.append(rec.path)
            except Exception:
                continue
    # Write report
    _ensure_reports_dir()
    with open(os.path.join(REPO_ROOT, "docs", "reports", "docs_header_dedup.json"), "w", encoding="utf-8") as f:
        json.dump({"changed": changed, "touched": touched}, f, ensure_ascii=False, indent=2)
    return {"changed": changed, "touched": len(touched)}


def _build_inventory_maps(inventory: list[DocRecord]) -> tuple[dict[str, list[str]], list[str]]:
    by_name: dict[str, list[str]] = {}
    # Also build normalized-name map
    by_norm: dict[str, list[str]] = {}
    all_paths: list[str] = []
    for rec in inventory:
        path = rec.path
        all_paths.append(path)
        name = os.path.basename(path)
        by_name.setdefault(name, []).append(path)
        norm = _normalize_basename(name)
        by_norm.setdefault(norm, []).append(path)
    # Pack both maps into a tuple-like payload by abusing typing (documented caller expectations)
    return {"by_name": by_name, "by_norm": by_norm}, all_paths  # type: ignore[return-value]


def _normalize_basename(name: str) -> str:
    s = name.lower()
    # drop extension
    if "." in s:
        s = s.rsplit(".", 1)[0]
    # remove non-alphanumeric
    s = re.sub(r"[^a-z0-9]+", "", s)
    return s


def propose_missing_link_fixes(inventory: list[DocRecord], missing: list[str]) -> dict[str, object]:
    maps, all_paths = _build_inventory_maps(inventory)
    by_name = maps["by_name"]
    by_norm = maps["by_norm"]
    replacements: list[dict[str, object]] = []
    unresolved: list[str] = []
    for m in missing:
        base = os.path.basename(m)
        cand = None
        score = 0.0
        if base in by_name:
            options = by_name[base]
            if len(options) == 1:
                cand = options[0]
                score = 1.0
            else:
                match = difflib.get_close_matches(m, options, n=1, cutoff=0.6)
                if match:
                    cand = match[0]
                    score = difflib.SequenceMatcher(None, m, cand).ratio()
        if not cand:
            # try normalized basename match ignoring punctuation/spaces/case
            n = _normalize_basename(base)
            if by_norm.get(n):
                # Prefer a docs/ path over others if multiple
                opts = sorted(by_norm[n], key=lambda p: (0 if p.startswith("docs/") else 1, len(p)))
                cand = opts[0]
                score = 0.95
        if not cand:
            match = difflib.get_close_matches(m, all_paths, n=1, cutoff=0.7)
            if match:
                cand = match[0]
                score = difflib.SequenceMatcher(None, m, cand).ratio()
        if cand:
            replacements.append({"from": m, "to": cand, "score": round(score, 3)})
        else:
            unresolved.append(m)
    # Write report
    _ensure_reports_dir()
    with open(os.path.join(REPO_ROOT, "docs", "reports", "docs_missing_link_fixes.json"), "w", encoding="utf-8") as f:
        json.dump({"replacements": replacements, "unresolved": unresolved}, f, ensure_ascii=False, indent=2)
    return {"replacements": replacements, "unresolved": unresolved}


def apply_missing_link_fixes(index_path: str, replacements: list[dict[str, str]], max_replacements: int = 0) -> dict[str, int]:
    try:
        content = _load_file(index_path)
    except FileNotFoundError:
        return {"updated": 0}
    # Backup copy in reports
    _ensure_reports_dir()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    _save_file(os.path.join(REPO_ROOT, "docs", "reports", f"DOCUMENTATION_INDEX.backup.{ts}.md"), content)

    # Replace links by rewriting markdown link matches
    applied = 0
    def repl(match: re.Match) -> str:
        title, href = match.group(1), match.group(2)
        for r in replacements:
            if href == r.get("from"):
                nonlocal applied
                if max_replacements and applied >= max_replacements:
                    return match.group(0)
                applied += 1
                return f"[{title}]({r.get('to')})"
        return match.group(0)

    new_content = MD_LINK_RE.sub(repl, content)
    if new_content != content:
        _save_file(index_path, new_content)
        updated = 1
    else:
        updated = 0
    return {"updated": updated, "applied": applied}


SECTION_CANDIDATES = {
    "reference": ["## Reference Documentation"],
    "reports": ["## Documentation"],  # No dedicated Reports section; place under Documentation
    "strategic": ["## Documentation"],  # Fallback
    "process": ["## Process Documentation"],
    "developer": ["## Developer Documentation"],
    "user": ["## User Documentation"],
    "technical": ["## Documentation"],
    "documentation": ["## Documentation"],
    "archive": ["## Archive"],
}


def _infer_index_section_for_path(p: str) -> str | None:
    pl = p.replace("\\", "/").lower()
    if "docs/archive/" in pl:
        return SECTION_CANDIDATES["archive"][0]
    if "docs/reference/" in pl:
        return SECTION_CANDIDATES["reference"][0]
    if "docs/reports/" in pl:
        return SECTION_CANDIDATES["reports"][0]
    if "docs/strategic/" in pl:
        return SECTION_CANDIDATES["strategic"][0]
    if "docs/process/" in pl:
        return SECTION_CANDIDATES["process"][0]
    if "docs/developer/" in pl:
        return SECTION_CANDIDATES["developer"][0]
    if "docs/user/" in pl or "docs/user_guide/" in pl:
        return SECTION_CANDIDATES["user"][0]
    if "docs/technical/" in pl:
        return SECTION_CANDIDATES["technical"][0]
    if "docs/theory/" in pl or "docs/breakthroughs/" in pl or "docs/assets/images/" in pl or "docs/implementation/" in pl or "docs/scripts/" in pl:
        return SECTION_CANDIDATES["documentation"][0]
    if "docs/" in pl:
        return SECTION_CANDIDATES["documentation"][0]
    return None


def categorize_unclassified_additions(index_path: str = INDEX_PATH, max_moves: int = 0) -> dict[str, int]:
    try:
        content = _load_file(index_path)
    except FileNotFoundError:
        return {"moved": 0, "left": 0}

    section_title = "## Unclassified Additions (Automated)"
    if section_title not in content:
        return {"moved": 0, "left": 0}

    # Find block of Unclassified section
    lines = content.splitlines()
    start = None
    for i, line in enumerate(lines):
        if line.strip() == section_title:
            start = i
            break
    if start is None:
        return {"moved": 0, "left": 0}
    end = len(lines)
    for i in range(start + 1, len(lines)):
        if lines[i].startswith("## ") and i > start + 1:
            end = i
            break
    # Collect links in Unclassified
    block = "\n".join(lines[start:end])
    unclassified_links = MD_LINK_RE.findall(block)

    # Build index of existing links OUTSIDE the Unclassified block to avoid duplicates
    content_outside = content.replace(block, "")
    existing_targets_outside = set(m.group(2) for m in MD_LINK_RE.finditer(content_outside))

    moved = 0
    left = 0
    # Prepare mutable content as string for insertions/removals
    content_mut = content

    def _remove_unclassified_entry(text: str, title: str, href: str) -> str:
        # Remove full bullet line variants (with or without bold), plus optional trailing blank line
        # Pattern 1: - **[Title](href)**
        pat_bold = rf"(?m)^\s*-\s*\*\*\s*\[{re.escape(title)}\]\({re.escape(href)}\)\s*\*\*\s*\r?\n(?:\r?\n)?"
        new_text, n = re.subn(pat_bold, "", text)
        if n:
            return new_text
        # Pattern 2: - [Title](href)
        pat_plain = rf"(?m)^\s*-\s*\[{re.escape(title)}\]\({re.escape(href)}\)\s*\r?\n(?:\r?\n)?"
        new_text, _ = re.subn(pat_plain, "", text)
        return new_text

    for title, href in unclassified_links:
        section_header = _infer_index_section_for_path(href)
        if not section_header:
            left += 1
            continue

        # If already present elsewhere, just remove from Unclassified
        if href in existing_targets_outside:
            content_mut = _remove_unclassified_entry(content_mut, title, href)
            moved += 1
            continue

        # Insert under section_header
        m = re.search(re.escape(section_header), content_mut, re.IGNORECASE)
        if not m:
            left += 1
            continue
        # Find insertion point: end of that section, before next '## '
        sec_end = len(content_mut)
        m_end = re.search(r"\n## ", content_mut[m.end():])
        if m_end:
            sec_end = m.end() + m_end.start()
        # Ensure a leading newline
        insertion = f"\n- **[{title}]({href})**\n"
        content_mut = content_mut[:sec_end] + insertion + content_mut[sec_end:]
        # Remove from Unclassified block occurrence (full bullet line)
        content_mut = _remove_unclassified_entry(content_mut, title, href)
        moved += 1
        if max_moves and moved >= max_moves:
            break
        # Track as now existing outside Unclassified for subsequent iterations
        existing_targets_outside.add(href)

    if content_mut != content:
        _save_file(index_path, content_mut)
    return {"moved": moved, "left": left}


def write_index_suggestions(unindexed: list[str]) -> str:
    _ensure_reports_dir()
    out = os.path.join(REPO_ROOT, "docs", "reports", "docs_index_suggestions.md")
    with open(out, "w", encoding="utf-8") as f:
        f.write("# Documentation Index Suggestions\n\n")
        f.write(f"Generated: {datetime.now().isoformat(timespec='seconds')}\n\n")
        f.write("The following files appear unindexed in DOCUMENTATION_INDEX.md. Suggested entries:\n\n")
        for p in unindexed:
            title = os.path.basename(p).replace("_", " ")
            f.write(f"- **[{title}]({p})**\n\n")
    return out


def _load_file(path: str) -> str:
    with open(path, encoding="utf-8", errors="ignore") as f:
        return f.read()


def _save_file(path: str, content: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def apply_index(unindexed: list[str], index_path: str = INDEX_PATH) -> dict[str, int]:
    """Append unindexed entries to DOCUMENTATION_INDEX.md under a dedicated section,
    avoiding duplicates. Does not attempt category placement to keep it safe.
    """
    if not unindexed:
        return {"appended": 0, "skipped": 0}

    try:
        content = _load_file(index_path)
    except FileNotFoundError:
        return {"appended": 0, "skipped": 0}

    section_title = "## Unclassified Additions (Automated)\n"
    if section_title not in content:
        content += "\n\n" + section_title + "\n"

    existing = set()
    for m in MD_LINK_RE.finditer(content):
        existing.add(m.group(2))

    appended = 0
    skipped = 0
    lines_to_add: list[str] = []
    for p in sorted(unindexed):
        if p in existing:
            skipped += 1
            continue
        title = os.path.basename(p).replace("_", " ")
        lines_to_add.append(f"- **[{title}]({p})**\n\n")
        appended += 1

    if appended:
        content += "".join(lines_to_add)
        _save_file(index_path, content)

    return {"appended": appended, "skipped": skipped}


def write_reports(inventory: list[DocRecord], reconciliation: dict[str, object], analysis: dict[str, object]) -> None:
    _ensure_reports_dir()
    inv_path = os.path.join(REPO_ROOT, "docs", "reports", "docs_inventory.json")
    rec_path = os.path.join(REPO_ROOT, "docs", "reports", "docs_reconciliation.json")
    ana_path = os.path.join(REPO_ROOT, "docs", "reports", "docs_analysis.md")

    with open(inv_path, "w", encoding="utf-8") as f:
        json.dump([asdict(r) for r in inventory], f, ensure_ascii=False, indent=2)

    with open(rec_path, "w", encoding="utf-8") as f:
        json.dump(reconciliation, f, ensure_ascii=False, indent=2)

    with open(ana_path, "w", encoding="utf-8") as f:
        f.write("# Documentation Analysis\n\n")
        f.write(f"Generated: {datetime.now().isoformat(timespec='seconds')}\n\n")
        f.write("## Summary\n\n")
        f.write(json.dumps(analysis.get("summary", {}), ensure_ascii=False, indent=2))
        f.write("\n\n## Problems\n\n")
        for p in analysis.get("problems", []):
            f.write(f"- {p['path']}: missing {', '.join(p['missing_fields'])}\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Docs Management & Analysis Toolkit")
    parser.add_argument("command", choices=[
        "inventory",
        "reconcile",
        "analyze",
        "refactor",
        "dedup-headers",
        "fix-missing-links",
        "apply-index",
        "categorize-index",
        "apply-all",
        "all",
    ], nargs="?", default="all")
    parser.add_argument("--root", default=DEFAULT_DOCS_ROOT, help="Root directory to scan (default: ./docs)")
    parser.add_argument("--apply", action="store_true", help="Apply refactor changes (default: dry-run)")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of files to modify when applying changes")
    parser.add_argument("--max-replacements", type=int, default=0, help="Max link replacements to apply in this run (0 = no limit)")
    parser.add_argument("--max-moves", type=int, default=0, help="Max Unclassified moves to apply in this run (0 = no limit)")
    args = parser.parse_args(argv)

    inventory = build_inventory(args.root)
    links = parse_index_links()
    reconciliation = reconcile_index(inventory, links)
    analysis = analyze_content(inventory)

    if args.command == "inventory":
        _ensure_reports_dir()
        with open(os.path.join(REPO_ROOT, "docs", "reports", "docs_inventory.json"), "w", encoding="utf-8") as f:
            json.dump([asdict(r) for r in inventory], f, ensure_ascii=False, indent=2)
        print(f"Inventory: {len(inventory)} files")
        return 0

    if args.command == "reconcile":
        _ensure_reports_dir()
        with open(os.path.join(REPO_ROOT, "docs", "reports", "docs_reconciliation.json"), "w", encoding="utf-8") as f:
            json.dump(reconciliation, f, ensure_ascii=False, indent=2)
        print(
            f"Reconcile: links={reconciliation['linked_count']} files={reconciliation['files_count']} "
            f"missing={len(reconciliation['missing_targets'])} unindexed={len(reconciliation['unindexed_files'])}"
        )
        # Also emit suggestions file to help index updates
        suggestions_path = write_index_suggestions(reconciliation.get("unindexed_files", []))
        print(f"Index suggestions: {suggestions_path}")
        return 0

    if args.command == "analyze":
        _ensure_reports_dir()
        with open(os.path.join(REPO_ROOT, "docs", "reports", "docs_analysis.md"), "w", encoding="utf-8") as f:
            f.write("# Documentation Analysis\n\n")
            f.write(f"Generated: {datetime.now().isoformat(timespec='seconds')}\n\n")
            f.write("## Summary\n\n")
            f.write(json.dumps(analysis.get("summary", {}), ensure_ascii=False, indent=2))
            f.write("\n\n## Problems\n\n")
            for p in analysis.get("problems", []):
                f.write(f"- {p['path']}: missing {', '.join(p['missing_fields'])}\n")
        print(
            f"Analyze: total={analysis['summary']['total']} with_problems={analysis['summary']['with_problems']}"
        )
        return 0

    if args.command == "refactor":
        # Dry-run by default; apply with --apply and optional --limit
        ref = refactor_headers(inventory, apply=args.apply, limit=args.limit)
        # Always write index suggestions in refactor mode
        suggestions_path = write_index_suggestions(reconciliation.get("unindexed_files", []))
        print(
            f"Refactor headers: proposed={ref['proposed']} changed={ref['changed']} "
            f"applied={ref['applied']} limit={ref['limit']}\nIndex suggestions: {suggestions_path}"
        )
        return 0

    if args.command == "dedup-headers":
        res = dedup_headers(inventory, apply=True)
        print(f"Dedup headers: changed={res['changed']} touched={res['touched']}")
        return 0

    if args.command == "fix-missing-links":
        fixes = propose_missing_link_fixes(inventory, reconciliation.get("missing_targets", []))
        if fixes.get("replacements"):
            upd = apply_missing_link_fixes(INDEX_PATH, fixes["replacements"], max_replacements=args.max_replacements)  # type: ignore[arg-type]
            print(
                f"Fix missing links: replacements={len(fixes['replacements'])} unresolved={len(fixes['unresolved'])} updated={upd['updated']} applied={upd.get('applied', 0)}"
            )
        else:
            print(f"Fix missing links: no replacements found; unresolved={len(fixes['unresolved'])}")
        return 0

    if args.command == "categorize-index":
        res = categorize_unclassified_additions(INDEX_PATH, max_moves=args.max_moves)
        print(f"Categorize index: moved={res['moved']} left={res['left']}")
        return 0

    if args.command == "apply-index":
        res = apply_index(reconciliation.get("unindexed_files", []), INDEX_PATH)
        print(f"Apply index: appended={res['appended']} skipped={res['skipped']}")
        return 0

    if args.command == "apply-all":
        ref = refactor_headers(inventory, apply=True, limit=args.limit)
        res = apply_index(reconciliation.get("unindexed_files", []), INDEX_PATH)
        print(
            f"Apply-all: headers_applied={ref['applied']} (proposed={ref['proposed']}) index_appended={res['appended']} skipped={res['skipped']}"
        )
        return 0

    # default: all
    write_reports(inventory, reconciliation, analysis)
    suggestions_path = write_index_suggestions(reconciliation.get("unindexed_files", []))
    print(
        f"Done: inventory={len(inventory)} links={reconciliation['linked_count']} "
        f"missing={len(reconciliation['missing_targets'])} unindexed={len(reconciliation['unindexed_files'])}\n"
        f"Index suggestions: {suggestions_path}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
