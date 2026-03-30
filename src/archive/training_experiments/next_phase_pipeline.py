#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #documentation #python #source_code #src/training/next_phase_pipeline.py #testing #training
**Category:** Training System
**Status:** Active
"""









# Next Phase Pipeline

# Created:** October 15, 2024
# Updated:** August 4, 2025
# Author:** ImpressionCore Team
# Tags:** #documentation #python #source_code #src\\training\\next_phase_pipeline.py #testing #training
# Category:** Training System
# Status:** Active

"""
B2 Next-Phase Automation Pipeline

Automates:
 - Documentation update checklist
 - Loader test sanity check
 - Dependency check
 - (Optional) dataset embedding
 - Training launch checklist

Author: GitHub Copilot
Date: 2025-06-29
"""
import subprocess
import sys
from pathlib import Path

DOCS_PATH = Path('docs/data_prep_notes.md')
CATALOGUE_PATH = Path('F:/b2_datasets/b2_data_catalogue.json')
LOADER_TEST = Path('src/training/datasets/test_data_loader.py')
TRAIN_SCRIPT = Path('src/training/train_b2.py')

def check_dependencies():
    """Check for required Python packages."""
    print("[1/5] Checking dependencies...")
    missing = []
    for pkg in ["soundfile", "PIL", "torch", "numpy", "rich"]:
        try:
            __import__(pkg if pkg != "PIL" else "PIL.Image")
        except ImportError:
            missing.append(pkg)
    if missing:
        print(f"Missing packages: {', '.join(missing)}. Please install before proceeding.")
        return False
    print("All dependencies present.")
    return True

def update_documentation():
    """Remind user to update docs/data_prep_notes.md with schema, counts, and notes."""
    print("[2/5] Documentation checklist:")
    print(f"- [ ] Review and update {DOCS_PATH} with final schema, labeling, preprocessing, and file counts.")
    print(f"- [ ] Add any special notes about curated data.")
    print(f"- [ ] Optionally summarize file counts from {CATALOGUE_PATH}.")

def run_loader_test():
    """Run the loader test script to verify data loads without errors."""
    print("[3/5] Running loader test script...")
    if not LOADER_TEST.exists():
        print(f"Loader test script not found: {LOADER_TEST}")
        return False
    result = subprocess.run([sys.executable, str(LOADER_TEST)], capture_output=True, text=True)
    print(result.stdout)
    if result.returncode == 0:
        print("Loader test passed.")
        return True
    else:
        print("Loader test failed. See output above.")
        return False

def embed_dataset():
    """(Optional) Placeholder for dataset embedding step before training."""
    print("[4/5] (Optional) Dataset embedding step not implemented. If required, run your embedding pipeline here.")

def launch_training():
    """Remind user to launch training and monitor logs/metrics."""
    print("[5/5] Training launch checklist:")
    print(f"- [ ] Set hyperparameters in {TRAIN_SCRIPT} (e.g., 3B params, 128k context)")
    print(f"- [ ] Confirm all dependencies are installed.")
    print(f"- [ ] Start training: python {TRAIN_SCRIPT}")
    print(f"- [ ] Monitor logs, metrics, and system resource usage.")
    print(f"- [ ] Review training/validation metrics and iterate as needed.")

def main():
    print("\n=== B2 Next-Phase Automation Pipeline ===\n")
    if not check_dependencies():
        return
    update_documentation()
    run_loader_test()
    embed_dataset()
    launch_training()
    print("\nPipeline complete. Review checklist above before proceeding.\n")

if __name__ == "__main__":
    main()
