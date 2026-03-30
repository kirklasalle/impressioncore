#!/usr/bin/env python3
"""Generate a markdown table of registered models.

Writes/prints a table listing model key and class name (if instantiable).
Intended to be lightweight; avoids full heavy imports by trying factories
and catching exceptions.
"""
from __future__ import annotations

import os
import sys

# Ensure 'src' directory is on sys.path for direct execution contexts
_here = os.path.abspath(os.path.dirname(__file__))
_repo_root = os.path.abspath(os.path.join(_here, '..', '..'))  # dev_tools -> src -> repo root
_src_root = os.path.join(_repo_root, 'src')
if _src_root not in sys.path:
    sys.path.insert(0, _src_root)
import re
from pathlib import Path

from core.models.registry import get_metadata, get_model, list_models  # type: ignore


def build_table():
    rows = ["| Name | Class | Status | Param Estimate | Version |", "|------|-------|--------|----------------|---------|"]
    for name in list_models():
        try:
            payload = get_model(name)
            inst = payload.get('instance', payload)
            cls_name = inst.__class__.__name__
        except Exception as e:  # pragma: no cover
            cls_name = f"(error: {e.__class__.__name__})"
        meta = get_metadata(name) or {}
        status = meta.get('status', '-')
        params = meta.get('param_estimate', '-')
        version = meta.get('version', '-')
        rows.append(f"| {name} | {cls_name} | {status} | {params} | {version} |")
    return "\n".join(rows)

MARKER_START = "<!-- MODEL_REGISTRY_TABLE_START -->"
MARKER_END = "<!-- MODEL_REGISTRY_TABLE_END -->"


def update_readme(readme_path: str = "README.md", check: bool = False) -> int:
    path = Path(readme_path)
    if not path.exists():
        tbl = build_table()
        if check:
            print("README missing; would create table.")
            return 1
        print(tbl)
        return 0
    content = path.read_text(encoding='utf-8')
    table = build_table()
    block = f"{MARKER_START}\n{table}\n{MARKER_END}"
    if MARKER_START in content and MARKER_END in content:
        updated = re.sub(f"{MARKER_START}.*?{MARKER_END}", block, content, flags=re.DOTALL)
    else:
        updated = content + f"\n\n{block}\n"
    if check:
        if updated != content:
            print("Model registry table out of date.")
            return 1
        print("Model registry table up to date.")
        return 0
    path.write_text(updated, encoding='utf-8')
    print("Updated README with model registry table.")
    return 0


if __name__ == '__main__':  # pragma: no cover
    import argparse
    import sys
    ap = argparse.ArgumentParser(description="Generate/verify model registry table in README.")
    ap.add_argument('--check', action='store_true', help='Verify table is current (non-zero exit if stale)')
    ap.add_argument('--readme', type=str, default='README.md')
    args = ap.parse_args()
    code = update_readme(args.readme, check=args.check)
    sys.exit(code)
