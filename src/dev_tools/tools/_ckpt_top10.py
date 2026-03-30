#!/usr/bin/env python3
import csv
from pathlib import Path

p = Path('ckpts_all.csv')
if not p.exists():
    print('ckpts_all.csv not found in cwd')
    raise SystemExit(2)

rows = []
with p.open('r', encoding='utf-8') as f:
    rdr = csv.DictReader(f)
    for row in rdr:
        bl = row.get('best_loss')
        try:
            blv = float(bl) if bl not in (None,'','None') else None
        except Exception:
            blv = None
        try:
            sz = int(row.get('size_bytes') or 0)
        except Exception:
            sz = 0
        rows.append({'path':row.get('path'),'size':sz,'best_loss':blv,'global_step':row.get('global_step'),'read_error':row.get('read_error')})

rows_with_loss = [r for r in rows if r['best_loss'] is not None]
if rows_with_loss:
    rows_with_loss.sort(key=lambda x: x['best_loss'])
    print('Top checkpoints by best_loss (lowest first):')
    for i,r in enumerate(rows_with_loss[:10],1):
        print(f"{i}. {r['path']}  size={r['size']//1024//1024}MB  best_loss={r['best_loss']}  step={r['global_step']}  err={r['read_error']}")
else:
    print('No checkpoints with best_loss metadata found. Showing top 10 largest files:')
    rows.sort(key=lambda x: x['size'], reverse=True)
    for i,r in enumerate(rows[:10],1):
        print(f"{i}. {r['path']}  size={r['size']//1024//1024}MB  step={r['global_step']}  err={r['read_error']}")
