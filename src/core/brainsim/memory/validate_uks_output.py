#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #memory_management #python #source_code #src/brainsim/memory/validate_uks_output.py
**Category:** Source Code
**Status:** Active
"""









# Validate Uks Output

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:00
# Author:** ImpressionCore Team
# Tags:** #memory_management #python #source_code #src\\brainsim\\memory\\validate_uks_output.py
# Category:** Source Code
# Status:** Active

"""
Validation and sampling script for UKS output (ImpressionCore-b1).
- Checks key diversity, embedding completeness, and absence of duplicates.
- Prints a sample of entries for manual inspection.
- Checks for missing modalities (text, image).
"""
import pickle
import random

UKS_PATH = "F:/impressioncore-b1-uks-output/uks_db.pkl"
SAMPLE_SIZE = 10

def main():
    with open(UKS_PATH, "rb") as f:
        uks_db = pickle.load(f)
    print(f"Loaded UKS DB with {len(uks_db)} unique entries.")
    # Check for duplicate keys
    if len(uks_db) != len(set(uks_db.keys())):
        print("[ERROR] Duplicate keys found!")
    # Check embedding completeness and modalities
    missing_text = 0
    missing_image = 0
    for v in uks_db.values():
        if not v.get("text_ids"):
            missing_text += 1
        if not v.get("image_features"):
            missing_image += 1
    print(f"Entries missing text_ids: {missing_text}")
    print(f"Entries missing image_features: {missing_image}")
    # Print sample entries
    print("\nSample entries:")
    keys = list(uks_db.keys())
    for k in random.sample(keys, min(SAMPLE_SIZE, len(keys))):
        print(f"Key: {k}\n  Embedding: {uks_db[k]}\n")

if __name__ == "__main__":
    main()
