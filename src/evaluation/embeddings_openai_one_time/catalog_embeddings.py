r"""
Recursively catalog all files in the given directories and summarize their structure and file statistics.

USAGE:
    # Activate the environment first (Windows PowerShell):
    #   .\.venv310\Scripts\Activate.ps1
    # Then run:
    python catalog_embeddings.py --dirs F:\data\embeddings\workspaceStorage F:\data\embeddings\OpenAI-DataExport_Kirk_LaSalle --output catalog_report.json
"""
import argparse
import json
import os
from pathlib import Path


def catalog_directory(root_path):
    catalog = []
    for dirpath, _dirnames, filenames in os.walk(root_path):
        for fname in filenames:
            fpath = os.path.join(dirpath, fname)
            try:
                stat = os.stat(fpath)
                catalog.append({
                    "relative_path": os.path.relpath(fpath, root_path),
                    "size_bytes": stat.st_size,
                    "modified": stat.st_mtime,
                    "created": stat.st_ctime,
                    "extension": Path(fname).suffix.lower(),
                })
            except Exception as e:
                catalog.append({
                    "relative_path": os.path.relpath(fpath, root_path),
                    "error": str(e)
                })
    return catalog

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dirs', nargs='+', required=True, help='Directories to catalog')
    parser.add_argument('--output', default='catalog_report.json', help='Output JSON file')
    args = parser.parse_args()

    report = {}
    for d in args.dirs:
        print(f"Cataloging: {d}")
        report[d] = catalog_directory(d)
        print(f"  {len(report[d])} files found.")

    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    print(f"Catalog written to {args.output}")

if __name__ == "__main__":
    main()
