#!/usr/bin/env python3
"""Produce deep analysis for top5_checkpoints.json.
Generates inventory_reports/top5_detailed_analysis.json
For each checkpoint:
 - size, timestamp (human)
 - steps, metrics (best/val/tail/primary)
 - parameter count (if model state available) and total elements
 - top 15 tensors by parameter count (name, shape, elems, percent)
 - estimated bits per parameter (file_size_bytes*8/param_elems)
 - anomaly flags (e.g., unusually high loss scale, low steps, size vs params mismatch)
"""
from __future__ import annotations

import json
import time
import traceback
from pathlib import Path
from typing import Any

import torch

INV_DIR = Path('inventory_reports')
TOP5_FILE = INV_DIR/'top5_checkpoints.json'
OUT_FILE = INV_DIR/'top5_detailed_analysis.json'

LARGE_LOSS_THRESHOLD = 100.0  # anything above suggests different scale
LOW_STEP_THRESHOLD = 50


def load_ckpt(path: Path):
    try:
        ck = torch.load(path, map_location='cpu')
        return ck, 'full'
    except Exception as e:
        # attempt weights_only if available
        try:
            import inspect
            if 'weights_only' in inspect.signature(torch.load).parameters:
                ck2 = torch.load(path, map_location='cpu', weights_only=True)
                return ck2, 'weights_only'
        except Exception:
            pass
        return {'__error': str(e)}, 'error'


def summarize_state_dict(container) -> dict[str, Any]:
    if isinstance(container, dict):
        sd = container.get('model_state_dict') or container.get('state_dict') or (container if all(isinstance(v, torch.Tensor) for v in container.values()) else None)
    else:
        sd = None
    if sd is None:
        return {'param_elems': 0, 'param_tensors': 0, 'top_tensors': []}
    total = 0
    entries = []
    for name, tensor in sd.items():
        if not isinstance(tensor, torch.Tensor):
            continue
        elems = tensor.numel()
        total += elems
        entries.append((name, tuple(tensor.shape), elems))
    entries.sort(key=lambda x: x[2], reverse=True)
    top = entries[:15]
    top_summary=[{
        'name': n,
        'shape': list(s),
        'elems': e,
        'percent': round(e/total*100,3) if total else 0.0
    } for n,s,e in top]
    return {
        'param_elems': total,
        'param_tensors': len(entries),
        'top_tensors': top_summary
    }


def analyze_entry(item: dict[str, Any]) -> dict[str, Any]:
    path = Path(item['path'])
    ck, mode = load_ckpt(path)
    metrics = {
        'primary': item.get('primary'),
        'best_loss': item.get('best_loss'),
        'val_best': item.get('val_best'),
        'hist_tail': item.get('hist_tail'),
        'steps': item.get('steps')
    }
    state_summary = summarize_state_dict(ck)
    size_mb = item.get('size_mb')
    param_elems = state_summary['param_elems'] or 1
    file_size_bytes = size_mb * 1024**2 if size_mb else 0
    bits_per_param = round((file_size_bytes*8)/param_elems, 3) if param_elems and file_size_bytes else None
    anomalies=[]
    if metrics['primary'] and metrics['primary'] > LARGE_LOSS_THRESHOLD:
        anomalies.append('loss_scale_outlier')
    if (metrics['steps'] or 0) < LOW_STEP_THRESHOLD:
        anomalies.append('low_step_count')
    if bits_per_param and bits_per_param > 64:
        anomalies.append('high_bits_per_param')
    if mode == 'error' or (isinstance(ck, dict) and '__error' in ck):
        anomalies.append('load_error')
    # attempt to glean config footprint
    config_repr=None
    if isinstance(ck, dict):
        cfg = ck.get('config')
        if cfg is not None:
            # grab selected attrs commonly present
            fields = ['hidden_size','num_layers','n_heads','vocab_size','max_seq_length','moe_num_experts','moe_top_k']
            parts=[]
            for f in fields:
                if hasattr(cfg,f):
                    parts.append(f"{f}={getattr(cfg,f)}")
            if parts:
                config_repr=', '.join(parts)
    return {
        'path': item['path'],
        'filename': item['filename'],
        'size_mb': size_mb,
        'timestamp': item.get('timestamp'),
        'timestamp_human': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(item.get('timestamp',0))),
        'load_mode': mode,
        'metrics': metrics,
        'state': state_summary,
        'bits_per_param': bits_per_param,
        'anomalies': anomalies,
        'config_summary': config_repr
    }


def main():
    if not TOP5_FILE.exists():
        raise SystemExit('Missing top5_checkpoints.json')
    data = json.loads(TOP5_FILE.read_text(encoding='utf-8'))
    detailed=[]
    for item in data:
        try:
            detailed.append(analyze_entry(item))
        except Exception as e:
            detailed.append({'path': item['path'], 'error': str(e), 'trace': traceback.format_exc()})
    OUT_FILE.write_text(json.dumps(detailed, indent=2), encoding='utf-8')
    print('TOP5_DETAILED_ANALYSIS_COMPLETE')

if __name__ == '__main__':
    main()
