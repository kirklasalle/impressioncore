"""Quick comparison tool for two embedding reconstruction head directories.

Computes blended validation loss for each (raw + optional EMA) on identical
subset and prints a delta summary.

Usage:
  python -m src.evaluation.compare_heads \
    --ckpt-dir-a F:/models/checkpoints/b3/b3_39m_128k_v2 \
    --ckpt-dir-b F:/models/checkpoints/b3/b3_39m_128k_v2_headft_long_restart
"""
from __future__ import annotations

import argparse
import json

import torch
import torch.nn.functional as F
from torch import amp
from torch.utils.data import DataLoader, Subset

from src.inference.embedding_head_loader import load_best_head
from src.training.embedded_dataset import PrecomputedEmbeddingDataset


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--ckpt-dir-a', required=True)
    p.add_argument('--ckpt-dir-b', required=True)
    p.add_argument('--val-size', type=int, default=12000)
    p.add_argument('--batch-size', type=int, default=512)
    p.add_argument('--workers', type=int, default=4)
    p.add_argument('--no-amp', action='store_true')
    p.add_argument('--device', default='cuda' if torch.cuda.is_available() else 'cpu')
    p.add_argument('--w-cos', type=float, default=0.7)
    p.add_argument('--w-mse', type=float, default=0.3)
    return p.parse_args()


def _val_subset(size: int):
    ds = PrecomputedEmbeddingDataset()
    n = len(ds)
    vs = min(size, n // 8)
    idx = list(range(n - vs, n))
    return Subset(ds, idx)


def _blended(out, tgt, w_cos, w_mse):
    on = F.normalize(out, dim=-1)
    tn = F.normalize(tgt, dim=-1)
    cos = 1 - (on * tn).sum(dim=-1).mean()
    mse = F.mse_loss(on, tn)
    return (w_cos * cos + w_mse * mse).item()


def _eval(model, loader, device, w_cos, w_mse, use_amp=True):
    model.eval()
    total=0.0
    count=0
    autocast = amp.autocast(device_type='cuda', enabled=(device.startswith('cuda') and use_amp))
    with torch.no_grad():
        for x,y in loader:
            x=x.to(device)
            y=y.to(device)
            with autocast:
                out = model(x)
                loss = _blended(out, y, w_cos, w_mse)
            b=x.size(0)
            total += loss * b
            count += b
    return total / max(1,count)


def main():
    args = parse_args()
    device = args.device
    subset = _val_subset(args.val_size)
    dl = DataLoader(subset, batch_size=args.batch_size, shuffle=False, num_workers=args.workers, pin_memory=True)

    results = {}
    for tag, ckdir in [('A', args.ckpt_dir_a), ('B', args.ckpt_dir_b)]:
        model = load_best_head(ckdir, map_location=device)
        loss = _eval(model, dl, device, args.w_cos, args.w_mse, use_amp=not args.no_amp)
        results[tag] = {'dir': ckdir, 'raw_val_loss': loss}

    # Delta
    a = results['A']['raw_val_loss']
    b = results['B']['raw_val_loss']
    rel = (a - b)/a * 100.0 if a>0 else None
    summary = {
        'head_A': results['A'],
        'head_B': results['B'],
        'relative_improvement_B_vs_A_pct': rel
    }
    print(json.dumps(summary, indent=2))

if __name__ == '__main__':
    main()
