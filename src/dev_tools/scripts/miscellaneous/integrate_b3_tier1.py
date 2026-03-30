#!/usr/bin/env python3
r"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #python #source_code #src/scripts/miscellaneous/integrate_b3_tier1.py
**Category:** Source Code
**Status:** Active
"""


"""
B3 Embeddings Tier 1 Integration Script

Copies critical model and embedding files to F: drive, verifying integrity and logging all actions.

Usage: python integrate_b3_tier1.py
"""
import datetime
import hashlib
import logging
import os
import shutil

# === CONFIGURATION ===
# Source directory containing all B3 embedding files
SRC = r"F:\data/embeddings/b3_embeddings"

# File integration map: (source filename, destination directory)
TIER1_FILES = [
    ("impressioncore_b1_flagship_1.pth", r"F:\models/flagship"),
    ("vector_database_1.db", r"F:\models"),
    ("b1_checkpoint_epoch_0_1.pt", r"F:\models/checkpoint"),
]

# Logging setup
log_dir = os.path.join(os.path.dirname(__file__), "integration_logs")
os.makedirs(log_dir, exist_ok=True)
log_path = os.path.join(log_dir, f"b3_tier1_integration_{datetime.datetime.now():%Y%m%d_%H%M%S}.log")
logging.basicConfig(filename=log_path, level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")


def sha256sum(filepath, chunk_size=1024*1024):
    """Compute SHA256 hash of a file."""
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(chunk_size), b''):
            h.update(chunk)
    return h.hexdigest()


def copy_and_verify(src_path, dst_path):
    """
    Copy file from src_path to dst_path, verifying SHA256 before and after.
    Returns True if successful, False otherwise.
    """
    try:
        src_hash = sha256sum(src_path)
        shutil.copy2(src_path, dst_path)
        dst_hash = sha256sum(dst_path)
        if src_hash == dst_hash:
            logging.info(f"SUCCESS: {os.path.basename(src_path)} copied and verified.")
            return True
        else:
            logging.error(f"HASH MISMATCH: {src_path} to {dst_path}")
            return False
    except Exception as e:
        logging.error(f"ERROR copying {src_path} to {dst_path}: {e}")
        return False


def main():
    logging.info("=== B3 Tier 1 Integration Started ===")
    for fname, dest_dir in TIER1_FILES:
        src_file = os.path.join(SRC, fname)
        os.makedirs(dest_dir, exist_ok=True)
        dst_file = os.path.join(dest_dir, fname)
        if not os.path.exists(src_file):
            logging.error(f"SOURCE MISSING: {src_file}")
            continue
        if os.path.exists(dst_file):
            logging.info(f"SKIP: {dst_file} already exists.")
            continue
        logging.info(f"Copying {src_file} -> {dst_file}")
        copy_and_verify(src_file, dst_file)
    logging.info("=== B3 Tier 1 Integration Complete ===")

if __name__ == "__main__":
    main()
