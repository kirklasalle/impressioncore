#!/usr/bin/env python3
"""Checkpoint Ranking Utility

Evaluates a directory of checkpoints and produces a ranked list of top-N based on:
 - Stored validation loss / best_loss if present
 - Fallback: most recent improvement (loss_history tail average)
 - Optional lightweight forward perplexity probe on a synthetic mini batch (configurable)

Enhancements:
 - Multi-extension support (.pth,.pt,.safetensors,.ckpt,.bin)
 - Safe load fallback (attempt weights_only when full unpickle fails)
 - Finite sentinel score (LARGE_SENTINEL) instead of inf for missing metrics
 - Optional custom extension list via --exts

Usage (example):
    python -m src.training.evaluation.checkpoint_ranker \
        --root F:/models/checkpoints/sweet_spot_recovery \
        --top 5 --probe --device cuda

Outputs JSON + pretty table.

Created: August 22, 2025
Updated: August 22, 2025
Author: Kirk LaSalle & GitHub Copilot
"""
from __future__ import annotations

import argparse
import json
import math
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import torch

DEFAULT_EXTS = [".pth", ".pt", ".safetensors", ".ckpt", ".bin"]
LARGE_SENTINEL = 1e12  # finite large number instead of inf for absent metrics


def _supports_weights_only() -> bool:
    # Heuristic: torch.load gained 'weights_only' param recently; test via signature inspection
    import inspect
    try:
        return 'weights_only' in inspect.signature(torch.load).parameters
    except Exception:  # pragma: no cover
        return False


def load_checkpoint(path: Path) -> dict[str, Any] | None:
    """Attempt to load checkpoint returning dict with metadata.
    Strategy:
      1. Try regular torch.load (full pickle) for metrics access
      2. On failure, if weights_only supported, retry with weights_only=True
    """
    try:
        ckpt = torch.load(path, map_location='cpu')  # full load for metrics
        ckpt['__file'] = str(path)
        ckpt['__load_mode'] = 'full'
        return ckpt
    except Exception as e1:
        # Fallback
        if _supports_weights_only():
            try:
                ckpt2 = torch.load(path, map_location='cpu', weights_only=True)
                # When weights_only, we only get state_dict; wrap for uniform handling
                if isinstance(ckpt2, dict):
                    wrapper = {
                        'model_state_dict': ckpt2,
                        '__file': str(path),
                        '__load_mode': 'weights_only'
                    }
                else:  # unusual case
                    wrapper = {
                        'model_state_obj': ckpt2,
                        '__file': str(path),
                        '__load_mode': 'weights_only_raw'
                    }
                return wrapper
            except Exception as e2:
                print(f"[WARN] failed to load {path.name}: {e1} | weights_only fallback failed: {e2}")
                return None
        else:
            print(f"[WARN] failed to load {path.name}: {e1}")
            return None


def extract_score(ckpt: dict[str, Any]) -> dict[str, Any]:
    loss_history = ckpt.get('loss_history') or []
    best_loss = ckpt.get('best_loss')
    val_best = None
    if isinstance(ckpt.get('best_val'), dict):
        val_best = ckpt['best_val'].get('value')
    hist_tail = None
    if loss_history:
        tail = loss_history[-min(10, len(loss_history)) :]
        hist_tail = float(sum(tail)/len(tail))
    # priority chain
    if val_best is not None:
        primary = float(val_best)
    elif best_loss is not None:
        primary = float(best_loss)
    elif hist_tail is not None:
        primary = hist_tail
    else:
        primary = LARGE_SENTINEL
    return {
        'primary_score': primary,
        'best_loss': best_loss,
        'val_best': val_best,
        'hist_tail': hist_tail,
        'steps': ckpt.get('global_step') or ckpt.get('step'),
        'load_mode': ckpt.get('__load_mode')
    }


def synthetic_probe(ckpt: dict[str, Any], device: str) -> float | None:
    config = ckpt.get('config')
    state_dict = ckpt.get('model_state_dict') or ckpt.get('state_dict')
    if config is None or state_dict is None:
        return None
    try:
        from src.core.models.impressioncore_b3_architecture import ImpressionCoreB3Model
        model = ImpressionCoreB3Model(config)
        model.load_state_dict(state_dict, strict=False)
        model.to(device)
        model.eval()
        with torch.no_grad():
            vocab = getattr(config, 'vocab_size', 50257)
            seq = getattr(config, 'max_seq_length', 128)
            batch = 1
            x = torch.randint(0, vocab, (batch, seq), device=device)
            attn = (x != 0).long()
            out = model(input_ids=x, image_features=None, audio_features=None, mask=attn)
            logits = out['logits'][:, :-1]
            target = x[:, 1:]
            loss = torch.nn.functional.cross_entropy(logits.reshape(-1, logits.size(-1)), target.reshape(-1))
            return float(loss.item())
    except Exception as e:
        print(f"[PROBE] failed: {e}")
        return None


def iter_checkpoint_files(root: Path, extensions: Iterable[str]) -> Iterable[Path]:
    for ext in extensions:
        yield from sorted(root.glob(f'*{ext}'))


def rank_checkpoints(root: Path, top: int, probe: bool, device: str, extensions: list[str]) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for p in iter_checkpoint_files(root, extensions):
        ckpt = load_checkpoint(p)
        if not ckpt:
            continue
        meta = extract_score(ckpt)
        probe_loss = synthetic_probe(ckpt, device) if probe else None
        meta.update({
            'path': str(p),
            'filename': p.name,
            'size_mb': round(p.stat().st_size / 1024**2, 2),
            'probe_loss': probe_loss,
            'timestamp': p.stat().st_mtime
        })
        entries.append(meta)
    def sort_key(e):
        return (
            e['probe_loss'] if e['probe_loss'] is not None else e['primary_score'],
            e['primary_score'],
            e['size_mb']
        )
    entries.sort(key=sort_key)
    return entries[:top]


def main():
    ap = argparse.ArgumentParser(description='Rank checkpoints by saved metrics + optional probe')
    ap.add_argument('--root', type=str, required=True, help='Checkpoint directory')
    ap.add_argument('--top', type=int, default=5, help='Top N')
    ap.add_argument('--probe', action='store_true', help='Run tiny synthetic perplexity probe')
    ap.add_argument('--device', type=str, default='cpu')
    ap.add_argument('--json-out', type=str, default=None)
    ap.add_argument('--exts', type=str, default=None, help='Comma list of extensions (default includes .pth,.pt,.safetensors,.ckpt,.bin)')
    args = ap.parse_args()
    root = Path(args.root)
    if not root.exists():
        print(f"[ERR] root not found: {root}")
        return
    extensions = [e.strip() if e.startswith('.') else f'.{e.strip()}' for e in args.exts.split(',')] if args.exts else DEFAULT_EXTS
    ranked = rank_checkpoints(root, args.top, args.probe, args.device, extensions)
    # Pretty print
    print("\nRANKED CHECKPOINTS:")
    print("# | primary | probe | best | val | tail | step | szMB | mode | file")
    for i, r in enumerate(ranked, 1):
        def fmt(v):
            if v is None:
                return '-'
            if isinstance(v, float) and (math.isinf(v) or v >= LARGE_SENTINEL):
                return '-'
            return f"{v:.4f}" if isinstance(v, float) else str(v)
        print(f"{i:>1} | {fmt(r['primary_score']):>7} | {fmt(r['probe_loss']):>5} | {fmt(r['best_loss']):>5} | {fmt(r['val_best']):>5} | {fmt(r['hist_tail']):>5} | {fmt(r['steps']):>5} | {r['size_mb']:.1f} | {r.get('load_mode','-'):>6} | {r['filename']}")
    if args.json_out:
        with open(args.json_out, 'w', encoding='utf-8') as f:
            json.dump(ranked, f, indent=2)
        print(f"\n[OUT] wrote {args.json_out}")

if __name__ == '__main__':
    main()
