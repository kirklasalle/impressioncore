#!/usr/bin/env python3
"""Full F:/models recursive inventory.
Outputs CSV + JSON summaries under inventory_reports/.
"""
import json
import os
import pathlib
from collections import defaultdict

ROOT = pathlib.Path('F:/models')
OUT = pathlib.Path('inventory_reports')
exts = {'.pth','.pt','.safetensors','.bin','.ckpt'}

def main():
    OUT.mkdir(exist_ok=True)
    records=[]
    for dirpath,_,files in os.walk(ROOT):
        for fn in files:
            ext = os.path.splitext(fn)[1].lower()
            if ext in exts:
                fp = pathlib.Path(dirpath)/fn
                try:
                    st=fp.stat()
                except OSError:
                    continue
                records.append({
                    'path': str(fp),
                    'ext': ext,
                    'size_bytes': st.st_size,
                    'size_mb': round(st.st_size/1024**2,2),
                    'mtime': st.st_mtime
                })
    # write CSV
    lines=["path,ext,size_mb,mtime"]
    for r in records:
        lines.append(f"{r['path']},{r['ext']},{r['size_mb']},{r['mtime']}")
    (OUT/'f_models_checkpoint_inventory.csv').write_text('\n'.join(lines),encoding='utf-8')
    agg=defaultdict(lambda:{'count':0,'bytes':0})
    for r in records:
        agg[r['ext']]['count']+=1
        agg[r['ext']]['bytes']+=r['size_bytes']
    summary=[{'ext':k,'count':v['count'],'total_gb':round(v['bytes']/1024**3,2)} for k,v in sorted(agg.items())]
    (OUT/'f_models_checkpoint_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    top20=sorted(records,key=lambda r:r['size_bytes'],reverse=True)[:20]
    (OUT/'f_models_top20_largest.json').write_text(json.dumps(top20,indent=2),encoding='utf-8')
    print(f"INVENTORY_COMPLETE files={len(records)} top20={len(top20)}")

if __name__=='__main__':
    main()
