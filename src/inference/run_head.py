"""CLI utility to run the (production) embedding reconstruction head (v1 preferred).

Example (PowerShell):
  python -m src.inference.run_head --ckpt-dir F:/models/checkpoints/b3/b3_39m_128k_v2 --eval-samples 2048 --device cuda

Outputs quick cosine + mse stats on a sample subset to confirm everything works.
"""
from __future__ import annotations

import argparse
import random

import torch
import torch.nn.functional as F

from src.inference.embedding_head_loader import load_best_head
from src.training.embedded_dataset import PrecomputedEmbeddingDataset


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--ckpt-dir', type=str, required=True)
    p.add_argument('--device', type=str, default='cuda', help='Device (forced to cuda if available)')
    p.add_argument('--batch-size', type=int, default=512)
    p.add_argument('--eval-samples', type=int, default=1024, help='Number of pairs to sample for a quick sanity check')
    p.add_argument('--seed', type=int, default=123)
    return p.parse_args()


def batched(indices: list[int], bsz: int):
    for i in range(0, len(indices), bsz):
        yield indices[i:i+bsz]


def main():
    args = parse_args()
    random.seed(args.seed)
    torch.manual_seed(args.seed)

    # Enforce CUDA usage per project standard
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA not available but project requires CUDA-only execution.")
    args.device = 'cuda'
    model = load_best_head(args.ckpt_dir, map_location='cpu')
    model.to(args.device)
    model.eval()
    print(f"Loaded head: {model.__class__.__name__} on CUDA from {args.ckpt_dir}")

    # Dataset (may rely on local precomputed arrays; handle failure gracefully)
    try:
        ds = PrecomputedEmbeddingDataset()
    except Exception as e:
        print(f"Failed to load PrecomputedEmbeddingDataset: {e}")
        return 1

    n = len(ds)
    k = min(args.eval_samples, n)
    idx = list(range(n - k, n))  # take last k for determinism

    total_cos = 0.0
    total_mse = 0.0
    total = 0
    with torch.no_grad():
        for _batch_idx, chunk in enumerate(batched(idx, args.batch_size)):
            src_list = []
            tgt_list = []
            for i in chunk:
                x, y = ds[i]
                if not torch.is_tensor(x):
                    x = torch.from_numpy(x)
                if not torch.is_tensor(y):
                    y = torch.from_numpy(y)
                src_list.append(x)
                tgt_list.append(y)
            x_t = torch.stack(src_list).to(args.device, non_blocking=True)
            y_t = torch.stack(tgt_list).to(args.device, non_blocking=True)
            pred = model(x_t)
            pn = F.normalize(pred, dim=-1)
            yn = F.normalize(y_t, dim=-1)
            cos = 1.0 - (pn * yn).sum(dim=-1)
            mse = (pn - yn).pow(2).mean(dim=-1)
            total_cos += float(cos.sum().item())
            total_mse += float(mse.sum().item())
            total += len(chunk)
    if total == 0:
        print("No samples evaluated.")
        return 0

    avg_cos = total_cos / total
    avg_mse = total_mse / total
    blended = 0.7 * avg_cos + 0.3 * avg_mse
    print(f"Eval samples: {total}")
    print(f"Average cosine distance: {avg_cos:.6e}")
    print(f"Average normalized MSE:  {avg_mse:.6e}")
    print(f"Blended(0.7*cos + 0.3*mse): {blended:.6e}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
