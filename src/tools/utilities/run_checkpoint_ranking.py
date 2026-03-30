#!/usr/bin/env python3
"""Batch rank all discovered checkpoints from inventory.
Requires inventory_full_scan.py to have been run.
Generates per-directory ranks and a global aggregation.
"""
import json
import math
import pathlib
import subprocess
import sys

INV_DIR = pathlib.Path('inventory_reports')
INV_FILE = INV_DIR/'f_models_checkpoint_inventory.csv'
RANKER = pathlib.Path('src/training/evaluation/checkpoint_ranker.py')
GLOBAL_OUT = INV_DIR/'global_top.json'
CANDIDATES_39M = INV_DIR/'candidates_approx_39m.json'
TARGET_MB_MIN, TARGET_MB_MAX = 70, 95  # rough FP16 39M param size window (~78-85MB) widened

if not INV_FILE.exists():
    print('Inventory file missing. Run inventory_full_scan.py first.', file=sys.stderr)
    sys.exit(1)

# Collect unique parent directories of checkpoints
parents=set()
for line in INV_FILE.read_text(encoding='utf-8').splitlines()[1:]:
    if not line.strip():
        continue
    path=line.split(',')[0]
    p = pathlib.Path(path).parent
    parents.add(str(p))

dirs=sorted(parents)
print(f"Found {len(dirs)} checkpoint directories. Running ranker per dir (no probe).")

results=[]
for d in dirs:
    json_out = INV_DIR / f"rank_{pathlib.Path(d).name}.json"
    cmd = [sys.executable,str(RANKER), '--root', d, '--top', '5', '--json-out', str(json_out)]
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True, timeout=300)
    except subprocess.CalledProcessError as e:
        out = f"ERROR for {d}: {e.output}"
    except subprocess.TimeoutExpired:
        out = f"TIMEOUT for {d}"
    results.append({'dir': d, 'output': out})

# Aggregate
aggregate=[]
for f in INV_DIR.glob('rank_*.json'):
    try:
        data=json.loads(f.read_text(encoding='utf-8'))
        for item in data:
            item['source_rank_file']=f.name
            aggregate.append(item)
    except Exception:
        continue

def agg_sort_key(e):
    # If primary_score missing or LARGE_SENTINEL-like, push back
    ps = e.get('primary_score', math.inf)
    if ps is None:
        ps = math.inf
    if isinstance(ps, int | float) and ps >= 1e12:
        ps = math.inf
    probe = e.get('probe_loss', math.inf) if e.get('probe_loss') is not None else ps
    return (probe, ps, e.get('size_mb', 1e9))

aggregate.sort(key=agg_sort_key)
# Save global top 25 and all
GLOBAL_OUT.write_text(json.dumps({'top25': aggregate[:25], 'all': aggregate}, indent=2), encoding='utf-8')

# Detect ~39M parameter sized candidates
candidates=[a for a in aggregate if TARGET_MB_MIN <= a.get('size_mb',0) <= TARGET_MB_MAX]
CANDIDATES_39M.write_text(json.dumps(candidates, indent=2), encoding='utf-8')

(INV_DIR/'checkpoint_rankings_raw.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
print('Ranking complete. Raw outputs + per-directory JSON scores + global_top.json + candidates_approx_39m.json saved.')
