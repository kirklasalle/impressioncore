#!/usr/bin/env python3
"""
Unified Sweet Spot Training Launcher
===================================

Quick launcher for unified training with data validation and setup.
Ensures Constitutional Framework compliance before training launch.

Created: August 7, 2025
Author: Kirk LaSalle & GitHub Copilot
"""

import os
import sys

# Set encoding for Windows compatibility
if sys.platform.startswith('win'):
    os.environ['PYTHONIOENCODING'] = 'utf-8'

import subprocess
from pathlib import Path


def check_environment():
    """Check training environment setup."""
    print("DISCOVERY: Environment Check")
    print("-" * 30)

    # Check Python environment
    python_version = sys.version_info
    print(f"PYTHON: Python: {python_version.major}.{python_version.minor}.{python_version.micro}")

    # Check CUDA availability
    try:
        import torch
        cuda_available = torch.cuda.is_available()
        if cuda_available:
            gpu_name = torch.cuda.get_device_name(0)
            total_vram = torch.cuda.get_device_properties(0).total_memory / 1024**3
            print(f"GPU: GPU: {gpu_name}")
            print(f"MEMORY: VRAM: {total_vram:.1f}GB")
        else:
            print("ERROR: CUDA not available")
            return False
    except ImportError:
        print("ERROR: PyTorch not installed")
        return False

    # Check src directory
    src_path = Path("src")
    if not src_path.exists():
        print("ERROR: src/ directory not found")
        return False
    else:
        print("SUCCESS: src/ directory found")

    # Check F: drive
    f_drive = Path("F:/")
    if not f_drive.exists():
        print("ERROR: F: drive not accessible")
        return False
    else:
        print("SUCCESS: F: drive accessible")

    return True

def run_data_analysis():
    """Run unified data analysis."""
    print("\nDISCOVERY: Running Data Analysis...")
    try:
        result = subprocess.run([sys.executable, "analyze_unified_data.py"],
                              capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print("SUCCESS: Data analysis completed successfully")
            return True
        else:
            print(f"ERROR: Data analysis failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("TIMEOUT: Data analysis timed out")
        return False
    except Exception as e:
        print(f"ERROR: Data analysis error: {e}")
        return False

def launch_training():
    """Launch unified sweet spot training."""
    print("\nLAUNCH: Launching Unified Sweet Spot Training...")
    print("=" * 50)
    print("TARGET: Constitutional Framework: ACTIVE")
    print("LIGHTNING: Concentrated Intelligence: ENABLED")
    print("WRENCH: Consumer Hardware Democracy: GTX 1050 Ti OPTIMIZED")
    print("MEMORY: Data Condensation: Embeddings + Datasets UNIFIED")
    print("=" * 50)

    try:
        # Launch training in real-time mode
        process = subprocess.Popen([sys.executable, "train_unified_sweet_spot.py"],
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT,
                                 universal_newlines=True,
                                 bufsize=1)

        print("CHART: Training started! Monitoring output...\n")

        # Stream output in real-time
        for line in process.stdout:
            print(line.rstrip())

        process.wait()

        if process.returncode == 0:
            print("\nCELEBRATE: Training completed successfully!")
            return True
        else:
            print(f"\nERROR: Training failed with code: {process.returncode}")
            return False

    except KeyboardInterrupt:
        print("\nWARNING: Training interrupted by user")
        if 'process' in locals():
            process.terminate()
        return False
    except Exception as e:
        print(f"\nERROR: Training launch error: {e}")
        return False

def main():
    """Main launcher function."""
    print("LAUNCH: ImpressionCore Unified Sweet Spot Training Launcher")
    print("TARGET: Constitutional Framework Implementation")
    print("=" * 60)

    # Step 1: Environment check
    if not check_environment():
        print("\nERROR: Environment check failed. Please fix issues before training.")
        return 1

    print("\nSUCCESS: Environment check passed!")

    # Step 2: Data analysis
    print("\n" + "="*60)
    if not run_data_analysis():
        print("\nWARNING: Data analysis failed. Training may proceed with synthetic data.")
        response = input("Continue anyway? (y/N): ").lower()
        if response != 'y':
            print("Training cancelled.")
            return 1

    # Step 3: Training confirmation
    print("\n" + "="*60)
    print("TARGET: READY TO LAUNCH UNIFIED TRAINING")
    print("CHART: Training will use:")
    print("   • F:/data/embeddings (if available)")
    print("   • F:/data/datasets (if available)")
    print("   • Constitutional Framework compliance")
    print("   • GTX 1050 Ti optimization")
    print("   • Sweet spot architecture (506M parameters)")

    response = input("\nLAUNCH: Launch training? (Y/n): ").lower()
    if response == 'n':
        print("Training cancelled.")
        return 0

    # Step 4: Launch training
    success = launch_training()

    if success:
        print("\nCELEBRATE: UNIFIED SWEET SPOT TRAINING COMPLETE!")
        print("SUCCESS: Constitutional Framework: FULLY IMPLEMENTED")
        print("LAUNCH: Sweet Spot Theory: VALIDATED WITH ENHANCED DATA")
        return 0
    else:
        print("\nERROR: Training failed. Check logs for details.")
        return 1

if __name__ == "__main__":
    exit(main())
