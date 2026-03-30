"""Check checkpoint file existence, size, and attempt to load model_state_dict safely to detect corruption.

Usage:
  D:\\Projects\\impressioncore/.venv310/Scripts/python.exe tools/check_ckpt_integrity.py --path "F:\\models/checkpoints/unified_sweet_spot/best/best_loss_step_11620.pth"
"""
import argparse
from pathlib import Path

import torch

parser = argparse.ArgumentParser()
parser.add_argument('--path', required=True)
args = parser.parse_args()

p = Path(args.path)
print('Path:', p)
if not p.exists():
    print('MISSING')
    raise SystemExit(2)

print('Size (MB):', p.stat().st_size/1024/1024)

# Attempt to load safely
try:
    print('Attempting torch.load(map_location="cpu")...')
    ckpt = torch.load(str(p), map_location='cpu')
    print('Loaded checkpoint type:', type(ckpt))
    if isinstance(ckpt, dict):
        keys = list(ckpt.keys())
        print('Top-level keys:', keys)
        if 'model_state_dict' in ckpt:
            msd = ckpt['model_state_dict']
            print('model_state_dict keys count:', len(msd) if hasattr(msd, '__len__') else 'unknown')
    print('SUCCESS')
except Exception as e:
    print('LOAD FAILED:', repr(e))
    # for truncated files try to show first bytes
    try:
        with open(str(p), 'rb') as f:
            head = f.read(512)
            print('First 512 bytes (hex):', head[:512].hex())
    except Exception as e2:
        print('Failed reading raw bytes:', e2)
    raise
