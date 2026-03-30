"""Scan F:\\models for PyTorch checkpoint files and report embed_dim (from config or inferred).

Writes summary JSON to F:\\data/embeddings\b3_39m\\ckpt_scan.json
"""
import json
from pathlib import Path

import torch


def infer_dim_from_state_dict(sd):
    # common token/embedding names
    for key in sd:
        if 'lm_head.weight' in key or 'token_embedding.weight' in key or 'wte.weight' in key or 'embeddings.word_embeddings.weight' in key:
            return sd[key].shape[1] if sd[key].dim() == 2 else None
    # fallback: try any 2D param where second dim is smallish
    for key in sd:
        v = sd[key]
        if hasattr(v, 'dim') and v.dim() == 2:
            return v.shape[1]
    return None


def scan_models(root=Path(r'F:\models')):
    results = []
    for p in root.rglob('*.pt'):
        try:
            ck = torch.load(str(p), map_location='cpu')
        except Exception as e:
            results.append({'path': str(p), 'error': f'load_error: {e}'})
            continue

        state_dict = None
        for k in ('model_state_dict', 'state_dict', 'model'):
            if isinstance(ck, dict) and k in ck:
                state_dict = ck[k]
                break
        if state_dict is None and isinstance(ck, dict):
            # maybe the dict itself is state_dict-like
            state_dict = ck

        cfg = ck.get('config') if isinstance(ck, dict) else None
        embed_dim = None
        try:
            if cfg is not None:
                if isinstance(cfg, dict):
                    embed_dim = cfg.get('embed_dim') or cfg.get('hidden_size') or cfg.get('d_model')
                else:
                    # object
                    embed_dim = getattr(cfg, 'embed_dim', None) or getattr(cfg, 'hidden_size', None) or getattr(cfg, 'd_model', None)
        except Exception:
            embed_dim = None

        if embed_dim is None and isinstance(state_dict, dict):
            try:
                embed_dim = infer_dim_from_state_dict(state_dict)
            except Exception:
                embed_dim = None

        results.append({'path': str(p), 'embed_dim_reported': embed_dim, 'has_config': cfg is not None})

    return results


def main():
    out = Path(r'F:\data\embeddings\b3_39m\ckpt_scan.json')
    out.parent.mkdir(parents=True, exist_ok=True)
    res = scan_models()
    with open(out, 'w', encoding='utf-8') as fh:
        json.dump(res, fh, indent=2)
    print('Wrote', out)


if __name__ == '__main__':
    main()
