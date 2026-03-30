#!/usr/bin/env python3
"""Run synthetic probe (forward CE loss) on top 3 unified_sweet_spot checkpoints and export enriched report.
Outputs: inventory_reports/top3_report.json
"""
from __future__ import annotations

import json
from pathlib import Path

import torch

INV_DIR = Path('inventory_reports')
TOP5 = INV_DIR/'top5_checkpoints.json'
OUT = INV_DIR/'top3_report.json'
TARGET_FILENAMES = { 'unified_final_step_25.pth', 'unified_final_step_20.pth', 'unified_final_step_8.pth' }
DEVICE = 'cpu'


def load_checkpoint(path: Path):
    ck = torch.load(path, map_location='cpu')
    return ck


def build_model(config):
    from src.core.models.impressioncore_b3_architecture import ImpressionCoreB3Model
    model = ImpressionCoreB3Model(config)
    return model


def synthetic_probe(model, config):
    vocab = getattr(config, 'vocab_size', 50257)
    seq = min(getattr(config, 'max_seq_length', 128), 128)
    model.eval()
    with torch.no_grad():
        x = torch.randint(0, vocab, (1, seq), device=DEVICE)
        mask = (x != 0).long()
        out = model(input_ids=x, image_features=None, audio_features=None, mask=mask)
        logits = out['logits'][:, :-1]
        target = x[:, 1:]
        loss = torch.nn.functional.cross_entropy(logits.reshape(-1, logits.size(-1)), target.reshape(-1))
        return float(loss.item())


def estimate_bits_per_param(size_mb: float, param_elems: int) -> float:
    if not param_elems:
        return float('nan')
    bytes_size = size_mb * 1024**2
    return bytes_size * 8 / param_elems


def main():
    data = json.loads(TOP5.read_text(encoding='utf-8'))
    top3 = [d for d in data if d['filename'] in TARGET_FILENAMES]
    enriched=[]
    for item in top3:
        path = Path(item['path'])
        ck = load_checkpoint(path)
        config = ck.get('config') if isinstance(ck, dict) else None
        state_dict = ck.get('model_state_dict') or ck.get('state_dict')
        param_elems = 0
        if isinstance(state_dict, dict):
            for t in state_dict.values():
                if isinstance(t, torch.Tensor):
                    param_elems += t.numel()
        probe_loss = None
        if config and state_dict:
            try:
                model = build_model(config)
                model.load_state_dict(state_dict, strict=False)
                model.to(DEVICE)
                probe_loss = synthetic_probe(model, config)
            except Exception as e:
                probe_loss = f"probe_failed: {e}"
        item_out = {
            'filename': item['filename'],
            'path': item['path'],
            'best_loss': item.get('best_loss'),
            'hist_tail': item.get('hist_tail'),
            'steps': item.get('steps'),
            'size_mb': item.get('size_mb'),
            'param_elems': param_elems,
            'bits_per_param_est': round(estimate_bits_per_param(item.get('size_mb'), param_elems),3) if param_elems else None,
            'probe_loss': probe_loss,
            'timestamp': item.get('timestamp')
        }
        enriched.append(item_out)
    OUT.write_text(json.dumps(enriched, indent=2), encoding='utf-8')
    print('TOP3_PROBE_COMPLETE entries=', len(enriched))

if __name__ == '__main__':
    main()
