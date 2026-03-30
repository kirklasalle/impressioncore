#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #memory_management #python #source_code #src/brainsim/memory/uks_consistency_check.py
**Category:** Source Code
**Status:** Active
"""









# Uks Consistency Check

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:00
# Author:** ImpressionCore Team
# Tags:** #memory_management #python #source_code #src\\brainsim\\memory\\uks_consistency_check.py
# Category:** Source Code
# Status:** Active

"""
Automated consistency check for UKS (ImpressionCore-b1).
- Verifies all expected data sources are represented in the UKS.
- Checks for missing modalities and prints summary.
"""
import pickle

UKS_PATH = "F:/impressioncore-b1-uks-output/uks_db.pkl"
EXPECTED_SOURCES = [
    "F:/datasets/",
    "F:/impressioncore-b1-processed-transcripts/"
]

def main():
    with open(UKS_PATH, "rb") as f:
        uks_db = pickle.load(f)
    sources = set()
    missing_text = 0
    missing_image = 0
    for v in uks_db.values():
        meta = v.get("metadata", {})
        src = meta.get("source", "")
        sources.add(src)
        if not v.get("text_ids"):
            missing_text += 1
        if not v.get("image_features"):
            missing_image += 1
    print(f"Total unique sources: {len(sources)}")
    for expected in EXPECTED_SOURCES:
        found = any(expected in s for s in sources)
        print(f"Source {expected}: {'FOUND' if found else 'MISSING'}")
    print(f"Entries missing text_ids: {missing_text}")
    print(f"Entries missing image_features: {missing_image}")

if __name__ == "__main__":
    main()
