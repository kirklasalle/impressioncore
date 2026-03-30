#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #python #source_code #src/core/utils/check_package_size.py #training
**Category:** Core Implementation
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:00
# Author:** ImpressionCore Team
# Tags:** #python #source_code #src\\core\\utils\\check_package_size.py #training
# Category:** Core Implementation
# Status:** Active

"""Quick size checker for the certified data package"""

from pathlib import Path


def check_package_size():
    certified_dir = Path("src/training/datasets/certified")

    print("📦 IMPRESSIONCORE CERTIFIED ACADEMIC DATA PACKAGE SIZES")
    print("=" * 60)

    # Check ZIP file
    zip_files = list(certified_dir.glob("*.zip"))
    if zip_files:
        zip_file = zip_files[0]
        size_bytes = zip_file.stat().st_size
        size_kb = size_bytes / 1024
        size_mb = size_bytes / (1024 * 1024)

        print(f"ZIP Package: {zip_file.name}")
        print(f"  Size: {size_bytes:,} bytes")
        print(f"  Size: {size_kb:.2f} KB")
        print(f"  Size: {size_mb:.3f} MB")

    # Check directory contents
    dirs = [d for d in certified_dir.iterdir() if d.is_dir()]
    if dirs:
        dir_path = dirs[0]
        print(f"\n📁 Uncompressed Directory: {dir_path.name}")

        total_size = 0
        for file_path in dir_path.rglob("*"):
            if file_path.is_file():
                file_size = file_path.stat().st_size
                total_size += file_size
                print(f"  {file_path.name}: {file_size:,} bytes ({file_size/1024:.1f} KB)")

        total_mb = total_size / (1024 * 1024)
        print(f"\nTotal uncompressed: {total_size:,} bytes ({total_mb:.3f} MB)")

if __name__ == "__main__":
    check_package_size()
