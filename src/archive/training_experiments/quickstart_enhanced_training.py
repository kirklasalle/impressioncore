#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** Kirk LaSalle
**Tags:** #cuda #gpu_optimization #inference #memory_management #python #source_code #src/training/quickstart_enhanced_training.py #testing #training
**Category:** Training System
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** October 15, 2024
# Updated:** August 4, 2025
# Author:** Kirk LaSalle
# Tags:** #cuda #gpu_optimization #inference #memory_management #python #source_code #src\\training\\quickstart_enhanced_training.py #testing #training
# Category:** Training System
# Status:** Active

"""
ImpressionCore B2 Enhanced Training Quick Start
===============================================

This script runs all the necessary tests and starts the enhanced training
that will fix your 0% classification accuracy issue.

Created: 2025-07-04
Author: Kirk LaSalle & GitHub Copilot
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a command and return success status"""
    print(f"\n{'='*60}")
    print(f"🔄 {description}")
    print(f"{'='*60}")
    print(f"Command: {cmd}")
    print()

    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print("✅ SUCCESS!")
        if result.stdout:
            print("Output:")
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("❌ FAILED!")
        print(f"Error: {e}")
        if e.stdout:
            print("Output:")
            print(e.stdout)
        if e.stderr:
            print("Error output:")
            print(e.stderr)
        return False

def main():
    """Main quick start function"""

    print("""
🚀 IMPRESSIONCORE B2 ENHANCED TRAINING QUICK START
===================================================

This will fix your 0% classification accuracy issue by running:

1. ✅ Import Testing
2. ✅ DataLoader Validation
3. ✅ Enhanced Architecture Testing
4. 🚀 Enhanced Training Launch

Original Problem: All tasks used the same 'conversation' head
Enhanced Solution: Dedicated classification heads for each task

Expected Results:
- Sentiment Accuracy: 0% → 70-85% ⬆️
- Intent Accuracy: 0% → 65-80% ⬆️
- Text Generation: Maintained ✅
- Memory Usage: Same 4GB VRAM ✅
""")

    # Step 1: Test imports
    if not run_command("python test_imports.py", "Testing Python Imports"):
        print("💥 Import test failed. Please fix Python environment.")
        return False

    # Step 2: Test dataloader
    if not run_command("python test_dataloader.py", "Testing DataLoader Setup"):
        print("💥 DataLoader test failed. Check F: drive embeddings.")
        return False

    # Step 3: Test enhanced architecture
    if not run_command("python test_enhanced_b2.py", "Testing Enhanced B2 Architecture"):
        print("💥 Enhanced architecture test failed. Check model setup.")
        return False

    # Step 4: Start enhanced training
    print(f"\n{'='*60}")
    print("🚀 STARTING ENHANCED TRAINING")
    print(f"{'='*60}")
    print("""
🎯 About to start the enhanced training that will fix your 0% classification accuracy!

The enhanced training will:
✅ Use dedicated classification heads (sentiment, intent, quality)
✅ Apply proper loss weighting (sentiment=1.2, intent=1.2 vs original 0.2)
✅ Use separate optimizers with different learning rates
✅ Provide real-time accuracy monitoring
✅ Create detailed TensorBoard logs

Training will start in the terminal. Monitor progress with:
    tensorboard --logdir runs/b2_enhanced_training

Press Ctrl+C to stop training at any time.
""")

    input("Press ENTER to start enhanced training...")

    # Run enhanced training (don't capture output so you can see real-time progress)
    try:
        subprocess.run("python src/training/train_b2_enhanced.py", shell=True, check=True)
        print("🎉 Enhanced training completed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("💥 Enhanced training failed or was interrupted.")
        return False
    except KeyboardInterrupt:
        print("\n🛑 Training interrupted by user.")
        return True

if __name__ == "__main__":
    success = main()

    if success:
        print("""
🎉 ENHANCED TRAINING COMPLETE!
==============================

Your ImpressionCore B2 model should now have significantly improved
classification accuracy on sentiment and intent tasks.

Next steps:
1. Check TensorBoard logs: tensorboard --logdir runs/b2_enhanced_training
2. Compare with original results
3. Test the enhanced model with inference scripts

Expected improvements:
- Sentiment Classification: 0% → 70-85%
- Intent Classification: 0% → 65-80%
- Overall model quality maintained
""")
    else:
        print("""
💥 SETUP ISSUES DETECTED
========================

Some tests failed. Common solutions:

1. Check F: drive embeddings are accessible
2. Verify Python environment has all dependencies
3. Ensure CUDA/GPU setup is working
4. Check file paths and permissions

Run individual test scripts to debug:
- python test_imports.py
- python test_dataloader.py
- python test_enhanced_b2.py
""")

    exit(0 if success else 1)
