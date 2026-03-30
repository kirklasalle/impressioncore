#!/usr/bin/env python3
"""Dump full config objects for 768-d checkpoints and search for long-context indicators.

Writes per-checkpoint JSON under F:/data/embeddings/b3_39m/config_dumps and a summary file.
"""
import json
from pathlib import Path

import torch

ROOT = Path("d:/Projects/impressioncore")
CKPT_SCAN = Path("F:/data/embeddings/b3_39m/ckpt_scan.json")
OUT_DIR = Path("F:/data/embeddings/b3_39m/config_dumps")
OUT_DIR.mkdir(parents=True, exist_ok=True)

KEYWORDS = [
    'n_ctx', 'max_seq', 'max_position', 'context', 'context_length', '128000', '128k',
    'rotary', 'rope', 'alibi', 'rotary_pct', 'rotary_scaling', 'positional', 'attention_window',
    'window_size', 'block_size'
]

def make_json_serializable(obj):
    # Try common objects: dataclasses, namespaces, dicts, lists
    try:
        if obj is None:
            return None
        if isinstance(obj, str | int | float | bool):
            return obj
        if isinstance(obj, dict):
            return {str(k): make_json_serializable(v) for k, v in obj.items()}
        if isinstance(obj, list | tuple):
            return [make_json_serializable(v) for v in obj]
        # PyTorch tensor
        try:
            import torch
            if isinstance(obj, torch.Tensor):
                return obj.size()
        except Exception:
            pass
        # objects with __dict__
        if hasattr(obj, '__dict__'):
            return make_json_serializable(vars(obj))
        return repr(obj)
    except Exception as e:
        return f"<unserializable: {e}>"


def inspect_checkpoint(path):
    path = Path(path)
    out = {
        'path': str(path),
        'loaded': False,
        'top_keys': None,
        'config': None,
        'config_serializable': None,
        'search_hits': [],
        'load_error': None,
    }
    try:
        ckpt = torch.load(str(path), map_location='cpu')
        out['loaded'] = True
        if isinstance(ckpt, dict):
            out['top_keys'] = list(ckpt.keys())
            cfg = ckpt.get('config') or ckpt.get('cfg') or ckpt.get('args') or ckpt.get('state_dict')
            out['config'] = cfg
            out['config_serializable'] = make_json_serializable(cfg)
            # Create a searchable string repr
            s = json.dumps(out['config_serializable'], default=str) if out['config_serializable'] is not None else ''
            s = s.lower()
            hits = []
            for kw in KEYWORDS:
                if kw.lower() in s:
                    hits.append(kw)
            out['search_hits'] = hits
        else:
            out['top_keys'] = ['<not-a-dict>']
    except Exception as e:
        out['load_error'] = str(e)
    return out


def main():
    # Load ckpt_scan.json if present
    candidates = []
    if CKPT_SCAN.exists():
        try:
            data = json.loads(CKPT_SCAN.read_text(encoding='utf-8'))
            for entry in data:
                try:
                    if entry.get('embed_dim_reported') == 768:
                        candidates.append(entry.get('path'))
                except Exception:
                    continue
        except Exception as e:
            print(f"Failed to read {CKPT_SCAN}: {e}")

    # Fallback: scan F:/models for .pt files
    if not candidates:
        mdir = Path('F:/models')
        if mdir.exists():
            for p in mdir.rglob('*.pt'):
                candidates.append(str(p))

    summary = []
    for p in candidates:
        print(f"Inspecting: {p}")
        info = inspect_checkpoint(p)
        # Write per-checkpoint dump
        safe_name = Path(p).stem
        out_path = OUT_DIR / (safe_name + '.json')
        try:
            out_path.write_text(json.dumps(info, indent=2, default=str), encoding='utf-8')
        except Exception as e:
            print(f"Failed to write dump for {p}: {e}")
        summary.append({'path': p, 'loaded': info['loaded'], 'search_hits': info.get('search_hits', []), 'load_error': info.get('load_error')})

    summary_path = OUT_DIR / 'summary.json'
    summary_path.write_text(json.dumps(summary, indent=2), encoding='utf-8')
    print(f"Wrote {len(summary)} dumps to {OUT_DIR}. Summary: {summary_path}")


if __name__ == '__main__':
    main()
