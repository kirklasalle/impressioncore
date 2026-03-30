#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #manage_f_models.py #python #source_code
**Category:** Source Code
**Status:** Active
"""



import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

try:
    from core.models.management.f_models_manager import main

    if __name__ == "__main__":
        main()

except ImportError as e:
    print(f"❌ Could not import F:/models manager: {e}")
    print("📍 Make sure you're running this from the project root directory")
    print("📍 Ensure src/core/models/management/ exists with the management system")
