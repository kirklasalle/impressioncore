"""
ImpressionCore Documentation Indexer Wrapper (with fallback)

Purpose: Provide a stable entrypoint at src/dev_tools/documentation_indexer.py
so IDS automation tools can trigger a documentation index rebuild.

Strategy:
- Attempt to import and execute the archived indexer if present at
  src/archive/archive/dev_tools/documentation_indexer.py.
- If unavailable or invalid, run a lightweight fallback indexer that scans
  docs/ and src/memlog/ to produce JSON snapshot stats and tags.

Outputs (fallback):
- docs/reports/ids_index_snapshot_YYYYMMDD_HHMMSS.json
- docs/reports/ids_tags_snapshot_YYYYMMDD_HHMMSS.json

This wrapper avoids external dependencies and keeps behavior deterministic.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import runpy
import sys
import yaml
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Iterable


# Ensure stdout/stderr won't crash on Windows when printing Unicode.
try:  # Python 3.7+
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def _safe_print(msg: str) -> None:
    """Print with robust Unicode handling on Windows consoles.

    Falls back to backslashescape if the console cannot render characters.
    """
    try:
        print(msg)
    except Exception:
        try:
            # Encode with backslashreplace to avoid encode errors
            safe = msg.encode("utf-8", errors="backslashreplace").decode("utf-8", errors="ignore")
            print(safe)
        except Exception:
            # Last resort: strip to ASCII
            print(msg.encode("ascii", errors="ignore").decode("ascii", errors="ignore"))


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _archived_indexer_path(root: Path) -> Path:
    # Known archived path discovered during system validation
    return root / "src" / "archive" / "archive" / "dev_tools" / "documentation_indexer.py"


def _iter_markdown_files(paths: Iterable[Path]) -> Iterable[Path]:
    for base in paths:
        if not base.exists():
            continue
        for p in base.rglob("*.md"):
            # Skip archived duplicates if scanning outside docs/archive as needed
            yield p


_TAG_RE = re.compile(r"^\s*\*\*Tags:\*\*\s*(.+)$", re.IGNORECASE)
_CREATED_RE = re.compile(r"^\s*\*\*Created:\*\*\s*(.+)$", re.IGNORECASE)
_UPDATED_RE = re.compile(r"^\s*\*\*Updated:\*\*\s*(.+)$", re.IGNORECASE)


def _parse_header_lines(lines: Iterable[str]) -> dict:
    data: dict[str, object] = {}
    for line in lines:
        if "Tags:" in line:
            m = _TAG_RE.match(line.strip())
            if m:
                # tags separated by spaces; items often prefixed with '#'
                raw = m.group(1)
                tags = [t.strip() for t in re.split(r"[\s,]", raw) if t.strip()]
                data["tags"] = tags
        elif "Created:" in line:
            m = _CREATED_RE.match(line.strip())
            if m:
                data["created_raw"] = m.group(1).strip()
        elif "Updated:" in line:
            m = _UPDATED_RE.match(line.strip())
            if m:
                data["updated_raw"] = m.group(1).strip()
        # Limit header scan to first ~40 lines
        if len(getattr(data, "_lines_scanned", [])) > 40:
            break
    return data


def _fallback_index(root: Path) -> tuple[dict, dict, dict, dict, dict]:
    docs_dir = root / "docs"
    memlog_dir = root / "src" / "memlog"

    files = list(_iter_markdown_files([docs_dir, memlog_dir]))
    tag_counter: Counter[str] = Counter()

    file_summaries = []
    file_metadata = {}
    reverse_index = defaultdict(list)
    unified_index = {}
    for path in files:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        head = text.splitlines()[:50]
        meta = _parse_header_lines(head)
        tags = [t for t in meta.get("tags", []) if t]
        tag_counter.update(tags)
        rel_path = str(path.relative_to(root))
        file_summaries.append(
            {
                "path": rel_path,
                "tags": tags,
                "created": meta.get("created_raw"),
                "updated": meta.get("updated_raw"),
            }
        )
        # Build file_metadata and reverse_index for YAML
        file_metadata[rel_path] = {
            "tags": tags,
            "created": meta.get("created_raw"),
            "updated": meta.get("updated_raw"),
        }
        for tag in tags:
            reverse_index[tag].append(rel_path)

    # Unified index: tag → list of files
    for tag, rel_files in reverse_index.items():
        unified_index[tag] = rel_files

    stats = {
        "generated_at": datetime.now().strftime("%Y%m%d_%H%M%S"),
        "total_files": len(files),
        "docs_files": len([p for p in files if docs_dir in p.parents or p.parent == docs_dir]),
        "memlog_files": len([p for p in files if memlog_dir in p.parents or p.parent == memlog_dir]),
        "top_tags": tag_counter.most_common(50),
    }

    tags_payload = {
        "generated_at": stats["generated_at"],
        "tags": [t for t, _ in tag_counter.most_common()],
        "counts": dict(tag_counter),
    }

    return stats | {"files": file_summaries}, tags_payload, unified_index, file_metadata, dict(reverse_index)


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

def _write_yaml(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(payload, f, allow_unicode=True, sort_keys=False)


def _run_archived_or_fallback(root: Path, argv: list[str], use_archived: bool = False) -> int:
    candidate = _archived_indexer_path(root)
    if use_archived and candidate.is_file():
        # Attempt to execute archived indexer; may fail if file contains non-Python markers
        saved_argv = sys.argv[:]
        try:
            sys.argv = [str(candidate)] + argv
            runpy.run_path(str(candidate), run_name="__main__")
            return 0
        except SyntaxError as e:
            _safe_print(f"[documentation_indexer] Archived indexer invalid Python: {e}")
        except Exception as e:
            _safe_print(f"[documentation_indexer] Archived indexer execution failed: {e}")
        finally:
            sys.argv = saved_argv

    # Fallback path
    stats, tags_payload, unified_index, file_metadata, reverse_index = _fallback_index(root)
    ts = stats.get("generated_at")
    out_dir = root / "docs" / "reports"
    _write_json(out_dir / f"ids_index_snapshot_{ts}.json", stats)
    _write_json(out_dir / f"ids_tags_snapshot_{ts}.json", tags_payload)
    # Write YAML indices for IDS server
    yaml_dir = root / "docs"
    _write_yaml(yaml_dir / "unified_tags_index.yaml", unified_index)
    _write_yaml(yaml_dir / "file_metadata.yaml", file_metadata)
    _write_yaml(yaml_dir / "reverse_tag_index.yaml", reverse_index)
    _safe_print(
        "[documentation_indexer] Fallback index generated →\n"
        f"  - {out_dir / f'ids_index_snapshot_{ts}.json'}\n"
        f"  - {out_dir / f'ids_tags_snapshot_{ts}.json'}\n"
        f"  - {yaml_dir / 'unified_tags_index.yaml'}\n"
        f"  - {yaml_dir / 'file_metadata.yaml'}\n"
        f"  - {yaml_dir / 'reverse_tag_index.yaml'}"
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    argv = argv or sys.argv[1:]
    parser = argparse.ArgumentParser(description="ImpressionCore Documentation Indexer Wrapper")
    parser.add_argument("--fallback", action="store_true", help="Force fallback scanner even if archived indexer exists")
    parser.add_argument("--use-archived", action="store_true", help="Explicitly run archived indexer (opt-in)")
    args, passthrough = parser.parse_known_args(argv)

    root = _repo_root()
    if args.fallback:
        stats, tags_payload, unified_index, file_metadata, reverse_index = _fallback_index(root)
        ts = stats.get("generated_at")
        out_dir = root / "docs" / "reports"
        _write_json(out_dir / f"ids_index_snapshot_{ts}.json", stats)
        _write_json(out_dir / f"ids_tags_snapshot_{ts}.json", tags_payload)
        yaml_dir = root / "docs"
        _write_yaml(yaml_dir / "unified_tags_index.yaml", unified_index)
        _write_yaml(yaml_dir / "file_metadata.yaml", file_metadata)
        _write_yaml(yaml_dir / "reverse_tag_index.yaml", reverse_index)
        _safe_print(f"[documentation_indexer] Fallback index generated at {ts} (YAML written)")
        return 0

    # Default: do NOT run archived indexer unless explicitly requested or env var set
    use_archived = args.use_archived or os.environ.get("USE_ARCHIVED_INDEXER") == "1"
    return _run_archived_or_fallback(root, passthrough, use_archived=use_archived)


if __name__ == "__main__":
    raise SystemExit(main())
