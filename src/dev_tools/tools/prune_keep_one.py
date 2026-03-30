"""Move all files in a directory except the chosen 'keep' file.

Default behavior: pick the file with the highest step number parsed from filename (digits), fallback to newest mtime.

Usage:
  D:\\Projects\\impressioncore/.venv310/Scripts/python.exe tools/prune_keep_one.py --dir "F:\\models/checkpoints/unified_sweet_spot/best"
"""
import argparse
import re
import shutil
import sys
import time
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--dir', required=True)
parser.add_argument('--dest-root', default=r'D:\Projects\impressioncore\backups')
parser.add_argument('--mode', choices=['highest-step','newest'], default='highest-step')
parser.add_argument('--dry-run', action='store_true')
args = parser.parse_args()

dirpath = Path(args.dir)
if not dirpath.exists():
    print('Directory not found:', dirpath)
    sys.exit(2)

files = [p for p in dirpath.iterdir() if p.is_file()]
if not files:
    print('No files found in', dirpath)
    sys.exit(0)

# helper: extract highest integer in filename
step_re = re.compile(r'(?:step[_-]|_)?(\d{2,7})')

def parse_step(p: Path):
    m = step_re.search(p.name)
    if m:
        return int(m.group(1))
    return None

keep = None
if args.mode == 'highest-step':
    files_with_step = [(parse_step(p), p) for p in files]
    # prefer files with a step, choose max step; if none, fallback to newest mtime
    files_with_valid = [t for t in files_with_step if t[0] is not None]
    if files_with_valid:
        keep = max(files_with_valid, key=lambda x: x[0])[1]
    else:
        keep = max(files, key=lambda p: p.stat().st_mtime)
else:
    keep = max(files, key=lambda p: p.stat().st_mtime)

print('Keeping:', keep.name)

timestamp = time.strftime('%Y%m%d_%H%M%S')
dest_dir = Path(args.dest_root) / f'pruned_checkpoints_{timestamp}' / dirpath.name
if not args.dry_run:
    dest_dir.mkdir(parents=True, exist_ok=True)

moved = []
for p in files:
    if p == keep:
        continue
    target = dest_dir / p.name
    print('Moving', p, '->', target)
    if not args.dry_run:
        try:
            shutil.move(str(p), str(target))
            moved.append((p, target))
        except Exception as e:
            print('Error moving', p, e)

print('\nDone. Moved', len(moved), 'files to', dest_dir)
if moved:
    print('Sample moved:', moved[0][1])
