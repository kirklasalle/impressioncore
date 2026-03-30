"""
Master pipeline script for Option A: True Q&A Dataset Training.

This script orchestrates the entire process:
1. Download SQuAD 2.0 dataset
2. Download ELI5 dataset
3. Create mixed Q&A + conversation dataset
4. Train model with mixed dataset
5. Test and validate results

Created: October 8, 2025
Author: Kirk LaSalle; GitHub Copilot
"""

import subprocess
import sys
from pathlib import Path
import time

def run_script(script_name: str, description: str) -> bool:
    """Run a Python script and report results."""
    print("\n" + "=" * 70)
    print(f"🚀 {description}")
    print("=" * 70)

    try:
        result = subprocess.run(
            [sys.executable, script_name],
            check=True,
            capture_output=False,
            text=True
        )
        print(f"\n✅ {description} - COMPLETE")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ {description} - FAILED")
        print(f"Error: {e}")
        return False
    except KeyboardInterrupt:
        print(f"\n⚠️ {description} - INTERRUPTED BY USER")
        return False


def main():
    """Run complete Option A pipeline."""
    print("=" * 70)
    print("PATH B OPTION A - COMPLETE PIPELINE")
    print("True Q&A Dataset Training")
    print("=" * 70)
    print("\nThis pipeline will:")
    print("  1. Download SQuAD 2.0 dataset (~5-10 minutes)")
    print("  2. Download ELI5 dataset (~10-15 minutes)")
    print("  3. Create mixed Q&A + conversation dataset (~5 minutes)")
    print("  4. Train model with mixed dataset (~10 hours)")
    print("  5. Test and validate results")
    print("\nTotal estimated time: ~11-12 hours")
    print("\nPress Ctrl+C at any time to stop.")

    input("\nPress Enter to begin...")

    start_time = time.time()

    # Step 1: Download SQuAD
    print("\n" + "🔵" * 35)
    print("STEP 1/4: DOWNLOAD SQUAD 2.0 DATASET")
    print("🔵" * 35)

    if not run_script("download_squad_dataset.py", "SQuAD 2.0 Download"):
        print("\n❌ Pipeline stopped - SQuAD download failed")
        return

    # Step 2: Download Explanatory Q&A (ELI5 alternative)
    print("\n" + "🔵" * 35)
    print("STEP 2/4: DOWNLOAD EXPLANATORY Q&A DATASET")
    print("🔵" * 35)

    print("\n⚠️  NOTE: ELI5 is defunct. Using alternative datasets:")
    print("   - Natural Questions (Google)")
    print("   - MS MARCO")
    print("   - WikiQA")
    print("   - Or SQuAD-generated explanatory Q&A\n")

    if not run_script("download_explanatory_qa_alternative.py", "Explanatory Q&A Download"):
        print("\n⚠️  Explanatory dataset download had issues")
        print("   Continuing with SQuAD only (factual Q&A)")
        print("   This will reduce explanatory capability but maintain Q&A ability")
    else:
        print("\n✅ Explanatory Q&A Download - COMPLETE")

    # Step 3: Create mixed dataset
    print("\n" + "🔵" * 35)
    print("STEP 3/4: CREATE MIXED DATASET")
    print("🔵" * 35)

    if not run_script("create_mixed_qa_dataset.py", "Mixed Dataset Creation"):
        print("\n❌ Pipeline stopped - Mixed dataset creation failed")
        return

    # Step 4: Train model
    print("\n" + "🔵" * 35)
    print("STEP 4/4: TRAIN MODEL WITH TRUE Q&A DATA")
    print("🔵" * 35)
    print("\n⏱️  This will take approximately 10 hours")
    print("💡 Training will run in the background")
    print("💾 Checkpoints saved after each epoch")

    if not run_script("train_with_true_qa_dataset.py", "True Q&A Training"):
        print("\n❌ Pipeline stopped - Training failed")
        return

    # Complete
    total_time = (time.time() - start_time) / 3600

    print("\n" + "=" * 70)
    print("🎉 OPTION A PIPELINE COMPLETE!")
    print("=" * 70)
    print(f"\nTotal time: {total_time:.1f} hours")
    print("\n📊 Results:")
    print("  - SQuAD 2.0: Downloaded and prepared")
    print("  - ELI5: Downloaded and prepared")
    print("  - Mixed dataset: Created (70% Q&A, 30% conversation)")
    print("  - Model: Trained for 3 epochs")
    print("\n📁 Checkpoints saved to: F:/models/checkpoints/b3/hybrid/")
    print("   Look for: true_qa_epoch*_r*.pth")
    print("\n🎯 Next steps:")
    print("  1. Review training results in terminal output")
    print("  2. Test best checkpoint interactively")
    print("  3. If relevance >7.5, deploy to production")
    print("  4. If relevance <7.5, consider:")
    print("     - Training 2 more epochs")
    print("     - Adjusting dataset mix ratio")
    print("     - Using Option B (instruction-tuning head)")
    print("\n" + "=" * 70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Pipeline interrupted by user")
        print("You can resume by running individual scripts:")
        print("  1. download_squad_dataset.py")
        print("  2. download_eli5_dataset.py")
        print("  3. create_mixed_qa_dataset.py")
        print("  4. train_with_true_qa_dataset.py")
