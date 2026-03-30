import statistics
from pathlib import Path

import torch

ART = Path(r'F:/models/checkpoints/artifacts')
files = sorted(ART.glob('bad_batch_*.pt'), key=lambda p: p.stat().st_mtime, reverse=True)[:40]
reports = []
for p in files:
    try:
        d = torch.load(p, map_location='cpu')
    except Exception as e:
        reports.append((p.name, 'LOAD_ERROR', str(e)))
        continue
    meta = d.get('meta', {})
    step = meta.get('step')
    rec = {'file': p.name, 'step': step}
    for k in ('input_ids','labels','attention_mask'):
        v = d.get(k)
        if v is None:
            rec[k] = None
            continue
        try:
            arr = v.numpy()
            rec[k] = {
                'shape': list(arr.shape),
                'dtype': str(v.dtype),
                'min': int(arr.min()),
                'max': int(arr.max()),
                'mean': float(arr.mean()),
            }
            if k == 'input_ids' or k == 'labels':
                total = arr.size
                zeros = int((arr == 0).sum())
                rec[k]['zero_pct'] = zeros/total*100.0
        except Exception as e:
            rec[k] = f'ERR:{e}'
    reports.append(rec)

# Summarize
print(f'ANALYZED {len(reports)} files (most recent first)')
steps = [r.get('step') for r in reports if isinstance(r, dict) and r.get('step') is not None]
if steps:
    print('Step range:', min(steps), '->', max(steps))

def summarize_key(key):
    vals = [r[key] for r in reports if isinstance(r, dict) and r.get(key) is not None]
    if not vals:
        return None
    shapes = [v['shape'] for v in vals if isinstance(v, dict) and 'shape' in v]
    zero_pcts = [v.get('zero_pct') for v in vals if isinstance(v, dict) and 'zero_pct' in v]
    mins = [v['min'] for v in vals if isinstance(v, dict) and 'min' in v]
    maxs = [v['max'] for v in vals if isinstance(v, dict) and 'max' in v]
    return {
        'count': len(vals),
        'shapes_sample': shapes[:3],
        'min_overall': min(mins) if mins else None,
        'max_overall': max(maxs) if maxs else None,
        'zero_pct_mean': statistics.mean(zero_pcts) if zero_pcts else None,
    }

for k in ('input_ids','labels','attention_mask'):
    s = summarize_key(k)
    print(f'--- {k} summary ---')
    print(s)

print('\nSample rows:')
for r in reports[:5]:
    print(r)
