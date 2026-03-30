#!/usr/bin/env python3
"""Comprehensive analysis of all checkpoint-like files discovered on F:/models.

Outputs:
 - inventory_reports/full_checkpoint_analysis.json : list with metrics/size/status
 - inventory_reports/top5_checkpoints.json : selected top 5 according to ranking rules

Ranking rules:
 1. Prefer checkpoints with real metric (val_best, best_loss, or hist_tail).
 2. Primary score = val_best | best_loss | hist_tail (lowest is better).
 3. If no real metric (all missing) they are excluded from top unless fewer than 5 qualifying; then fallback to those with steps info.
 4. Tie-breakers: lower primary, more steps, larger size (assumes completeness), newer timestamp.

Large sentinel (1e12) used when metrics missing.
"""
from __future__ import annotations

import json
import traceback
from pathlib import Path
from typing import Any

import torch

INV_DIR = Path('inventory_reports')
INV_FILE = INV_DIR / 'f_models_checkpoint_inventory.csv'
OUT_FULL = INV_DIR / 'full_checkpoint_analysis.json'
OUT_TOP5 = INV_DIR / 'top5_checkpoints.json'
LARGE_SENTINEL = 1e12

EXTS = {'.pth','.pt','.safetensors','.ckpt','.bin'}

def supports_weights_only():
    import inspect
    try:
        return 'weights_only' in inspect.signature(torch.load).parameters
    except Exception:
        return False

SUPPORTS_WEIGHTS_ONLY = supports_weights_only()

def load_ckpt(path: Path) -> dict[str, Any]:
    try:
        ck = torch.load(path, map_location='cpu')
        return {'data': ck, 'mode': 'full'}
    except Exception as e1:
        if SUPPORTS_WEIGHTS_ONLY:
            try:
                ck2 = torch.load(path, map_location='cpu', weights_only=True)
                return {'data': ck2, 'mode': 'weights_only'}
            except Exception as e2:
                return {'error': f"full:{e1} | weights_only:{e2}"}
        return {'error': str(e1)}


def extract_metrics(obj: dict[str, Any]) -> dict[str, Any]:
    if 'error' in obj:
        return {'primary': LARGE_SENTINEL, 'best_loss': None, 'val_best': None, 'hist_tail': None, 'steps': None, 'load_mode': None, 'error': obj['error']}
    data = obj['data']
    load_mode = obj.get('mode')
    # if weights_only returned just a state_dict, wrap heuristically
    if load_mode == 'weights_only' and not isinstance(data, dict):
        return {'primary': LARGE_SENTINEL, 'best_loss': None, 'val_best': None, 'hist_tail': None, 'steps': None, 'load_mode': load_mode}
    best_loss = data.get('best_loss') if isinstance(data, dict) else None
    val_best = None
    if isinstance(data, dict) and isinstance(data.get('best_val'), dict):
        val_best = data['best_val'].get('value')
    loss_history = data.get('loss_history') if isinstance(data, dict) else None
    hist_tail = None
    if loss_history:
        tail = loss_history[-min(10, len(loss_history)) :]
        if tail:
            hist_tail = float(sum(tail)/len(tail))
    if val_best is not None:
        primary = float(val_best)
    elif best_loss is not None:
        primary = float(best_loss)
    elif hist_tail is not None:
        primary = hist_tail
    else:
        primary = LARGE_SENTINEL
    steps = None
    if isinstance(data, dict):
        steps = data.get('global_step') or data.get('step')
    return {
        'primary': primary,
        'best_loss': best_loss,
        'val_best': val_best,
        'hist_tail': hist_tail,
        'steps': steps,
        'load_mode': load_mode
    }


def read_inventory() -> list[Path]:
    if not INV_FILE.exists():
        raise SystemExit('Run inventory_full_scan.py first.')
    out=[]
    for line in INV_FILE.read_text(encoding='utf-8').splitlines()[1:]:
        if not line.strip():
            continue
        path=line.split(',')[0]
        p=Path(path)
        if p.suffix.lower() in EXTS:
            out.append(p)
    return out


def rank(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    qualified=[r for r in records if r['primary'] < LARGE_SENTINEL]
    fallback=[r for r in records if r['primary'] >= LARGE_SENTINEL]
    def sort_key(r):
        return (r['primary'], -(r['steps'] or -1), -r['size_mb'], -r['timestamp'])
    qualified.sort(key=sort_key)
    if len(qualified) >= 5:
        return qualified[:5]
    # supplement with fallback using steps then size
    def fb_key(r):
        return (-(r['steps'] or -1), -r['size_mb'], -r['timestamp'])
    fallback.sort(key=fb_key)
    return qualified + fallback[: max(0, 5-len(qualified))]


def main():
    paths = read_inventory()
    records=[]
    for p in paths:
        try:
            stat = p.stat()
            size_mb = round(stat.st_size/1024**2,2)
            ts = stat.st_mtime
            loaded = load_ckpt(p)
            extract_metrics(loaded)
            rec = {
                'path': str(p),
                'filename': p.name,
                'size_mb': size_mb,
                'timestamp': ts,
                # metrics
            }
            records.append(rec)
        except Exception as e:
            records.append({'path': str(p), 'filename': p.name, 'error': str(e), 'trace': traceback.format_exc(), 'primary': LARGE_SENTINEL, 'size_mb': None, 'timestamp': None})
    OUT_FULL.write_text(json.dumps(records, indent=2), encoding='utf-8')
    top5 = rank(records)
    OUT_TOP5.write_text(json.dumps(top5, indent=2), encoding='utf-8')
    print('ANALYSIS_COMPLETE total_files=', len(records), 'top5_written')

if __name__ == '__main__':
    main()
