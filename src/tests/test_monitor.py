#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #gpu_optimization #python #source_code #src/tests/test_monitor.py #testing #training
**Category:** Testing Framework
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:02
# Author:** ImpressionCore Team
# Tags:** #gpu_optimization #python #source_code #src\\tests\\test_monitor.py #testing #training
# Category:** Testing Framework
# Status:** Active

"""Test script for VRGC Monitor"""

import os
import sys

# conftest.py already adds src to sys.path

try:
    from src.core.utils.vrgc_autonomous_monitor import VRGCAutonomousMonitor
    print("🤖 VRGC Monitor imported successfully")

    monitor = VRGCAutonomousMonitor()
    print("✅ Monitor instance created")

    # Test GPU status
    gpu_status = monitor.get_gpu_status()
    print(f"🎮 GPU Status: {gpu_status}")

    # Test training progress
    progress = monitor.calculate_training_progress()
    print(f"🎯 Training Progress: {progress}")

    # Test status display creation
    status_display = monitor.create_status_display()
    print(f"📊 Status Display: {type(status_display)}")

    print("✅ All basic tests passed!")
    print("🚀 Starting short monitoring test...")

    # Short test run
    monitor.monitoring_active = True
    monitor.run_continuous_monitoring(update_interval=5)  # 5 second intervals

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
