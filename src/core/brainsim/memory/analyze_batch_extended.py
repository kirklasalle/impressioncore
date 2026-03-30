#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #memory_management #python #source_code #src/brainsim/memory/analyze_batch_extended.py
**Category:** Source Code
**Status:** Active
"""









# Analyze Batch Extended

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:00
# Author:** ImpressionCore Team
# Tags:** #memory_management #python #source_code #src\\brainsim\\memory\\analyze_batch_extended.py
# Category:** Source Code
# Status:** Active

import pickle
import sys


def analyze_batch_extended(file_path):
    """
    Analyzes a batch of data from a pickle file, printing metadata and data types for each item.
    """
    print(f"Running extended analysis on batch file: {file_path}")
    try:
        with open(file_path, 'rb') as f:
            data = pickle.load(f)

        print(f"Total items in batch: {len(data)}")

        for i, item in enumerate(data):
            # Print item index on its own line to make it easy to spot in logs
            print(f"\n--- Item {i} ---")

            # Check item type
            if not isinstance(item, dict):
                print(f"  WARNING: Item is not a dictionary. Type: {type(item)}")
                print(f"  Item content: {str(item)[:500]}")
                continue

            source = item.get('source', 'N/A')
            text = item.get('text', None)
            image_path = item.get('image_path', None)

            print(f"  Source: {source}")

            # Analyze text field
            if text is not None:
                text_type = type(text)
                if isinstance(text, str):
                    text_size = len(text.encode('utf-8'))
                    print("  Text Type: str")
                    print(f"  Text Size: {text_size} bytes")
                    if text_size > 1_000_000: # 1MB threshold
                         print("  WARNING: Very large text field detected (>1MB).")
                else:
                    print(f"  WARNING: Text field is NOT a string. Type: {text_type}")
                    try:
                        print(f"  Data representation: {str(text)[:200]}")
                    except Exception as e:
                        print(f"  Could not get representation of text field: {e}")
            else:
                print("  Text: None")

            # Analyze image_path field
            if image_path is not None:
                image_path_type = type(image_path)
                if isinstance(image_path, str):
                    print("  Image Path Type: str")
                else:
                    print(f"  WARNING: Image path is NOT a string. Type: {image_path_type}")
            else:
                print("  Image Path: None")


    except Exception as e:
        print(f"\n\nAn error occurred during analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    file_path = sys.argv[1] if len(sys.argv) > 1 else 'F:/impressioncore-b1-uks-output/first_batch_for_inspection.pkl'
    analyze_batch_extended(file_path)
