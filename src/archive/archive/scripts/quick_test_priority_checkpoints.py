"""
Quick Priority Checkpoint Test
Tests the 4 most important checkpoints: Baseline, Phase1-End, Phase2-End, Final
Estimated time: 8-12 minutes (2-3 min per checkpoint)
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime

def main():
    print("\n" + "="*80)
    print("🚀 QUICK PRIORITY CHECKPOINT TEST")
    print("="*80)
    print("\nThis will test 4 critical checkpoints:")
    print("  1. Baseline (b3_massive_final.pth) - Pre-training quality")
    print("  2. Phase 1 Complete (alignment_epoch10.pth) - Embedding alignment")
    print("  3. Phase 2 Complete (generation_epoch20.pth) - Generation training")
    print("  4. Final Model (b3_embedding_integrated_final.pth) - All 55 epochs")
    print("\n⏱️  Estimated Time: 8-12 minutes")
    print("📊 Each checkpoint: 8 conversation queries")
    print("="*80)

    response = input("\n▶️  Start priority testing? (y/n): ")
    if response.lower() != 'y':
        print("❌ Testing cancelled.")
        return 0

    print("\n🏁 Starting priority checkpoint testing...")
    print(f"⏰ Start Time: {datetime.now().strftime('%H:%M:%S')}\n")

    # Run the test
    try:
        result = subprocess.run(
            [sys.executable, "test_all_checkpoints.py", "--priority-only"],
            cwd=Path(__file__).parent,
            check=True
        )

        print(f"\n⏰ End Time: {datetime.now().strftime('%H:%M:%S')}")
        print("\n✅ Priority testing complete!")
        print("📄 Results saved to: docs/analysis/checkpoint_progression_results.md")

        return result.returncode

    except subprocess.CalledProcessError as e:
        print(f"\n❌ Testing failed with error code: {e.returncode}")
        return e.returncode
    except KeyboardInterrupt:
        print("\n⚠️  Testing interrupted by user.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
