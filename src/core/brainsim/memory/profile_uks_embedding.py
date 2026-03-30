#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #memory_management #python #source_code #src/brainsim/memory/profile_uks_embedding.py
**Category:** Source Code
**Status:** Active
"""









# Profile Uks Embedding

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:00
# Author:** ImpressionCore Team
# Tags:** #memory_management #python #source_code #src\\brainsim\\memory\\profile_uks_embedding.py
# Category:** Source Code
# Status:** Active

"""
Performance profiling script for UKS embedding pipeline (ImpressionCore-b1).
- Uses memory_profiler and time to log batch processing times and memory usage.
"""
import pickle
import time

from memory_profiler import memory_usage

UKS_PATH = "F:/impressioncore-b1-uks-output/uks_db.pkl"


def profile_uks_loading():
    def load():
        with open(UKS_PATH, "rb") as f:
            return pickle.load(f)
    mem_usage = memory_usage((load,))
    print(f"Max memory usage during UKS load: {max(mem_usage):.2f} MiB")


def main():
    start = time.time()
    profile_uks_loading()
    elapsed = time.time() - start
    print(f"Total UKS load time: {elapsed:.2f} seconds")

if __name__ == "__main__":
    main()
