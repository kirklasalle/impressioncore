import json
from pathlib import Path

import torch


def extract_fields(cfg):
    fields = {}
    if cfg is None:
        return fields
    # support dict or object
    if isinstance(cfg, dict):
        list(cfg.keys())
    else:
        [k for k in dir(cfg) if not k.startswith('_') and not callable(getattr(cfg, k))]

    inspect_keys = ['embed_dim', 'd_model', 'hidden_size', 'max_seq_len', 'n_ctx', 'context_length', 'context_size', 'rope_base', 'rope_scaling', 'rope_decay', 'rotary_pct', 'attn_type', 'use_alibi', 'alibi_bias', 'window_size']
    for k in inspect_keys:
        try:
            if isinstance(cfg, dict):
                if k in cfg:
                    fields[k] = cfg[k]
            else:
                if hasattr(cfg, k):
                    fields[k] = getattr(cfg, k)
        except Exception:
            pass
    return fields


def inspect_ckpt(path):
    print('\n---', path)
    try:
        ck = torch.load(str(path), map_location='cpu')
    except Exception as e:
        print(' load error:', e)
        return
    cfg = None
    if isinstance(ck, dict):
        cfg = ck.get('config')
    # print top-level keys
    if isinstance(ck, dict):
        print(' top_keys:', list(ck.keys()))
    # extract fields
    f = extract_fields(cfg)
    if f:
        print(' config_fields:')
        for k, v in f.items():
            print('  ', k, ':', v)
    else:
        print(' no useful config fields found')


def main():
    scan = Path(r'F:\data\embeddings\b3_39m\ckpt_scan.json')
    if not scan.exists():
        print('Missing scan file at', scan)
        return
    entries = json.loads(scan.read_text(encoding='utf-8'))
    # filter embed_dim == 768
    candidates = [e['path'] for e in entries if e.get('embed_dim_reported') == 768]
    if not candidates:
        print('No 768-d checkpoints found in scan.')
        return
    print('Found', len(candidates), '768-d checkpoints; inspecting:')
    for p in candidates:
        inspect_ckpt(Path(p))


if __name__ == '__main__':
    main()
