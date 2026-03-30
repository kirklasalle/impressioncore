"""Generate a chronological documentation index.

Scans the `docs/` tree (excluding `docs/archive/`) for Markdown files, extracts the
`Created:` and `Updated:` metadata lines (Month Day, Year format), and produces a
chronologically sorted index file at `docs/CHRONOLOGICAL_INDEX.md`.

Ordering rule:
- Primary sort: Created date ascending
- Secondary sort: Updated date (if present) ascending
- Tertiary: path lexical

Date parsing:
- Expected format: Month Day, Year (standard project format)
- Fallbacks supported for legacy ISO (YYYY-MM-DD) or dashed (Month-Day-Year) with warning

Usage (PowerShell):
  .venv310\Scripts\activate
  python -m src.dev_tools.docs.generate_chronological_index

Optional args:
  --reverse            (newest first)
  --include-archive    (also include docs/archive)
  --limit N            (only first N entries)

The output file includes a compact timeline plus detailed table.
"""
from __future__ import annotations
import argparse
import re
import os
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Tuple
import hashlib

# --- Enhancement: incremental diff support & hashing ---
PREVIOUS_JSON = 'chronology_index.json'
DIFF_JSON = 'chronology_index_diff.json'
SCHEMA_VERSION = '1.0-baseline'

_HERE = Path(__file__).resolve()

def _find_project_root(start: Path) -> Path:
    """Ascend until a directory containing 'docs' and 'src' exists.

    Falls back to 4th parent (original heuristic) if not found.
    """
    cur = start
    for _ in range(10):  # safety bound
        if (cur / 'docs').is_dir() and (cur / 'src').is_dir():
            return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    # Fallback to prior heuristic
    try:
        return start.parents[4]
    except Exception:
        return start.parent.parent  # last resort

ROOT = _find_project_root(_HERE)
DOCS_DIR = ROOT / 'docs'
OUT_FILE = DOCS_DIR / 'CHRONOLOGICAL_INDEX.md'

CREATED_RE = re.compile(r'^\*\*Created:\*\*\s*(.+)$', re.IGNORECASE)
UPDATED_RE = re.compile(r'^\*\*Updated:\*\*\s*(.+)$', re.IGNORECASE)
CREATED_INLINE_RE = re.compile(r'^(?:#|//)\s*Created:\s*(.+)$', re.IGNORECASE)
DATE_HUMAN_FMT = '%B %d, %Y'
DATE_LEGACY_ISO = '%Y-%m-%d'
DATE_DEPRECATED_DASH = '%B-%d-%Y'
DATE_FORMATS = [
    DATE_HUMAN_FMT,        # August 15, 2025
    DATE_LEGACY_ISO,       # 2025-08-15 (legacy)
    DATE_DEPRECATED_DASH,  # August-15-2025 (deprecated)
]
ISO_TS_FMT = '%Y-%m-%dT%H:%M:%SZ'
TABLE_DOC_HEADER = '| Created | Updated | Title | Path |'
TABLE_GENERIC_HEADER = '| Created | Updated | Name | Path |'
TABLE_DIVIDER = '|---------|---------|------|------|'

@dataclass
class DocEntry:
    path: Path
    created: Optional[datetime]
    updated: Optional[datetime]
    title: str

    @property
    def rel(self) -> str:
        return str(self.path.relative_to(ROOT)).replace('\\', '/')

    def created_str(self) -> str:
        return self.created.strftime(DATE_HUMAN_FMT) if self.created else 'UNKNOWN'

    def updated_str(self) -> str:
        return self.updated.strftime(DATE_HUMAN_FMT) if self.updated else '—'


def parse_date(raw: str) -> Optional[datetime]:
    raw = raw.strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            continue
    return None


def extract_metadata(path: Path) -> Tuple[Optional[datetime], Optional[datetime]]:
    """Extract first (outer header) Created/Updated.

    Some docs contain duplicated metadata blocks (outer standardized header + inner legacy section).
    We only want the FIRST Created/Updated pair to represent the document's canonical dates.
    Scan first 120 lines to be tolerant of slightly longer lead-in blocks.
    """
    created = updated = None
    try:
        with path.open('r', encoding='utf-8', errors='ignore') as f:
            for i, line in enumerate(f):
                if i > 150:
                    break
                s = line.strip()
                if created is None:
                    # Markdown style
                    m = CREATED_RE.match(s)
                    if m:
                        created = parse_date(m.group(1))
                    # Inline comment style (# Created: ... or // Created: ...)
                    if created is None:
                        m_inline = CREATED_INLINE_RE.match(s)
                        if m_inline:
                            created = parse_date(m_inline.group(1))
                if updated is None:
                    m2 = UPDATED_RE.match(s)
                    if m2:
                        updated = parse_date(m2.group(1))
                if created and updated:
                    break
    except Exception:
        pass
    return created, updated


def derive_title(path: Path) -> str:
    try:
        with path.open('r', encoding='utf-8', errors='ignore') as f:
            for i, line in enumerate(f):
                if i > 120:
                    break
                if line.startswith('# '):
                    return line[2:].strip()
    except Exception:
        pass
    return path.stem


def collect(include_archive: bool) -> List[DocEntry]:
    entries: List[DocEntry] = []
    for p in DOCS_DIR.rglob('*.md'):
        rp = str(p).replace('\\', '/')
        if not include_archive and '/archive/' in rp:
            continue
        if p.name.lower() == 'chronological_index.md':  # skip self
            continue
        created, updated = extract_metadata(p)
        title = derive_title(p)
        entries.append(DocEntry(path=p, created=created, updated=updated, title=title))
    return entries


# ---------------- Source File Chronology ---------------- #
SRC_EXTENSIONS = {'.py', '.md', '.json', '.yml', '.yaml'}

# Additional roots for comprehensive chronology beyond docs + src
MCP_DIR = ROOT / '.mcp'
ROOT_CODE_EXT = {'.py', '.md'}  # top-level code/docs of interest

def collect_mcp() -> List[DocEntry]:
    entries: List[DocEntry] = []
    if not MCP_DIR.exists():
        return entries
    for p in MCP_DIR.rglob('*'):
        if not p.is_file():
            continue
        if p.suffix.lower() not in SRC_EXTENSIONS:
            continue
        created, updated = extract_metadata(p)
        if created is None or updated is None:
            try:
                stat = p.stat(); fs_time = datetime.fromtimestamp(stat.st_mtime)
                if created is None: created = fs_time
                if updated is None: updated = fs_time
            except Exception:
                pass
        title = derive_title(p) if p.suffix.lower() == '.md' else p.stem
        entries.append(DocEntry(path=p, created=created, updated=updated, title=title))
    return entries

def collect_root_scripts() -> List[DocEntry]:
    entries: List[DocEntry] = []
    for p in ROOT.iterdir():
        if not p.is_file():
            continue
        if p.suffix.lower() not in ROOT_CODE_EXT:
            continue
        if p.name.lower().startswith('readme'):
            # README already covered in docs directory typically; skip duplicates
            pass
        created, updated = extract_metadata(p)
        if created is None or updated is None:
            try:
                stat = p.stat(); fs_time = datetime.fromtimestamp(stat.st_mtime)
                if created is None: created = fs_time
                if updated is None: updated = fs_time
            except Exception:
                pass
        title = derive_title(p) if p.suffix.lower() == '.md' else p.stem
        entries.append(DocEntry(path=p, created=created, updated=updated, title=title))
    return entries

def collect_source() -> List[DocEntry]:
    src_dir = ROOT / 'src'
    entries: List[DocEntry] = []
    for p in src_dir.rglob('*'):
        if not p.is_file():
            continue
        if p.suffix.lower() not in SRC_EXTENSIONS:
            continue
        created, updated = extract_metadata(p)
        # Fallback to filesystem times if metadata missing
        if created is None or updated is None:
            try:
                stat = p.stat()
                fs_time = datetime.fromtimestamp(stat.st_mtime)
                if created is None:
                    created = fs_time
                if updated is None:
                    updated = fs_time
            except Exception:
                pass
        title = derive_title(p) if p.suffix.lower() == '.md' else p.stem
        entries.append(DocEntry(path=p, created=created, updated=updated, title=title))
    return entries


def sort_entries(entries: List[DocEntry], reverse: bool, created_only: bool = False) -> List[DocEntry]:
    def key(e: DocEntry):
        sentinel = datetime(2999, 12, 31)
        c = e.created or sentinel
        if created_only:
            return (c, e.rel)
        u = e.updated or c
        return (c, u, e.rel)
    return sorted(entries, key=key, reverse=reverse)


def render(entries: List[DocEntry], reverse: bool, source_entries: Optional[List[DocEntry]] = None,
           mcp_entries: Optional[List[DocEntry]] = None, root_entries: Optional[List[DocEntry]] = None) -> str:
    direction = 'Newest → Oldest' if reverse else 'Oldest → Newest'
    lines = []
    lines.append('**Created:** August 15, 2025')
    lines.append('**Updated:** August 15, 2025')
    lines.append('**Author:** GitHub Copilot')
    lines.append('**Tags:** #docs/chono_index #automation #timeline #documentation #governance')
    lines.append('**Category:** Documentation')
    lines.append('**Status:** Active')
    lines.append(f'**Schema Version:** {SCHEMA_VERSION}')
    lines.append('')
    lines.append('# Chronological Documentation Index')
    lines.append('')
    lines.append(f'Ordering: {direction}')
    lines.append('')
    lines.append('> Auto-generated. Do not hand-edit. Run generator to refresh.')
    lines.append('')
    lines.append('## Documentation Timeline')
    lines.append('')
    for e in entries:
        lines.append(f"- {e.created_str()} | {e.title} | `{e.rel}`")
    lines.append('')
    lines.append('## Documentation Detailed Table (Created is canonical)')
    lines.append('')
    lines.append(TABLE_DOC_HEADER)
    lines.append('|---------|---------|-------|------|')
    for e in entries:
        lines.append(f"| {e.created_str()} | {e.updated_str()} | {e.title} | `{e.rel}` |")
    lines.append('')
    if source_entries:
        lines.append('')
        lines.append('## Source Code Timeline')
        lines.append('')
        for e in source_entries:
            lines.append(f"- {e.created_str()} | {e.title} | `{e.rel}`")
        lines.append('')
        lines.append('## Source Code Detailed Table')
        lines.append('')
        lines.append(TABLE_GENERIC_HEADER)
        lines.append(TABLE_DIVIDER)
        for e in source_entries:
            lines.append(f"| {e.created_str()} | {e.updated_str()} | {e.title} | `{e.rel}` |")
    if mcp_entries:
        lines.append('')
        lines.append('## MCP Server & Tools Timeline')
        lines.append('')
        for e in mcp_entries:
            lines.append(f"- {e.created_str()} | {e.title} | `{e.rel}`")
        lines.append('')
        lines.append('## MCP Server & Tools Detailed Table')
        lines.append('')
        lines.append(TABLE_GENERIC_HEADER)
        lines.append(TABLE_DIVIDER)
        for e in mcp_entries:
            lines.append(f"| {e.created_str()} | {e.updated_str()} | {e.title} | `{e.rel}` |")
    if root_entries:
        lines.append('')
        lines.append('## Root-Level Scripts & Docs Timeline')
        lines.append('')
        for e in root_entries:
            lines.append(f"- {e.created_str()} | {e.title} | `{e.rel}`")
        lines.append('')
        lines.append('## Root-Level Scripts & Docs Detailed Table')
        lines.append('')
        lines.append(TABLE_GENERIC_HEADER)
        lines.append(TABLE_DIVIDER)
        for e in root_entries:
            lines.append(f"| {e.created_str()} | {e.updated_str()} | {e.title} | `{e.rel}` |")
    lines.append('')
    lines.append('---')
    lines.append('Generated by `src/dev_tools/docs/generate_chronological_index.py` (docs + source chronology).')
    return '\n'.join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--reverse', action='store_true', help='Newest first')
    ap.add_argument('--exclude-archive', action='store_true', help='Exclude archived docs (default includes)')
    # Source inclusion now baseline by default (docs + src always)
    ap.add_argument('--no-source', action='store_true', help='Exclude source code chronology section (override baseline)')
    ap.add_argument('--with-mcp', action='store_true', help='Include .mcp server/tool chronology')
    ap.add_argument('--with-root', action='store_true', help='Include root-level scripts chronology')
    ap.add_argument('--all', action='store_true', help='Shortcut: include source + mcp + root')
    ap.add_argument('--json-out', action='store_true', help='Emit machine-readable JSON timeline at docs/timelines/chronology_index.json for IDS ingestion')
    ap.add_argument('--delta', action='store_true', help='Also produce a diff JSON (changes vs previous chronology)')
    ap.add_argument('--created-only', action='store_true', help='Order strictly by Created date; ignore Updated in ordering')
    ap.add_argument('--limit', type=int, help='Limit number of entries')
    args = ap.parse_args()

    entries = collect(include_archive=not args.exclude_archive)
    entries = sort_entries(entries, reverse=args.reverse, created_only=args.created_only)
    if args.limit:
        entries = entries[:args.limit]
    # Baseline always includes source unless explicitly disabled
    include_source = (not args.no_source)
    include_mcp = args.with_mcp or args.all
    include_root = args.with_root or args.all
    source_entries: Optional[List[DocEntry]] = None
    mcp_entries: Optional[List[DocEntry]] = None
    root_entries: Optional[List[DocEntry]] = None
    if include_source:
        source_entries = sort_entries(collect_source(), reverse=args.reverse, created_only=args.created_only)
    if include_mcp:
        mcp_entries = sort_entries(collect_mcp(), reverse=args.reverse, created_only=args.created_only)
    if include_root:
        root_entries = sort_entries(collect_root_scripts(), reverse=args.reverse, created_only=args.created_only)
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(
        render(entries, reverse=args.reverse, source_entries=source_entries, mcp_entries=mcp_entries, root_entries=root_entries),
        encoding='utf-8'
    )
    print(f'[chronological-index] Wrote {OUT_FILE} (docs={len(entries)} src={len(source_entries) if source_entries else 0} mcp={len(mcp_entries) if mcp_entries else 0} root={len(root_entries) if root_entries else 0})')

    if args.json_out:
        timeline_dir = DOCS_DIR / 'timelines'
        timeline_dir.mkdir(parents=True, exist_ok=True)
        json_path = timeline_dir / PREVIOUS_JSON
        def serialize(e: DocEntry):
            # Stable hash (path + created + updated)
            h = hashlib.sha1(f"{e.rel}|{e.created_str()}|{e.updated_str()}".encode('utf-8')).hexdigest()[:10]
            return {
                'path': e.rel,
                'title': e.title,
                'created': e.created_str(),
                'updated': e.updated_str(),
                'hash': h,
                'type': 'source' if source_entries and any(e is se for se in source_entries) and 'docs/' not in e.rel else 'doc'
            }
        payload = {
            'schema_version': SCHEMA_VERSION,
            'generated': datetime.now(timezone.utc).strftime(ISO_TS_FMT),
            'ordering': 'reverse' if args.reverse else 'forward',
            'documents': [serialize(e) for e in entries],
            'source': [serialize(e) for e in (source_entries or [])],
        }
        # Only add extended domains if explicitly requested
        if mcp_entries:
            payload['mcp'] = [serialize(e) for e in mcp_entries]
        if root_entries:
            payload['root'] = [serialize(e) for e in root_entries]
        json_path.write_text(json.dumps(payload, indent=2), encoding='utf-8')
        print(f'[chronological-index] Wrote JSON {json_path}')

        if args.delta:
            # Produce diff relative to previous existing file (if any old snapshot saved as *.prev)
            prev_path = timeline_dir / PREVIOUS_JSON
            diff_path = timeline_dir / DIFF_JSON
            added = []
            removed = []
            changed = []
            try:
                if prev_path.exists():
                    # Load previous snapshot BEFORE overwrite? We already overwrote; attempt to load backup if exists
                    # Strategy: maintain a backup copy named chronology_index_prev.json BEFORE writing new one
                    backup_prev = timeline_dir / 'chronology_index_prev.json'
                    if backup_prev.exists():
                        prev_data = json.loads(backup_prev.read_text(encoding='utf-8'))
                    else:
                        prev_data = payload  # first run fallback
                else:
                    prev_data = payload
            except Exception:
                prev_data = payload
            # Build maps by path
            def map_by_path(arr):
                return {x['path']: x for x in arr}
            cur_all = {**map_by_path(payload['documents']), **map_by_path(payload['source']), **map_by_path(payload['mcp']), **map_by_path(payload['root'])}
            prev_all = {**map_by_path(prev_data.get('documents', [])), **map_by_path(prev_data.get('source', [])), **map_by_path(prev_data.get('mcp', [])), **map_by_path(prev_data.get('root', []))}
            for pth, meta in cur_all.items():
                if pth not in prev_all:
                    added.append(meta)
                else:
                    if meta.get('hash') != prev_all[pth].get('hash'):
                        changed.append({'before': prev_all[pth], 'after': meta})
            for pth, meta in prev_all.items():
                if pth not in cur_all:
                    removed.append(meta)
            diff_payload = {
                'generated': payload['generated'],
                'added': added,
                'removed': removed,
                'changed': changed,
                'counts': {
                    'added': len(added),
                    'removed': len(removed),
                    'changed': len(changed)
                }
            }
            diff_path.write_text(json.dumps(diff_payload, indent=2), encoding='utf-8')
            # Save backup of current snapshot for next run comparison
            backup_prev = timeline_dir / 'chronology_index_prev.json'
            backup_prev.write_text(json.dumps(payload, indent=2), encoding='utf-8')
            print(f'[chronological-index] Wrote diff {diff_path} (added={len(added)} changed={len(changed)} removed={len(removed)})')

if __name__ == '__main__':  # pragma: no cover
    main()
