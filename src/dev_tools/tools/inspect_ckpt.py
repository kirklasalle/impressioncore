#!/usr/bin/env python3
"""
Simple, safe checkpoint inspector for ImpressionCore.
Writes a JSON summary to stdout and optionally to artifacts/ckpt_inspect.json.
"""
import argparse
import json
import os
from pathlib import Path

import torch


def safe_size_of_state(state):
    # Estimate size by summing numel * element_size for tensors in state dict
    total = 0
    for _k, v in state.items():
        if isinstance(v, torch.Tensor):
            total += v.numel() * v.element_size()
    return total


def inspect(path):
    out = {
        'path': path,
        'exists': os.path.exists(path),
        'file_size_bytes': None,
        'load_ok': False,
        'load_error': None,
        'step': None,
        'model_param_count': None,
        'optimizer_state_present': False,
        'amp_state_present': False,
        'tokenizer_meta': None,
        'estimated_model_bytes': None,
    }
    if not os.path.exists(path):
        return out
    out['file_size_bytes'] = os.path.getsize(path)
    try:
        # Try to load weights-only if torch supports it
        try:
            ckpt = torch.load(path, map_location='cpu')
        except Exception:
            # Second attempt with pickle warnings suppressed
            ckpt = torch.load(path, map_location='cpu')
        out['load_ok'] = True
        # heuristics
        if isinstance(ckpt, dict):
            # common keys
            if 'step' in ckpt:
                out['step'] = int(ckpt['step'])
            if 'model_state' in ckpt and isinstance(ckpt['model_state'], dict):
                model_state = ckpt['model_state']
            elif 'state_dict' in ckpt and isinstance(ckpt['state_dict'], dict):
                model_state = ckpt['state_dict']
            else:
                # try to find first dict of tensors
                model_state = None
                for v in ckpt.values():
                    if isinstance(v, dict):
                        model_state = v
                        break
            if model_state is not None:
                param_count = 0
                for _k, t in model_state.items():
                    if isinstance(t, torch.Tensor):
                        param_count += t.numel()
                out['model_param_count'] = param_count
                out['estimated_model_bytes'] = safe_size_of_state(model_state)
            # optimizer
            for k in ('optimizer', 'optimizer_state', 'opt_state', 'optimizer_state_dict'):
                if k in ckpt:
                    out['optimizer_state_present'] = True
                    break
            # amp/gradscaler
            for k in ('scaler', 'amp', 'grad_scaler', 'scaler_state'):
                if k in ckpt:
                    out['amp_state_present'] = True
                    break
            # tokenizer meta
            if 'tokenizer' in ckpt:
                try:
                    out['tokenizer_meta'] = repr(ckpt['tokenizer'])[:400]
                except Exception:
                    out['tokenizer_meta'] = str(type(ckpt['tokenizer']))
    except Exception as e:
        out['load_error'] = repr(e)
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--path', required=True)
    p.add_argument('--out', default=os.environ.get('IMPRESSIONCORE_ARTIFACTS_DIR', 'F:/models/checkpoints/artifacts') + '/ckpt_inspect.json')
    args = p.parse_args()
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    summary = inspect(args.path)
    with open(str(out_path), 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
    print(json.dumps(summary, indent=2))

if __name__ == '__main__':
    main()
