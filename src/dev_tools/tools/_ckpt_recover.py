#!/usr/bin/env python3
"""Attempt metadata recovery for checkpoints listed in ckpts_all.csv.

Strategies:
- Ensure repo root is on sys.path so pickled module references to `src` can be resolved.
- Try torch.load(path, map_location='cpu') normally.
- If that fails and torch supports weights_only, try torch.load(..., weights_only=True) to only load tensors.

Outputs: writes `ckpts_recovered.csv` with updated metadata fields.
"""
from __future__ import annotations

import csv
import gc
import sys
from pathlib import Path
from typing import Any

ROOT = Path.cwd()
CSV_IN = ROOT / 'ckpts_all.csv'
CSV_OUT = ROOT / 'ckpts_recovered.csv'

try:
    import torch
except Exception:
    torch = None


def load_ckpt_try(path: Path) -> dict[str, Any]:
    # Ensure repo root is on sys.path
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    if not torch:
        raise RuntimeError('torch not available')
    last_err = None
    # First attempt: normal load
    try:
        ckpt = torch.load(str(path), map_location='cpu')
        return {'ckpt': ckpt, 'method': 'normal', 'error': None}
    except Exception as e:
        last_err = e
    # Second attempt: weights_only when supported
    try:
        # Newer PyTorch versions accept weights_only arg
        import inspect
        sig = inspect.signature(torch.load)
        if 'weights_only' in sig.parameters:
            try:
                ckpt = torch.load(str(path), map_location='cpu', weights_only=True)
                return {'ckpt': ckpt, 'method': 'weights_only', 'error': None}
            except Exception as e:
                last_err = e
    except Exception:
        pass
    return {'ckpt': None, 'method': None, 'error': str(last_err)}


def main():
    if not CSV_IN.exists():
        print(f'{CSV_IN} not found; run tools/ckpt_manager.py audit first')
        return 2
    rows = []
    with CSV_IN.open('r', encoding='utf-8') as f:
        rdr = csv.DictReader(f)
        for r in rdr:
            rows.append(dict(r))

    updated = []
    for r in rows:
        path = Path(r.get('path'))
        need = (r.get('read_error') and r.get('read_error') != '') or (not r.get('best_loss') or r.get('best_loss') in ('', 'None'))
        if not need:
            updated.append(r)
            continue
        print(f'Attempting recovery: {path}')
        res = load_ckpt_try(path)
        if res.get('ckpt') is None:
            r['read_error'] = res.get('error')
            print(f'  failed: {r["read_error"]}')
            updated.append(r)
            continue
        ck = res['ckpt']
        # If weights_only returned a state_dict mapping, treat accordingly
        try:
            if isinstance(ck, dict):
                if 'global_step' in ck and ck.get('global_step') is not None:
                    r['global_step'] = str(int(ck.get('global_step')))
                if 'best_loss' in ck and ck.get('best_loss') is not None:
                    try:
                        r['best_loss'] = str(float(ck.get('best_loss')))
                    except Exception:
                        r['best_loss'] = ''
                if 'timestamp' in ck and ck.get('timestamp') is not None:
                    r['timestamp'] = str(ck.get('timestamp'))
                if 'total_params' in ck and ck.get('total_params') is not None:
                    r['total_params'] = str(int(ck.get('total_params')))
            # clear heavy object
            del ck
            gc.collect()
            r['read_error'] = ''
            r['recovery_method'] = res.get('method')
            print('  recovered metadata')
        except Exception as e:
            r['read_error'] = str(e)
            print(f'  recovery error: {e}')
        updated.append(r)

    # write out recovered CSV
    # compute union of all keys to avoid missing-field errors
    all_keys = set()
    for r in updated:
        all_keys.update(r.keys())
    fieldnames = sorted(all_keys)
    # ensure each row contains all keys
    for r in updated:
        for k in fieldnames:
            if k not in r:
                r[k] = ''
    with CSV_OUT.open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in updated:
            w.writerow(r)

    print(f'Wrote recovered CSV to {CSV_OUT}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
