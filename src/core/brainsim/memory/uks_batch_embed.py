#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #gpu_optimization #memory_management #python #source_code #src/brainsim/memory/uks_batch_embed.py #tokenization
**Category:** Source Code
**Status:** Active
"""









# Uks Batch Embed

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:00
# Author:** ImpressionCore Team
# Tags:** #gpu_optimization #memory_management #python #source_code #src\\brainsim\\memory\\uks_batch_embed.py #tokenization
# Category:** Source Code
# Status:** Active

"""
Batch embedding and UKS population script for ImpressionCore-b1.

Supports text, image, and (optionally) audio transcription data.
"""

import os
import sys

# Add project root to the Python path to resolve module imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

# This manual path manipulation is removed to rely on standard `python -m` execution
# project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
# src_path = os.path.join(project_root, 'src')
# if project_root not in sys.path:
#     sys.path.insert(0, project_root)
# if src_path not in sys.path:
#     sys.path.insert(0, src_path)
import logging
import pickle

from memory_profiler import profile

from src.data.tokenization.tokenizer import initialize_models, tokenize

UKS_DB_PATH = "F:/impressioncore-b1-uks-output/uks_db.pkl"  # Always output to F:/impressioncore-b1-uks-output/
ERROR_LOG_PATH = "F:/impressioncore-b1-uks-output/memory_error_log.txt"

# --- Setup Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Create a specific logger for memory errors
mem_error_logger = logging.getLogger('MemoryErrorLogger')
handler = logging.FileHandler(ERROR_LOG_PATH)
mem_error_logger.addHandler(handler)
mem_error_logger.setLevel(logging.ERROR)
# ---------------------

MAX_TEXT_LENGTH = 1_000_000  # Set a reasonable character limit
BATCH_SIZE = 1000  # Tune as needed for memory



def embed_and_store_streaming(input_file, uks_db, models, batch_size: int = BATCH_SIZE):
    """
    Stream batches from a single pickle file and update the uks_db dictionary.
    """
    import gc
    total = 0
    batch_idx = 0
    print(f"[INFO] Starting to process {input_file}...")
    with open(input_file, "rb") as f:
        while True:
            try:
                batch = pickle.load(f)
                batch_idx += 1
                print(f"[INFO] Loaded batch {batch_idx} with {len(batch)} items.")
                for i in range(0, len(batch), batch_size):
                    sub_batch = batch[i:i+batch_size]
                    _process_batch(sub_batch, uks_db, models)
                    total += len(sub_batch)
                print(f"[INFO] Processed {total} total entries from {input_file}...")
                gc.collect()
            except EOFError:
                print(f"[INFO] Finished processing {input_file} after {batch_idx} batches.")
                break
            except Exception as e:
                print(f"[ERROR] Failed during processing of {input_file}: {e}")
                break

from PIL import Image


@profile
def _process_batch(batch, uks_db, models):
    text_tokenizer, image_model, image_preprocessor = models
    for entry in batch:
        # --- Sanity Check for oversized data ---
        if len(entry.get("text", "")) > MAX_TEXT_LENGTH:
            source = entry.get('metadata', {}).get('source', 'Unknown')
            print(f"[WARN] Skipping entry from {source} due to excessive text length ({len(entry['text'])} characters).")
            continue
        # ----------------------------------------

        # If 'image' is a PIL.Image or bytes, replace with file path only
        if isinstance(entry.get("image"), Image.Image):
            # This should not happen if aggregation is correct, but handle just in case
            entry["image"] = entry["metadata"].get("source")
        # If 'image' is bytes or other, skip or log
        if isinstance(entry.get("image"), bytes):
            print(f"[WARN] Skipping in-memory image bytes for entry {entry.get('metadata', {}).get('source')}")
            entry["image"] = None

        try:
            # Tokenize: should load/process image from file path only
            tokenized = tokenize(entry, text_tokenizer, image_model, image_preprocessor)

            # --- Convert tensors to CPU lists to free GPU memory ---
            text_ids_list = tokenized.get("text_ids").cpu().tolist() if tokenized.get("text_ids") is not None else None
            image_features_list = tokenized.get("image_features").cpu().tolist() if tokenized.get("image_features") is not None else None
            # --------------------------------------------------------

            embedding = {
                "text_ids": text_ids_list,
                "image_features": image_features_list,
                "metadata": tokenized.get("metadata", {})
            }
            key = entry.get("id") or str(hash(str(entry)))
            uks_db[key] = embedding

        except MemoryError:
            source = entry.get('metadata', {}).get('source', 'Unknown')
            error_msg = f"MemoryError while processing: {source}"
            print(f"[FATAL] {error_msg}")
            mem_error_logger.error(error_msg)
            # Skip this item and continue with the next
            continue
        except Exception as e:
            print(f"[ERROR] Tokenization failed for entry {entry.get('metadata', {}).get('source')}: {e}")
            continue

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Batch embed and populate UKS (streaming mode).")
    parser.add_argument("--input", type=str, nargs='+', required=True, help="Path(s) to input data file(s) (pickle, batches)")
    parser.add_argument("--append", action='store_true', help="Append to existing UKS DB (default: overwrite)")
    parser.add_argument("--batch_size", type=int, default=BATCH_SIZE, help="Batch size for processing")
    args = parser.parse_args()

    # --- Load Models Once ---
    models = initialize_models()
    if not all(models):
        print("[FATAL] Could not initialize models. Exiting.")
        sys.exit(1)
    # ----------------------

    uks_db_path = UKS_DB_PATH
    uks_db = {}

    if args.append and os.path.exists(uks_db_path):
        try:
            with open(uks_db_path, "rb") as f:
                uks_db = pickle.load(f)
            print(f"[INFO] Appending to existing UKS DB with {len(uks_db)} entries.")
        except Exception as e:
            print(f"[WARN] Could not load existing UKS DB for appending: {e}. Starting fresh.")
    elif not args.append:
        print("[INFO] Starting with a fresh UKS DB.")

    for input_file in args.input:
        embed_and_store_streaming(input_file, uks_db, models, args.batch_size)

    try:
        with open(uks_db_path, "wb") as f:
            pickle.dump(uks_db, f)
        print(f"[SUCCESS] UKS populated with {len(uks_db)} unique entries. Saved to {uks_db_path}.")
    except Exception as e:
        print(f"[ERROR] Failed to save UKS DB to {uks_db_path}: {e}")
