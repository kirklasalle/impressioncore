#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #python #source_code #src/core/utils/verify_and_copy_embeddings.py
**Category:** Core Implementation
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:01
# Author:** ImpressionCore Team
# Tags:** #python #source_code #src\\core\\utils\\verify_and_copy_embeddings.py
# Category:** Core Implementation
# Status:** Active

"""
ImpressionCore Utility: Verify and Copy Embeddings

Scans a source directory (default: F:/datasets/) for embedding files (.json, .pkl, .npy),
and copies them to a user-specified destination directory (e.g., F:/impressioncore-b1-embeddings-062125/),
preserving subfolder structure. Skips files that already exist at the destination with the same size.

Usage:
    python src/core/utils/verify_and_copy_embeddings.py

- Prompts for destination directory (default: F:/impressioncore-b1-embeddings-062125/)
- Logs all actions and prints a summary at the end

Complies with ImpressionCore Copilot Prime Directive and Sacred Covenant.
"""
import shutil
import sys
from pathlib import Path

try:
    from .core.utils.rich_logging import setup_rich_logging
    logger = setup_rich_logging(__name__)
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("verify_and_copy_embeddings")

def prompt_destination(default_dest):
    dest = input(f"Enter destination directory for embeddings [default: {default_dest}]: ").strip()
    return dest if dest else default_dest

def find_embedding_files(src_dir):
    """
    Recursively find all .json, .pkl, .npy files in src_dir.
    Returns a list of Path objects.
    """
    exts = {'.json', '.pkl', '.npy'}
    files = [p for p in Path(src_dir).rglob('*') if p.suffix.lower() in exts and p.is_file()]
    return files

def copy_embeddings(src_files, src_root, dest_root):
    """
    Copy embedding files from src_root to dest_root, preserving relative paths.
    Skips files that already exist at dest with same size.
    Returns stats dict.
    """
    copied, skipped, errors = 0, 0, 0
    for src_file in src_files:
        rel_path = src_file.relative_to(src_root)
        dest_file = Path(dest_root) / rel_path
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            if dest_file.exists() and dest_file.stat().st_size == src_file.stat().st_size:
                logger.debug(f"[SKIP] {dest_file} already exists (same size)")
                skipped += 1
                continue
            shutil.copy2(src_file, dest_file)
            logger.info(f"[COPY] {src_file} -> {dest_file}")
            copied += 1
        except Exception as e:
            logger.error(f"[ERROR] Failed to copy {src_file} -> {dest_file}: {e}")
            errors += 1
    return {'copied': copied, 'skipped': skipped, 'errors': errors}

def main():
    print("\nImpressionCore Embedding Verification & Copy Utility\n" + "-"*50)
    src_root = Path("F:/datasets/")
    if not src_root.exists():
        logger.error(f"Source directory does not exist: {src_root}")
        sys.exit(1)
    print(f"Scanning for embedding files in: {src_root}")
    src_files = find_embedding_files(src_root)
    print(f"Found {len(src_files)} embedding files (.json, .pkl, .npy)")
    default_dest = "F:/impressioncore-b1-embeddings-062125/"
    dest_root = Path(prompt_destination(default_dest))
    dest_root.mkdir(parents=True, exist_ok=True)
    print(f"Copying to: {dest_root}\n")
    stats = copy_embeddings(src_files, src_root, dest_root)
    print("\nSummary:")
    print(f"  Copied:  {stats['copied']}")
    print(f"  Skipped: {stats['skipped']}")
    print(f"  Errors:  {stats['errors']}")
    print("\nDone.")

if __name__ == "__main__":
    main()
