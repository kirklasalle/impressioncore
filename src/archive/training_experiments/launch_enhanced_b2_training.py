#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #memory_management #python #source_code #src/training/launch_enhanced_b2_training.py #training
**Category:** Training System
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** October 15, 2024
# Updated:** August 4, 2025
# Author:** ImpressionCore Team
# Tags:** #memory_management #python #source_code #src\\training\\launch_enhanced_b2_training.py #training
# Category:** Training System
# Status:** Active

"""
Enhanced B2 Training Launcher with Distillation Capture
Restart training with comprehensive teacher-student preparation
"""

import subprocess
import sys
import time
import os
from datetime import datetime

def stop_existing_training():
    """Stop any existing training processes"""
    print("🛑 Checking for existing training processes...")

    try:
        # Get python processes
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'],
                              capture_output=True, text=True, shell=True)

        if 'python.exe' in result.stdout:
            print("⚠️  Found existing Python processes:")
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if 'python.exe' in line and 'Console' in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        pid = parts[1]
                        memory = parts[4] if len(parts) > 4 else 'unknown'
                        print(f"   PID {pid}: {memory}")

            print("\n💡 If any of these are training processes, consider stopping them")
            print("   Use: taskkill /F /PID <PID_NUMBER>")

            response = input("\n🔄 Continue with enhanced training? (y/n): ").lower().strip()
            if response != 'y':
                print("⏹️  Training launch cancelled")
                return False

    except Exception as e:
        print(f"⚠️  Could not check processes: {e}")

    return True

def launch_enhanced_training():
    """Launch training with distillation capture enabled"""

    print("🚀 ImpressionCore B2 Enhanced Training Launcher")
    print("=" * 55)
    print(f"⏰ Launch Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    if not stop_existing_training():
        return

    print("🎯 Launching Enhanced B2 Training with Distillation Capture...")
    print()
    print("✅ Features Enabled:")
    print("   📊 Real-time teacher output capture")
    print("   💾 HDF5 efficient tensor storage")
    print("   🎯 Temperature-scaled soft targets")
    print("   📈 Training dynamics monitoring")
    print("   🔗 Phase 2 preparation pipeline")
    print()

    # Verify environment
    if not os.path.exists('.venv310/Scripts/activate'):
        print("❌ Virtual environment not found!")
        print("   Expected: .venv310/Scripts/activate")
        return

    # Verify enhanced script
    if not os.path.exists('setup_raw_data_training.py'):
        print("❌ Enhanced training script not found!")
        return

    # Check directories
    required_dirs = [
        'src/training/phase1_outputs',
        'src/training/phase2_prep',
        'src/training/distillation'
    ]

    missing_dirs = [d for d in required_dirs if not os.path.exists(d)]
    if missing_dirs:
        print(f"❌ Missing directories: {missing_dirs}")
        print("   Run the directory creation script first")
        return

    print("✅ All prerequisites satisfied")
    print()
    print("🎯 Starting Enhanced B2 Training...")
    print("   - Press Ctrl+C to stop training")
    print("   - Monitor progress with: python monitor_b2_distillation_training.py")
    print("   - Check logs in: logs/ and src/training/phase1_outputs/metadata/")
    print()

    try:
        # Launch training
        cmd = [
            'cmd', '/c',
            '.venv310\\Scripts\\activate | python setup_raw_data_training.py'
        ]

        print("▶️  Executing: python setup_raw_data_training.py")
        print("   (with distillation capture enabled)")
        print()

        subprocess.run(cmd, cwd=os.getcwd())

    except KeyboardInterrupt:
        print("\n⏹️  Training stopped by user")
    except Exception as e:
        print(f"\n❌ Training error: {e}")

    print(f"\n🔄 Training session ended at {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    launch_enhanced_training()
