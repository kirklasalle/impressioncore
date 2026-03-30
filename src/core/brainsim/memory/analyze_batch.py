#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #memory_management #python #source_code #src/brainsim/memory/analyze_batch.py
**Category:** Source Code
**Status:** Active
"""









# Analyze Batch

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:00
# Author:** ImpressionCore Team
# Tags:** #memory_management #python #source_code #src\\brainsim\\memory\\analyze_batch.py
# Category:** Source Code
# Status:** Active

import pickle
import sys

INPUT_PATH = "F:/impressioncore-b1-uks-output/first_batch_for_inspection.pkl"

def analyze_batch():
    """
    Loads the isolated first batch and prints information about each item.
    """
    print(f"[INFO] Analyzing batch file: {INPUT_PATH}")
    try:
        with open(INPUT_PATH, "rb") as f:
            batch = pickle.load(f)

        print(f"[INFO] Loaded batch with {len(batch)} items. Analyzing contents:")

        for i, item in enumerate(batch):
            source = item.get('metadata', {}).get('source', 'N/A')
            text_size = len(item.get('text', ''))
            image_path = item.get('image_path', 'N/A')

            print(f"--- Item {i+1} ---")
            print(f"  Source: {source}")
            print(f"  Text Size: {text_size} bytes")
            print(f"  Image Path: {image_path}")

            # Add a check for unusually large text files
            if text_size > 10_000_000: # 10MB
                print("  [WARNING] Very large text file detected!")

    except Exception as e:
        print(f"[ERROR] Failed to analyze batch: {e}")
        sys.exit(1)

if __name__ == "__main__":
    analyze_batch()
