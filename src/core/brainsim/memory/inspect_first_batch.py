#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #memory_management #python #source_code #src/brainsim/memory/inspect_first_batch.py
**Category:** Source Code
**Status:** Active
"""









# Inspect First Batch

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:00
# Author:** ImpressionCore Team
# Tags:** #memory_management #python #source_code #src\\brainsim\\memory\\inspect_first_batch.py
# Category:** Source Code
# Status:** Active

import pickle
import sys

INPUT_PATH = "F:/impressioncore-b1-uks-output/aggregated_data.pkl"
OUTPUT_PATH = "F:/impressioncore-b1-uks-output/first_batch_for_inspection.pkl"

def isolate_first_batch():
    """
    Reads the first batch from the aggregated data file and saves it to a new file.
    """
    print(f"[INFO] Attempting to read first batch from {INPUT_PATH}...")
    try:
        with open(INPUT_PATH, "rb") as f:
            first_batch = pickle.load(f)

        print(f"[INFO] Successfully loaded first batch with {len(first_batch)} items.")

        with open(OUTPUT_PATH, "wb") as f:
            pickle.dump(first_batch, f)

        print(f"[SUCCESS] First batch has been isolated and saved to {OUTPUT_PATH}")

    except EOFError:
        print("[ERROR] The aggregated data file appears to be empty or corrupted.")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    isolate_first_batch()
