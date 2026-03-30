"""File Integrity Hash Index
Created: August 22, 2025
Author: GitHub Copilot

Covers Category 3 (Data Quality & Integrity) + Category 9 (Safety & Failure Handling).
Maintains a JSON hash manifest for embedding/data files to detect corruption.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


class HashIndex:
    def __init__(self, root: Path, manifest_path: Path):
        self.root = root
        self.manifest_path = manifest_path
        self.index: dict[str, str] = {}
        if manifest_path.exists():
            try:
                self.index = json.loads(manifest_path.read_text(encoding='utf-8'))
            except Exception:
                self.index = {}

    def _hash_file(self, path: Path) -> str:
        h = hashlib.sha256()
        with path.open('rb') as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b''):
                h.update(chunk)
        return h.hexdigest()

    def build_or_update(self, pattern: str = '**/*.npy', limit: int | None = None):
        files = list(self.root.glob(pattern))
        if limit:
            files = files[:limit]
        updated = 0
        for p in files:
            try:
                digest = self._hash_file(p)
                if self.index.get(p.as_posix()) != digest:
                    self.index[p.as_posix()] = digest
                    updated += 1
            except Exception:
                continue
        self.manifest_path.parent.mkdir(parents=True, exist_ok=True)
        self.manifest_path.write_text(json.dumps(self.index, indent=2), encoding='utf-8')
        return updated, len(files)

    def verify(self, fast: bool = False):
        mismatches = []
        for rel, digest in list(self.index.items()):
            p = Path(rel)
            if not p.exists():
                mismatches.append(rel)
                continue
            if fast:
                continue
            new_digest = self._hash_file(p)
            if new_digest != digest:
                mismatches.append(rel)
        return mismatches
