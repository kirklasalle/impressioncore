#!/usr/bin/env python3
"""
Simple Enhanced LoRA Test

Basic test for Enhanced LoRA functionality without complex UI elements.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path.cwd()))

# Import and run the enhanced test
try:
    from src.training.models.lora.test_enhanced_lora import main
    print("Successfully imported the enhanced test module")
    main()
except Exception as e:
    print(f"Error occurred: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
