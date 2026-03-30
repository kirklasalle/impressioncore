"""Summarize JSONL training metrics (v2) for quick diagnostics.

Example:
    python -m src.evaluation.summarize_training_metrics \
        --metrics F:/models/checkpoints/b3/b3_39m_128k_v2/training_metrics_v2.jsonl

Reports:
  - Total steps, epochs observed
  - Loss mean/median/min/max & 5/95 percentiles
  - Final 500-step rolling mean
  - Validation improvements count & best val
"""
from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--metrics', required=True)
    p.add_argument('--tail', type=int, default=500, help='Window size for final rolling stats')
    return p.parse_args()


def percentile(data, q):
    if not data:
        return None
    data_sorted = sorted(data)
    k = (len(data_sorted)-1) * q
    f = int(k)
    c = min(f+1, len(data_sorted)-1)
    if f == c:
        return data_sorted[f]
    d0 = data_sorted[f] * (c - k)
    d1 = data_sorted[c] * (k - f)
    return d0 + d1


# NEW: small helpers to reduce complexity
def _collect_records(path: Path):
    step_losses = []
    val_events = []
    epochs = set()
    with path.open('r', encoding='utf-8') as f:
        for line in f:
            try:
                rec = json.loads(line)
            except Exception:
                continue
            if 'val_loss' in rec:
                val_events.append(rec)
            elif 'loss' in rec:
                step_losses.append(rec)
            if 'epoch' in rec:
                epochs.add(rec['epoch'])
    return step_losses, val_events, epochs


def _loss_stats(losses, tail):
    if not losses:
        return {
            'loss_mean': None,
            'loss_median': None,
            'loss_min': None,
            'loss_max': None,
            'loss_p5': None,
            'loss_p95': None,
            'tail_window': tail,
            'tail_mean': None,
            'tail_median': None
        }
    tail_slice = losses[-tail:] if len(losses) >= tail else None
    return {
        'loss_mean': float(statistics.mean(losses)),
        'loss_median': float(statistics.median(losses)),
        'loss_min': float(min(losses)),
        'loss_max': float(max(losses)),
        'loss_p5': float(percentile(losses, 0.05)),
        'loss_p95': float(percentile(losses, 0.95)),
        'tail_window': tail,
        'tail_mean': float(statistics.mean(tail_slice)) if tail_slice else None,
        'tail_median': float(statistics.median(tail_slice)) if tail_slice else None,
    }


def main():
    args = parse_args()
    path = Path(args.metrics)
    if not path.exists():
        raise SystemExit(f"Metrics file not found: {path}")

    step_losses, val_events, epochs = _collect_records(path)
    losses = [r['loss'] for r in step_losses]
    stats_block = _loss_stats(losses, args.tail)

    report = {
        'total_steps': len(step_losses),
        'epochs_observed': sorted(epochs),
        **stats_block,
        'val_event_count': len(val_events),
        'best_val_loss': float(min(e['val_loss'] for e in val_events)) if val_events else None,
        'final_val_loss': float(val_events[-1]['val_loss']) if val_events else None
    }

    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
