"""Lightweight Documentation Indexer Placeholder

Purpose:
    Temporary indexer to allow IDS tooling to rebuild search indices for newly
    added documentation tags until the full historical indexer is restored.

Functionality:
    - Scans `docs/` and `src/memlog/` for markdown files.
    - Extracts first-level heading and any inline hash tags (#word) from the
      first 40 lines.
    - Builds a minimal JSON index with fields: path, title, tags.
    - Writes to `docs/_lightweight_index.json`.

Limitations:
    Does not perform deep content tokenization or category inference. Intended
    only to surface new tag tokens (e.g., #checkpoint_governance) to IDS.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / 'docs'
MEMLOG = ROOT / 'src' / 'memlog'
OUTPUT = DOCS / '_lightweight_index.json'

TAG_PATTERN = re.compile(r'#([A-Za-z0-9_\-]+)')
TITLE_PATTERN = re.compile(r'^#\s+(.+)$')


def extract_meta(path: Path) -> dict:
    try:
        text = path.read_text(encoding='utf-8', errors='ignore')
    except Exception:
        return {"path": str(path), "title": None, "tags": []}
    lines = text.splitlines()[:40]
    title = None
    tags: set[str] = set()
    for ln in lines:
        if not title:
            m = TITLE_PATTERN.match(ln.strip())
            if m:
                title = m.group(1).strip()
        for t in TAG_PATTERN.findall(ln):
            tags.add(t.lower())
    return {"path": str(path.relative_to(ROOT)).replace('\\', '/'), "title": title, "tags": sorted(tags)}


def build_index():
    candidates = []
    for base in (DOCS, MEMLOG):
        if not base.exists():
            continue
        for p in base.rglob('*.md'):
            candidates.append(extract_meta(p))
    index = {
        "generated_at": datetime.now().strftime("%B %d, %Y %I:%M:%S %p"),
        "total_files": len(candidates),
        "entries": candidates,
        "note": "Lightweight indexer output (temporary)"
    }
    OUTPUT.write_text(json.dumps(index, indent=2), encoding='utf-8')
    return index


def main():  # pragma: no cover
    idx = build_index()
    print(f"Lightweight documentation index written: {OUTPUT} ({idx['total_files']} files)")


if __name__ == '__main__':  # pragma: no cover
    main()
