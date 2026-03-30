"""Export utilities for the production embedding reconstruction head.

Creates (baseline):
    - model.safetensors (state dict)
    - model.torchscript.pt (scripted module for deployment, CPU)
    - export_meta.json (metadata)

Optional (if --onnx):
    - model.onnx (opset 17, dynamic batch, exported in eval mode)

Example:
    python -m src.inference.export_head \
            --ckpt-dir F:/models/checkpoints/b3/b3_39m_128k_v2_headft_long_restart \
            --out-dir  F:/models/production/embedding_head_v2 \
            --onnx --force
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import torch
from safetensors.torch import save_file

from src.inference.embedding_head_loader import load_best_head


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--ckpt-dir', type=str, required=True)
    p.add_argument('--out-dir', type=str, required=True)
    p.add_argument('--device', type=str, default='cuda' if torch.cuda.is_available() else 'cpu')
    p.add_argument('--force', action='store_true', help='Overwrite existing export directory')
    p.add_argument('--onnx', action='store_true', help='Also export ONNX model (opset 17)')
    return p.parse_args()


def main():
    args = parse_args()
    out = Path(args.out_dir)
    if out.exists() and any(out.iterdir()) and not args.force:
        raise SystemExit(f"Refusing to overwrite non-empty directory: {out} (use --force)")
    out.mkdir(parents=True, exist_ok=True)

    # Keep on CPU for portable TorchScript export (avoid mixed device issues)
    model = load_best_head(args.ckpt_dir, map_location='cpu')
    model.eval()

    # Save state dict (safetensors)
    sd_path = out / 'model.safetensors'
    save_file(model.state_dict(), str(sd_path))

    # TorchScript
    example = torch.randn(2, 768)
    with torch.no_grad():
        scripted = torch.jit.trace(model, example)
    ts_path = out / 'model.torchscript.pt'
    scripted.save(str(ts_path))

    onnx_path = None
    if args.onnx:
        onnx_path = out / 'model.onnx'
        dyn_axes = { 'input': {0: 'batch'}, 'output': {0: 'batch'} }
        torch.onnx.export(
            model,
            example,
            str(onnx_path),
            input_names=['input'],
            output_names=['output'],
            dynamic_axes=dyn_axes,
            opset_version=17,
            do_constant_folding=True,
        )

    meta = {
        'source_ckpt_dir': str(args.ckpt_dir),
        'export_time': time.strftime('%B %d, %Y %I:%M:%S %p'),
        'device': args.device,
        'files': {
            'state_dict_safetensors': str(sd_path),
            'torchscript': str(ts_path),
            'onnx': str(onnx_path) if onnx_path else None
        }
    }
    (out / 'export_meta.json').write_text(json.dumps(meta, indent=2))
    print(f"Export complete: {out}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
