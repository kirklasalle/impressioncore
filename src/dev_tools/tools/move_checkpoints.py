"""Move checkpoint folders from F: to a destination on D: (workspace backups).

Usage:
  D:\\Projects\\impressioncore/.venv310/Scripts/python.exe tools/move_checkpoints.py --paths "F:\\models/checkpoints/unified_sweet_spot/best" "F:\\models/checkpoints/archive"
"""
import argparse
import contextlib
import os
import shutil
import sys
import time
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--dest', default=r'D:\Projects\impressioncore\backups')
parser.add_argument('--paths', nargs='+', required=True)
parser.add_argument('--dry-run', action='store_true')
args = parser.parse_args()

dest_root = Path(args.dest)
if not dest_root.exists():
    dest_root.mkdir(parents=True, exist_ok=True)

timestamp = time.strftime('%Y%m%d_%H%M%S')
dest_dir = dest_root / f'pruned_checkpoints_{timestamp}'
if not args.dry_run:
    dest_dir.mkdir()

# compute total size
paths = [Path(p) for p in args.paths]
missing = [str(p) for p in paths if not p.exists()]
if missing:
    print('Missing paths (won\'t proceed):')
    for m in missing:
        print('  ', m)
    sys.exit(2)

def dir_size(p: Path):
    total = 0
    for dirpath, _dirnames, filenames in os.walk(p):
        for fn in filenames:
            with contextlib.suppress(Exception):
                total += (Path(dirpath)/fn).stat().st_size
    return total

total_bytes = sum(dir_size(p) for p in paths)
print(f'Total to move: {total_bytes/1024/1024/1024:.2f} GB')

# check dest drive free
dest_drive = os.path.splitdrive(str(dest_dir))[0] + '\\'
st = shutil.disk_usage(dest_drive)
print(f'Dest drive {dest_drive} free {st.free/1e9:.2f} GB')

if st.free < total_bytes + 1_000_000_000:  # require ~1GB cushion
    print('Not enough free space on destination drive. Aborting.')
    sys.exit(3)

# perform moves
for p in paths:
    target = dest_dir / p.name
    print(f'Moving {p} -> {target}')
    if args.dry_run:
        continue
    try:
        shutil.move(str(p), str(target))
        print('Moved OK')
    except Exception as e:
        print('Error moving', p, e)

print('Done. New backup dir:', dest_dir)
