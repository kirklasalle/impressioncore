"""
Path B Relevance Fix - Complete Pipeline

Runs both steps:
1. Reformat dataset from Context/Response to Question/Answer
2. Fine-tune model with relevance-aware training

This fixes the issue where model generates grammatically correct but
irrelevant responses.

Created: October 7, 2025
Expected: 2-3 hours for reformatting + 8-10 hours for fine-tuning
"""

import subprocess
import sys
from pathlib import Path


def run_step(script_name: str, description: str) -> bool:
    """Run a Python script and report results."""
    print("\n" + "=" * 70)
    print(f"🚀 STEP: {description}")
    print("=" * 70)
    print()

    try:
        result = subprocess.run(
            [sys.executable, script_name],
            check=True,
            capture_output=False,
            text=True
        )
        print("\n✅ Step completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Step failed with error code {e.returncode}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False


def main():
    """Run complete relevance fix pipeline"""

    print("=" * 70)
    print("PATH B RELEVANCE FIX - COMPLETE PIPELINE")
    print("=" * 70)
    print()
    print("This will:")
    print("1. Reformat dataset to Q&A format (~5 minutes)")
    print("2. Fine-tune model with relevance training (~8-10 hours)")
    print()
    print("Expected improvement:")
    print("  - Relevance: 2.0/10.0 → 8.0/10.0 (target)")
    print("  - Grammar: 9.25/10.0 → 9.0/10.0 (slight trade-off acceptable)")
    print("  - Combined: 5.6/10.0 → 8.4/10.0 (major improvement)")
    print()

    input("Press Enter to begin, or Ctrl+C to cancel...")
    print()

    # Step 1: Reformat dataset
    step1_success = run_step(
        "fix_path_b_reformat_dataset.py",
        "Reformat Dataset to Q&A Format"
    )

    if not step1_success:
        print("\n❌ Pipeline failed at Step 1 (Dataset Reformatting)")
        print("Please check error messages above and try again.")
        return

    # Step 2: Fine-tune model
    step2_success = run_step(
        "fix_path_b_relevance_finetune.py",
        "Fine-tune Model with Relevance Training"
    )

    if not step2_success:
        print("\n❌ Pipeline failed at Step 2 (Fine-tuning)")
        print("Please check error messages above.")
        print("Dataset reformatting (Step 1) was successful.")
        return

    # Success!
    print("\n" + "=" * 70)
    print("🎉 RELEVANCE FIX COMPLETE!")
    print("=" * 70)
    print()
    print("Next steps:")
    print("1. Test the improved model:")
    print("   python conversation_interface.py")
    print()
    print("2. Check the saved checkpoint:")
    print("   F:/models/checkpoints/b3/hybrid/relevance_fixed_epoch*_r*.pth")
    print()
    print("3. Deploy if relevance is acceptable (>7.0/10.0):")
    print("   python deploy_best_model.py")
    print()
    print("Expected results:")
    print("  ✅ Responses now answer the actual questions")
    print("  ✅ Maintained natural language quality")
    print("  ✅ Ready for production deployment")
    print("=" * 70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Pipeline cancelled by user")
        sys.exit(1)
