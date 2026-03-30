"""Evaluate embedding reconstruction head checkpoint (raw vs EMA if present).

Update (September 7, 2025):
    * Added head auto-detection (v1 / v2) via training_config_v2.json
    * Added --ckpt-dir discovery mode (finds ckpt_best.pt + config + metrics)
    * Unified build via build_embedding_head (future extensibility)
    * Additional metrics: pct improvement EMA vs raw, relative improvement vs prior evaluation

Usage examples:
    Explicit paths:
        python -m src.evaluation.embedding_head_eval \
                --ckpt F:/models/checkpoints/b3/b3_39m_128k_v2/ckpt_best.pt \
                --config F:/models/checkpoints/b3/b3_39m_128k_v2/training_config_v2.json \
                --metrics F:/models/checkpoints/b3/b3_39m_128k_v2/training_metrics_v2.jsonl

    Directory auto-discovery:
        python -m src.evaluation.embedding_head_eval \
                --ckpt-dir F:/models/checkpoints/b3/b3_39m_128k_v2_headft_long_restart

Outputs:
    * Prints raw & (optionally) EMA blended validation losses
    * Writes evaluation_results.json beside checkpoint with extended metadata

Design notes:
    * Validation subset matches training slicing logic (last fraction of dataset)
    * Metrics JSONL optional
    recent tail statistics included if present
    * Low memory footprint / AMP optional
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import torch
import torch.nn.functional as F
from torch import amp
from torch.utils.data import DataLoader, Subset

from src.training.embed_head import build_embedding_head
from src.training.embedded_dataset import PrecomputedEmbeddingDataset


def _discover_in_dir(ckpt_dir: Path) -> tuple[Path, Path, Path | None]:
    """Discover checkpoint, config and metrics inside a directory.

    Preference order:
      * ckpt_best.pt else most recent ckpt_step_*.pt
      * training_config_v2.json required
      * training_metrics_v2.jsonl optional
    """
    if not ckpt_dir.exists():
        raise SystemExit(f"Checkpoint directory not found: {ckpt_dir}")
    best = ckpt_dir / 'ckpt_best.pt'
    if best.exists():
        ckpt = best
    else:
        steps = sorted(ckpt_dir.glob('ckpt_step_*.pt'))
        if not steps:
            raise SystemExit(f"No checkpoints found in {ckpt_dir}")
        ckpt = steps[-1]
    cfg = ckpt_dir / 'training_config_v2.json'
    if not cfg.exists():
        raise SystemExit(f"Missing training_config_v2.json in {ckpt_dir}")
    metrics = ckpt_dir / 'training_metrics_v2.jsonl'
    if not metrics.exists():
        metrics = None
    return ckpt, cfg, metrics


def parse_args():
    p = argparse.ArgumentParser()
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument('--ckpt', help='Path to checkpoint (.pt) file')
    g.add_argument('--ckpt-dir', help='Directory containing ckpt_best.pt and training_config_v2.json')
    p.add_argument('--config', help='Training config JSON (captures loss weights)')
    p.add_argument('--metrics', default=None, help='Optional training metrics jsonl for context')
    p.add_argument('--batch-size', type=int, default=512)
    p.add_argument('--val-size', type=int, default=12000)
    p.add_argument('--workers', type=int, default=4)
    p.add_argument('--no-amp', action='store_true')
    p.add_argument('--device', default='cuda' if torch.cuda.is_available() else 'cpu')
    return p.parse_args()


def blended_loss(pred, target, w_cos: float, w_mse: float):
    pred_n = F.normalize(pred, dim=-1)
    tgt_n = F.normalize(target, dim=-1)
    cos = 1.0 - (pred_n * tgt_n).sum(dim=-1).mean()
    mse = F.mse_loss(pred_n, tgt_n)
    return (w_cos * cos + w_mse * mse).item()


def load_validation_subset(val_size: int):
    ds = PrecomputedEmbeddingDataset()
    n = len(ds)
    vs = min(val_size, n // 8)
    val_idx = list(range(n - vs, n))
    return Subset(ds, val_idx)


def evaluate(model, loader, device, w_cos, w_mse, use_amp=True):
    model.eval()
    total = 0.0
    count = 0
    scaler = amp.autocast(device_type='cuda', enabled=(device.startswith('cuda') and use_amp))
    with torch.no_grad():
        for x,y in loader:
            x = x.to(device)
            y = y.to(device)
            with scaler:
                out = model(x)
                loss = blended_loss(out, y, w_cos, w_mse)
            bsz = x.size(0)
            total += loss * bsz
            count += bsz
    return total / max(1, count)


def main():
    args = parse_args()
    if args.ckpt_dir:
        ckpt_path, cfg_path, auto_metrics = _discover_in_dir(Path(args.ckpt_dir))
        if args.metrics is None and auto_metrics is not None:
            args.metrics = str(auto_metrics)
    else:
        ckpt_path = Path(args.ckpt)
        cfg_path = Path(args.config) if args.config else (ckpt_path.parent / 'training_config_v2.json')
    if not ckpt_path.exists():
        raise SystemExit(f"Checkpoint not found: {ckpt_path}")
    if not cfg_path.exists():
        raise SystemExit(f"Config not found: {cfg_path}")

    config = json.loads(cfg_path.read_text(encoding='utf-8'))
    head_version = config.get('head_version', 'v1')
    dropout = float(config.get('dropout', 0.0))
    final_norm = not bool(config.get('no_final_norm', False))
    w_cos = float(config.get('w_cos', 0.7))
    w_mse = float(config.get('w_mse', 0.3))

    device = args.device
    val_ds = load_validation_subset(args.val_size)
    vdl = DataLoader(val_ds, batch_size=args.batch_size, shuffle=False, num_workers=args.workers, pin_memory=True)

    model = build_embedding_head(version=head_version, dim=768, hidden=2048, dropout=dropout, final_norm=final_norm).to(device)
    ck = torch.load(str(ckpt_path), map_location=device)
    model.load_state_dict(ck['model_state_dict'])

    raw_val = evaluate(model, vdl, device, w_cos, w_mse, use_amp=not args.no_amp)

    ema_val = None
    if 'ema_state_dict' in ck:
        # load ema weights temporarily
        ema_state = ck['ema_state_dict']
        orig_state = {k: v.clone() for k,v in model.state_dict().items()}
        model.load_state_dict(ema_state, strict=False)
        ema_val = evaluate(model, vdl, device, w_cos, w_mse, use_amp=not args.no_amp)
        model.load_state_dict(orig_state)

    metrics_tail = None
    if args.metrics and Path(args.metrics).exists():
        try:
            # Read last 200 lines for quick context
            with open(args.metrics, encoding='utf-8') as f:
                lines = f.readlines()[-200:]
            import json as _json
            import statistics
            step_losses = [ _json.loads(l)['loss'] for l in lines if '"loss"' in l and 'val_loss' not in l]
            if step_losses:
                metrics_tail = {
                    'recent_mean_loss': float(statistics.mean(step_losses)),
                    'recent_median_loss': float(statistics.median(step_losses)),
                    'recent_min_loss': float(min(step_losses)),
                    'recent_max_loss': float(max(step_losses)),
                    'samples': len(step_losses)
                }
        except Exception:
            pass

    raw_vs_ema_pct = None
    if ema_val is not None and raw_val > 0:
        raw_vs_ema_pct = (raw_val - ema_val) / raw_val * 100.0

    prev_report_path = ckpt_path.parent / 'evaluation_results.json'
    prev_impr = None
    if prev_report_path.exists():
        try:
            prev = json.loads(prev_report_path.read_text())
            prev_raw = float(prev.get('raw_val_loss', 0.0))
            if prev_raw > 0 and prev_raw != raw_val:
                prev_impr = (prev_raw - raw_val) / prev_raw * 100.0
        except Exception:
            pass

    report: dict[str, Any] = {
        'checkpoint': str(ckpt_path),
        'config': str(cfg_path),
        'w_cos': w_cos,
        'w_mse': w_mse,
        'head_version': head_version,
        'dropout': dropout,
        'final_norm': final_norm,
        'raw_val_loss': raw_val,
        'ema_val_loss': ema_val,
        'improvement_ema_vs_raw': (raw_val - ema_val) if (ema_val is not None) else None,
        'improvement_ema_vs_raw_pct': raw_vs_ema_pct,
        'relative_improvement_vs_previous_eval_pct': prev_impr,
        'metric_tail_summary': metrics_tail
    }

    out_path = ckpt_path.parent / 'evaluation_results.json'
    out_path.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
