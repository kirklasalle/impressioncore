"""Summarize embedding head v2 training metrics JSONL.

Reads training_metrics_v2.jsonl from a run directory and outputs:
  - summary_stats.json
  - metrics_compact.csv (selected columns)
  - prints key milestones (best val improvements)

Usage:
  .\.venv310\Scripts\Activate.ps1; \
  $env:PYTHONPATH='D:/Projects/impressioncore'; \
  python -m src.training.summarize_embedding_training --run F:/models/checkpoints/b3/b3_39m_128k_v2_full30ep_3ksteps_v2_run3
"""
from __future__ import annotations
import argparse, json, math, statistics as stats
from pathlib import Path

FIELDS = ('step','epoch','loss','val_loss','lr','cos','mse','grad_norm')

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--run', required=True, help='Run directory containing training_metrics_v2.jsonl')
    p.add_argument('--out', default=None, help='Optional override output directory (default: run dir)')
    return p.parse_args()


def main():
    args = parse_args()
    run_dir = Path(args.run)
    metrics_file = run_dir / 'training_metrics_v2.jsonl'
    if not metrics_file.is_file():
        raise FileNotFoundError(metrics_file)

    out_dir = Path(args.out) if args.out else run_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    best_progression = []
    best_val = math.inf
    with metrics_file.open('r', encoding='utf-8') as f:
        for line in f:
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            rows.append(obj)
            if 'val_loss' in obj:
                vl = obj['val_loss']
                if vl < best_val:
                    best_val = vl
                    best_progression.append({'step': obj.get('step'), 'epoch': obj.get('epoch'), 'val_loss': vl})

    # Aggregate simple stats
    losses = [r['loss'] for r in rows if 'loss' in r]
    cos_vals = [r['cos'] for r in rows if 'cos' in r]
    mse_vals = [r['mse'] for r in rows if 'mse' in r]
    grad_vals = [r['grad_norm'] for r in rows if 'grad_norm' in r]

    summary = {
        'num_records': len(rows),
        'num_updates': len(losses),
        'final_step': rows[-1]['step'] if rows else None,
        'best_val_loss': best_val if best_val < math.inf else None,
        'loss_mean': stats.fmean(losses) if losses else None,
        'loss_median': stats.median(losses) if losses else None,
        'cos_mean': stats.fmean(cos_vals) if cos_vals else None,
        'mse_mean': stats.fmean(mse_vals) if mse_vals else None,
        'grad_norm_mean': stats.fmean(grad_vals) if grad_vals else None,
        'best_progression': best_progression,
    }
    (out_dir / 'summary_stats.json').write_text(json.dumps(summary, indent=2))

    # Compact CSV
    import csv
    csv_path = out_dir / 'metrics_compact.csv'
    with csv_path.open('w', newline='', encoding='utf-8') as cf:
        writer = csv.writer(cf)
        writer.writerow(FIELDS)
        for r in rows:
            writer.writerow([r.get(k,'') for k in FIELDS])

    print('[SUMMARY]')
    print(json.dumps(summary, indent=2))
    print(f'Wrote {csv_path}')

if __name__ == '__main__':
    main()
