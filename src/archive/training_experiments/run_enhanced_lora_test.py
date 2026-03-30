#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #python #source_code #src/training/run_enhanced_lora_test.py #testing #training
**Category:** Training System
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** October 15, 2024
# Updated:** August 4, 2025
# Author:** ImpressionCore Team
# Tags:** #python #source_code #src\\training\\run_enhanced_lora_test.py #testing #training
# Category:** Training System
# Status:** Active

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
    from training.models.lora.test_enhanced_lora import main
    print("Successfully imported the enhanced test module")
    main()
except Exception as e:
    print(f"Error occurred: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
