"""Lightweight inference loader for the best embedding reconstruction head.

Usage:
    from src.inference.embedding_head_loader import load_best_head
    model = load_best_head(r'F:/models/checkpoints/b3/b3_39m_128k_v2')
    model.eval(); out = model(x)  # x: (batch, 768)

Automatically prefers 'ckpt_best.pt' and falls back to most recent step checkpoint.
Supports v1 and v2 heads (with optional final norm) based on saved config if present.
"""
from __future__ import annotations

import json
from pathlib import Path

import torch

from src.training.embed_head import build_embedding_head


def _discover_checkpoint(ckpt_dir: Path) -> Path | None:
    best = ckpt_dir / 'ckpt_best.pt'
    if best.exists():
        return best
    # fallback: latest step checkpoint
    cands = sorted(ckpt_dir.glob('ckpt_step_*.pt'))
    return cands[-1] if cands else None


def load_best_head(ckpt_dir: str | Path, map_location: str = 'cpu', strict: bool = False):
    ckpt_dir = Path(ckpt_dir)
    ckpt = _discover_checkpoint(ckpt_dir)
    if not ckpt:
        raise FileNotFoundError(f'No checkpoint found in {ckpt_dir}')

    # Try to read training config for architecture hints
    cfg_path = ckpt_dir / 'training_config_v2.json'
    head_version = 'v1'
    dropout = 0.0
    final_norm = True
    if cfg_path.exists():
        try:
            cfg = json.loads(cfg_path.read_text())
            head_version = cfg.get('head_version', head_version)
            dropout = float(cfg.get('dropout', dropout))
            final_norm = not bool(cfg.get('no_final_norm', False))
        except Exception:
            pass

    model = build_embedding_head(version=head_version, dim=768, hidden=2048, dropout=dropout, final_norm=final_norm)
    state = torch.load(ckpt, map_location=map_location, weights_only=True)
    sd = state.get('model_state_dict', state)
    model.load_state_dict(sd, strict=strict)
    return model

__all__ = ['load_best_head']
