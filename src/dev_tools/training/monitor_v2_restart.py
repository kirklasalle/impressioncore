"""Monitoring utility for the v2 restart-based embedding head training run.

Reads the metrics JSONL incrementally and prints:
  - Latest step, epoch, loss, lr
  - Smoothed trailing window averages
  - Best validation loss so far (from ckpt_best if exists)
Usage (PowerShell):
  python -m src.dev_tools.training.monitor_v2_restart --ckpt-dir F:/models/checkpoints/b3/b3_39m_128k_v2_headft_long_restart --tail 2000
"""
from __future__ import annotations

import argparse
import contextlib
import json
from pathlib import Path
from statistics import mean


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--ckpt-dir', type=str, required=True)
    p.add_argument('--tail', type=int, default=1500, help='How many recent records to consider for smoothing')
    p.add_argument('--window', type=int, default=200, help='Window size for short-term average')
    return p.parse_args()


def load_metrics(path: Path):
    if not path.exists():
        return []
    recs = []
    with open(path, encoding='utf-8') as f:
        for line in f:
            line=line.strip()
            if not line:
                continue
            with contextlib.suppress(Exception):
                recs.append(json.loads(line))
    return recs


def main():
    args = parse_args()
    ckpt = Path(args.ckpt_dir)
    metrics_path = ckpt / 'training_metrics_v2.jsonl'
    records = load_metrics(metrics_path)
    if not records:
        print('No metrics yet.')
        return 0

    latest = records[-1]
    recent = records[-args.tail:]
    loss_entries = [r['loss'] for r in recent if 'loss' in r]
    short = loss_entries[-args.window:] if len(loss_entries) > args.window else loss_entries

    def avg(xs):
        return float(mean(xs)) if xs else float('nan')

    # Find latest validation
    val_events = [r for r in records if 'val_loss' in r]
    best_val = min([v['val_loss'] for v in val_events], default=float('nan'))
    last_val = val_events[-1]['val_loss'] if val_events else float('nan')

    latest_loss = latest.get('loss', None)
    loss_str = f"{latest_loss:.4e}" if isinstance(latest_loss, int | float) else 'NA'
    print(f"Latest step: {latest.get('step')} epoch: {latest.get('epoch')} loss: {loss_str} lr: {latest.get('lr', 'NA')}")
    print(f"Recent avg ({len(loss_entries)} samples): {avg(loss_entries):.4e} | Short-window avg ({len(short)}): {avg(short):.4e}")
    print(f"Best val: {best_val:.4e} | Last val: {last_val:.4e} | Val events: {len(val_events)}")
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
