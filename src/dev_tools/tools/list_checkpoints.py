"""List drive usage and largest files under F:\\models/checkpoints.

Run with the project's venv Python, e.g.
D:\\Projects\\impressioncore/.venv310/Scripts/python.exe tools/list_checkpoints.py
"""
import argparse
import heapq
import os
import shutil

parser = argparse.ArgumentParser()
parser.add_argument("--root", default=r"F:\\models\\checkpoints")
parser.add_argument("--top", type=int, default=50)
args = parser.parse_args()
root = args.root

try:
    du = shutil.disk_usage(os.path.splitdrive(root)[0] + "\\")
    print(f"Drive {os.path.splitdrive(root)[0]}: total={du.total/1e9:.2f}GB free={du.free/1e9:.2f}GB used={du.used/1e9:.2f}GB")
except Exception as e:
    print("Error getting disk usage:", e)

files = []
for dirpath, _dirs, filenames in os.walk(root):
    for fn in filenames:
        fp = os.path.join(dirpath, fn)
        try:
            sz = os.path.getsize(fp)
        except OSError:
            continue
        files.append((sz, fp))

if not files:
    print(f"No files found under {root}")
    raise SystemExit(0)

largest = heapq.nlargest(args.top, files)
print(f"\nTop {len(largest)} largest files under {root}:")
for sz, fp in largest:
    print(f"{sz/1024/1024:10.2f} MB\t{fp}")

# Directory size summary (top 20)
print("\nDirectory size summary (top 20):")
dir_sizes = {}
for sz, fp in files:
    dirpath = os.path.dirname(fp)
    dir_sizes[dirpath] = dir_sizes.get(dirpath, 0) + sz

top_dirs = heapq.nlargest(20, dir_sizes.items(), key=lambda x: x[1])
for dirpath, total in top_dirs:
    print(f"{total/1024/1024:10.2f} MB\t{dirpath}")

print("\nScan complete.")
