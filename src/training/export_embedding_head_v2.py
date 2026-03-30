"""Export trained embedding head v2 checkpoints to portable formats.

Usage (PowerShell):
  .\\.venv310\\Scripts\\Activate.ps1
  \
  $env:PYTHONPATH='D:/Projects/impressioncore'
  \
  python -m src.training.export_embedding_head_v2 \
    --ckpt F:/models/checkpoints/b3/b3_39m_128k_v2_full30ep_3ksteps_v2_run3/ckpt_best.pt \
    --out-dir F:/models/checkpoints/b3/b3_39m_128k_v2_full30ep_3ksteps_v2_run3/export

Creates:
  - embedding_head_v2_state_dict.pt (raw state dict)
  - embedding_head_v2_full.pt (model object with weights)
  - embedding_head_v2_torchscript.pt (TorchScript scripted model)
  - (optionally) embedding_head_v2.safetensors if safetensors installed
  - export_manifest.json with metadata

Focus: safe, deterministic export without modifying training artifacts.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import torch

from src.training.embed_head import build_embedding_head


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--ckpt', required=True, help='Path to training checkpoint (ckpt_best.pt).')
    p.add_argument('--out-dir', required=True, help='Destination directory for export files.')
    p.add_argument('--device', default='cpu')
    p.add_argument('--weights-only', action='store_true', help='Attempt weights_only load for safer deserialization (PyTorch 2.5+).')
    return p.parse_args()


def safe_load(path: str, map_location, weights_only: bool):
    if not weights_only:
        return torch.load(path, map_location=map_location)
    try:
        return torch.load(path, map_location=map_location, weights_only=True)  # type: ignore[arg-type]
    except TypeError:
        print('[WARN] weights_only not supported; falling back to standard torch.load')
        return torch.load(path, map_location=map_location)


def main():
    args = parse_args()
    ckpt_path = Path(args.ckpt)
    if not ckpt_path.is_file():
        raise FileNotFoundError(f'Checkpoint not found: {ckpt_path}')
    run_dir = ckpt_path.parent
    config_path = run_dir / 'training_config_v2.json'
    if not config_path.is_file():
        raise FileNotFoundError(f'Expected config alongside checkpoint: {config_path}')
    cfg = json.loads(config_path.read_text())

    # Build model using recorded hyperparams
    version = cfg.get('head_version','v2')
    dropout = float(cfg.get('dropout', 0.05))
    final_norm = not bool(cfg.get('no_final_norm', False))
    model = build_embedding_head(version=version, dim=768, hidden=2048, dropout=dropout, final_norm=final_norm)

    ck = safe_load(str(ckpt_path), map_location=args.device, weights_only=args.weights_only)
    sd = ck['model_state_dict']
    model.load_state_dict(sd, strict=False)
    model.eval()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # State dict export
    torch.save(sd, out_dir / 'embedding_head_v2_state_dict.pt')

    # Full model export
    torch.save({'model': model, 'meta': {'export_time': time.time(), 'source': str(ckpt_path)}}, out_dir / 'embedding_head_v2_full.pt')

    # TorchScript
    try:
        example = torch.randn(2, 768)
        scripted = torch.jit.trace(model, example)
        torch.jit.save(scripted, out_dir / 'embedding_head_v2_torchscript.pt')
        ts_ok = True
    except Exception as e:  # pragma: no cover
        print(f'[WARN] TorchScript export failed: {e}')
        ts_ok = False

    # safetensors (optional)
    st_ok = False
    try:
        from safetensors.torch import save_file  # type: ignore
        save_file(sd, str(out_dir / 'embedding_head_v2.safetensors'))
        st_ok = True
    except Exception as e:  # pragma: no cover
        print(f'[INFO] safetensors export skipped: {e}')

    manifest = {
        'checkpoint': str(ckpt_path),
        'export_dir': str(out_dir),
        'version': version,
        'dropout': dropout,
        'final_norm': final_norm,
        'files': {
            'state_dict_pt': 'embedding_head_v2_state_dict.pt',
            'full_model_pt': 'embedding_head_v2_full.pt',
            'torchscript': 'embedding_head_v2_torchscript.pt' if ts_ok else None,
            'safetensors': 'embedding_head_v2.safetensors' if st_ok else None,
        },
        'time': time.time(),
    }
    (out_dir / 'export_manifest.json').write_text(json.dumps(manifest, indent=2))
    print('[EXPORT] complete:')
    print(json.dumps(manifest, indent=2))

if __name__ == '__main__':
    main()
