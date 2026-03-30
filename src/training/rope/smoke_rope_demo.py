"""Smoke demo for RoPE utilities.

Runs a small forward pass: builds RoPE caches for seq_len=128 and applies to a random tensor,
then recomputes caches for seq_len=1024 (rescaled) and applies to a longer random tensor.
"""
import torch

from .rope_utils import apply_rope, build_rope_cache, rescale_rope_cache_by_recompute


def run_demo(device=None):
    device = device or (torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu'))
    D = 64
    seq1 = 128
    seq2 = 1024
    B = 2
    x1 = torch.randn(B, seq1, D, device=device)
    cos1, sin1 = build_rope_cache(seq1, D, device=device)
    y1 = apply_rope(x1, cos1, sin1)
    print(f"Applied RoPE to {x1.shape} -> {y1.shape} on {device}")

    # recompute for longer seq
    cos2, sin2 = rescale_rope_cache_by_recompute(D, seq2, device=device)
    x2 = torch.randn(B, seq2, D, device=device)
    y2 = apply_rope(x2, cos2, sin2)
    print(f"Applied recomputed RoPE to {x2.shape} -> {y2.shape} on {device}")


if __name__ == '__main__':
    run_demo()
