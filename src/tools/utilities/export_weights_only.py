#!/usr/bin/env python3
"""Export weights-only stripped checkpoints for top 3 unified files.
Creates *_weights_only.pth alongside originals + report JSON.
"""
from __future__ import annotations

import json
from pathlib import Path

import torch

INV_DIR = Path('inventory_reports')
TOP5 = INV_DIR/'top5_checkpoints.json'
REPORT = INV_DIR/'top3_weights_only_report.json'
TARGET_FILENAMES = { 'unified_final_step_25.pth', 'unified_final_step_20.pth', 'unified_final_step_8.pth' }


def main():
    data = json.loads(TOP5.read_text(encoding='utf-8'))
    targets = [d for d in data if d['filename'] in TARGET_FILENAMES]
    outputs=[]
    for item in targets:
        path = Path(item['path'])
        ck = torch.load(path, map_location='cpu')
        state = ck.get('model_state_dict') or ck.get('state_dict')
        config = ck.get('config')
        if not isinstance(state, dict):
            continue
        out_obj = {
            'model_state_dict': state,
            'config': config
        }
        out_path = path.with_name(path.stem + '_weights_only.pth')
        torch.save(out_obj, out_path)
        size_mb = round(out_path.stat().st_size/1024**2,2)
        param_elems = sum(t.numel() for t in state.values() if isinstance(t, torch.Tensor))
        bits_per_param = (out_path.stat().st_size*8/param_elems) if param_elems else None
        outputs.append({
            'original': str(path),
            'weights_only': str(out_path),
            'weights_only_size_mb': size_mb,
            'param_elems': param_elems,
            'bits_per_param': round(bits_per_param,3) if bits_per_param else None
        })
    REPORT.write_text(json.dumps(outputs, indent=2), encoding='utf-8')
    print('WEIGHTS_ONLY_EXPORT_COMPLETE entries=', len(outputs))

if __name__ == '__main__':
    main()
