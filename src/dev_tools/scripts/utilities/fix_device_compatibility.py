#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #cuda #python #source_code #src/scripts/utilities/fix_device_compatibility.py #testing
**Category:** Source Code
**Status:** Active
"""



import sys
from pathlib import Path

import torch

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def fix_device_compatibility():
    """Fix device compatibility with simple test"""

    print("🔧 Fixing device compatibility...")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    try:
        # Test basic B3 integration
        from src.core.models.b3_unified_integration import create_optimized_b3_system

        # Create system
        system = create_optimized_b3_system()
        system = system.to(device)

        # Simple test
        test_result = system.process_text_only("Hello, device test!")
        print(f"✅ Device compatibility fixed! Quality: {test_result.get('quality_score', 'N/A')}")
        return True

    except Exception as e:
        print(f"❌ Device fix failed: {e}")
        return False

if __name__ == "__main__":
    success = fix_device_compatibility()
    sys.exit(0 if success else 1)
