#!/usr/bin/env python3
"""Checkpoint audit & prune utility

Usage:
  python tools/ckpt_manager.py audit --dir F:/models/checkpoints --out ckpts.csv
  python tools/ckpt_manager.py prune --dir F:/models/checkpoints --policy keep_latest:3 --archive F:/models/checkpoints/archive --dry-run

This tool is conservative by default: pruning is a dry-run unless --apply is given.
It attempts to read small metadata from PyTorch .pth files (map_location='cpu') and will skip files it cannot read.

"""
from __future__ import annotations

import argparse
import csv
import gc
import shutil
import sys
from pathlib import Path
from typing import Any

try:
    import torch
except Exception:
    torch = None


def scan_checkpoints(directory: Path) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for p in sorted(directory.rglob('*.pth')):
        try:
            st = p.stat()
        except Exception:
            continue
        row: dict[str, Any] = {
            'path': str(p),
            'size_bytes': st.st_size,
            'mtime': st.st_mtime,
            'read_error': '',
            'global_step': None,
            'best_loss': None,
            'timestamp': None,
            'total_params': None,
        }
        if torch:
            try:
                ckpt = torch.load(str(p), map_location='cpu')
                # extract common keys if present
                row['global_step'] = int(ckpt.get('global_step')) if isinstance(ckpt.get('global_step'), int) else None
                # best_loss may be None or float
                try:
                    row['best_loss'] = float(ckpt.get('best_loss')) if ('best_loss' in ckpt and ckpt.get('best_loss') is not None) else None
                except Exception:
                    row['best_loss'] = None
                row['timestamp'] = ckpt.get('timestamp') if 'timestamp' in ckpt else None
                row['total_params'] = int(ckpt.get('total_params')) if 'total_params' in ckpt and ckpt.get('total_params') is not None else None
                # free memory asap
                del ckpt
                gc.collect()
            except Exception as e:
                row['read_error'] = str(e)
        else:
            row['read_error'] = 'torch_not_available'
        results.append(row)
    return results


def write_csv(rows: list[dict[str, Any]], outpath: Path):
    fieldnames = ['path', 'size_bytes', 'mtime', 'global_step', 'best_loss', 'timestamp', 'total_params', 'read_error']
    with open(outpath, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k) for k in fieldnames})


def select_prune_candidates(rows: list[dict[str, Any]], policy: str) -> list[str]:
    """Simple policy parser:
    - keep_latest:N  -> keep latest N files (by mtime), prune others
    - keep_best_per_prefix:N -> for files grouped by prefix before first underscore, keep best N by best_loss
    - keep_total_size:GB -> keep files until total retained size <= GB, others are prune candidates
    """
    candidates: list[str] = []
    if policy.startswith('keep_latest:'):
        try:
            n = int(policy.split(':', 1)[1])
        except Exception:
            n = 3
        rows_sorted = sorted(rows, key=lambda r: r['mtime'], reverse=True)
        keep = set(r['path'] for r in rows_sorted[:n])
        candidates = [r['path'] for r in rows if r['path'] not in keep]
    elif policy.startswith('keep_best_per_prefix:'):
        try:
            n = int(policy.split(':', 1)[1])
        except Exception:
            n = 1
        groups: dict[str, list[dict[str, Any]]] = {}
        for r in rows:
            name = Path(r['path']).name
            prefix = name.split('_', 1)[0] if '_' in name else name
            groups.setdefault(prefix, []).append(r)
        keep = set()
        for g in groups.values():
            # sort by best_loss ascending (lower is better), tiebreak by mtime desc
            g_sorted = sorted(g, key=lambda x: (float('inf') if x.get('best_loss') is None else x.get('best_loss'), -x.get('mtime', 0)))
            for item in g_sorted[:n]:
                keep.add(item['path'])
        candidates = [r['path'] for r in rows if r['path'] not in keep]
    elif policy.startswith('keep_total_size:'):
        try:
            gb = float(policy.split(':', 1)[1])
        except Exception:
            gb = 20.0
        limit = int(gb * 1024**3)
        rows_sorted = sorted(rows, key=lambda r: (r.get('best_loss') if r.get('best_loss') is not None else float('inf'), -r.get('mtime', 0)))
        retained: list[dict[str, Any]] = []
        total = 0
        for r in rows_sorted:
            if total + r.get('size_bytes', 0) <= limit:
                retained.append(r)
                total += r.get('size_bytes', 0)
        keep = set(r['path'] for r in retained)
        candidates = [r['path'] for r in rows if r['path'] not in keep]
    else:
        raise ValueError(f'Unknown policy: {policy}')
    return candidates


def perform_prune(paths: list[str], archive_dir: Path, apply: bool = False) -> tuple[int, int]:
    moved = 0
    skipped = 0
    archive_dir.mkdir(parents=True, exist_ok=True)
    for p in paths:
        try:
            src = Path(p)
            dst = archive_dir / src.name
            if apply:
                shutil.move(str(src), str(dst))
                moved += 1
            else:
                skipped += 1
        except Exception:
            skipped += 1
    return moved, skipped


def human_size(n: int) -> str:
    for unit in ['B','KB','MB','GB','TB']:
        if n < 1024.0:
            return f"{n:.1f}{unit}"
        n /= 1024.0
    return f"{n:.1f}PB"


def main(argv: list[str] | None = None):
    p = argparse.ArgumentParser()
    p.add_argument('cmd', choices=['audit','prune','report'])
    p.add_argument('--dir', type=str, default='F:/models/checkpoints')
    p.add_argument('--out', type=str, default='ckpts.csv')
    p.add_argument('--policy', type=str, default='keep_latest:3')
    p.add_argument('--archive', type=str, default=None)
    p.add_argument('--apply', action='store_true', help='actually move files (default: dry-run)')
    args = p.parse_args(argv)

    root = Path(args.dir)
    if not root.exists():
        print(f'Directory not found: {root}', file=sys.stderr)
        return 2

    rows = scan_checkpoints(root)
    if args.cmd == 'audit':
        out = Path(args.out)
        write_csv(rows, out)
        print(f'Wrote audit CSV to {out} ({len(rows)} entries)')
        # print summary
        total_size = sum(r.get('size_bytes',0) for r in rows)
        print(f'Total files: {len(rows)}  Total size: {human_size(total_size)}')
        # show top 10 largest
        for r in sorted(rows, key=lambda x: x.get('size_bytes',0), reverse=True)[:10]:
            print(f"{human_size(r.get('size_bytes',0)):>8}  {r.get('path')}  step={r.get('global_step')} loss={r.get('best_loss')} err={r.get('read_error')}")
        return 0

    if args.cmd == 'report':
        total_size = sum(r.get('size_bytes',0) for r in rows)
        print(f'Total files: {len(rows)}  Total size: {human_size(total_size)}')
        for r in sorted(rows, key=lambda x: x.get('mtime',0), reverse=True)[:20]:
            print(f"{human_size(r.get('size_bytes',0)):>8}  {r.get('path')}  step={r.get('global_step')} loss={r.get('best_loss')} err={r.get('read_error')}")
        return 0

    if args.cmd == 'prune':
        archive = Path(args.archive) if args.archive else root / 'archive'
        candidates = select_prune_candidates(rows, args.policy)
        print(f'Prune candidates: {len(candidates)} (policy={args.policy})')
        # show top 20 candidates
        for c in candidates[:20]:
            print(c)
        if args.apply:
            moved, skipped = perform_prune(candidates, archive, apply=True)
            print(f'Moved {moved} files to {archive}  skipped={skipped}')
        else:
            print('Dry-run mode (use --apply to actually move files).')
        return 0


if __name__ == '__main__':
    sys.exit(main())
