#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #python #source_code #src/core/utils/verify_b2_embeddings.py #testing
**Category:** Core Implementation
**Status:** Active
"""









# Verify B2 Embeddings

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:01
# Author:** ImpressionCore Team
# Tags:** #python #source_code #src\\core\\utils\\verify_b2_embeddings.py #testing
# Category:** Core Implementation
# Status:** Active

"""
verify_b2_embeddings.py
----------------------
Checks that all required B2 embedding files exist for each dataset split (train/val/test).

Usage:
    python src/core/utils/verify_b2_embeddings.py --embedding_root F:/b2_embeddings --splits train val test

Returns missing files and a summary report.
"""
import argparse
from pathlib import Path


def verify_embeddings(embedding_root, splits):
    missing = []
    found = []
    for split in splits:
        split_dir = Path(embedding_root) / split
        if not split_dir.exists():
            print(f"[ERROR] Split directory missing: {split_dir}")
            missing.append(str(split_dir))
            continue
        files = list(split_dir.glob('*.npy'))
        if not files:
            print(f"[ERROR] No embedding files found in: {split_dir}")
            missing.append(str(split_dir))
        else:
            print(f"[OK] {len(files)} embedding files found in: {split_dir}")
            found.append(str(split_dir))
    print("\nSummary:")
    print(f"  Splits checked: {splits}")
    print(f"  Found: {found}")
    print(f"  Missing: {missing}")
    if missing:
        print("\n[FAIL] Some splits or files are missing. Please regenerate embeddings as needed.")
    else:
        print("\n[SUCCESS] All required embedding files are present.")

def main():
    parser = argparse.ArgumentParser(description="Verify B2 embedding completeness.")
    parser.add_argument('--embedding_root', type=str, required=True, help='Path to B2 embedding root directory')
    parser.add_argument('--splits', nargs='+', default=['train', 'val', 'test'], help='Dataset splits to check')
    args = parser.parse_args()
    verify_embeddings(args.embedding_root, args.splits)

if __name__ == "__main__":
    main()
