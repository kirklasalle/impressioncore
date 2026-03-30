#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #multimodal #python #source_code #src/training/execute_training_pipeline.py #training
**Category:** Training System
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** October 15, 2024
# Updated:** August 4, 2025
# Author:** ImpressionCore Team
# Tags:** #multimodal #python #source_code #src\\training\\execute_training_pipeline.py #training
# Category:** Training System
# Status:** Active

"""
ImpressionCore B2 Training Pipeline Executor
Execute optimized enhanced training + raw data training preparation

Usage:
    python execute_training_pipeline.py --phase enhanced    # Run enhanced cycle 2
    python execute_training_pipeline.py --phase raw         # Setup raw training
    python execute_training_pipeline.py --phase both        # Run both phases
"""

import argparse
import sys
import time
import os
from pathlib import Path

def run_enhanced_training():
    """Execute enhanced training cycle 2"""
    print("🚀 Starting Enhanced Training Cycle 2...")
    print("=" * 60)

    try:
        # Import and run enhanced training
        from train_b2_enhanced_optimized import main as enhanced_main

        print("⚡ Quick optimization cycle with:")
        print("  • Reduced learning rates for fine-tuning")
        print("  • Optimized loss weights (intent=2.5)")
        print("  • Enhanced monitoring with early stopping")
        print("  • Target: Sentiment 40-45%, Intent 15-20%")
        print()

        start_time = time.time()
        final_metrics = enhanced_main()
        end_time = time.time()

        print(f"\n🎉 Enhanced Training Cycle 2 Complete!")
        print(f"⏱️ Total time: {(end_time - start_time)/60:.1f} minutes")
        print(f"📈 Final Results:")
        print(f"   Sentiment: {final_metrics['sentiment_acc']:.1%}")
        print(f"   Intent: {final_metrics['intent_acc']:.1%}")

        return True

    except Exception as e:
        print(f"❌ Enhanced training failed: {e}")
        return False

def setup_raw_training():
    """Setup raw data training"""
    print("🗃️ Setting up Raw Data Training...")
    print("=" * 60)

    try:
        # Import and setup raw training
        from setup_raw_data_training import main as raw_main

        print("🔧 Preparing comprehensive raw data pipeline:")
        print("  • Multimodal dataset loading (text + image + audio)")
        print("  • End-to-end encoder training")
        print("  • Production-ready architecture")
        print("  • Target: 70-85% sentiment, 60-75% intent accuracy")
        print()

        trainer = raw_main()

        print(f"\n✅ Raw Data Training Setup Complete!")
        print(f"📂 Ready to train on real multimodal conversations")
        print(f"🎯 Estimated training time: 6-12 hours")

        # Ask if user wants to start training immediately
        start_now = input("\n🚀 Start raw data training now? (y/N): ").lower().strip()
        if start_now == 'y':
            print("\n🚀 Starting raw data training...")
            trainer.start_raw_training()
        else:
            print("\n📝 Raw training prepared. Run trainer.start_raw_training() when ready.")

        return True

    except Exception as e:
        print(f"❌ Raw training setup failed: {e}")
        return False

def run_both_phases():
    """Run enhanced training then setup raw training"""
    print("🎯 ImpressionCore B2 Complete Training Pipeline")
    print("=" * 60)
    print("Phase 1: Enhanced Training Cycle 2 (quick optimization)")
    print("Phase 2: Raw Data Training Setup (production pipeline)")
    print()

    # Phase 1: Enhanced training
    enhanced_success = run_enhanced_training()

    if enhanced_success:
        print("\n" + "="*60)
        print("✅ Enhanced training complete! Proceeding to raw data setup...")
        print("="*60)
        time.sleep(2)

        # Phase 2: Raw data setup
        raw_success = setup_raw_training()

        if raw_success:
            print("\n" + "🎉" * 20)
            print("🎊 COMPLETE TRAINING PIPELINE READY! 🎊")
            print("🎉" * 20)
            print("\n📊 Summary:")
            print("  ✅ Enhanced architecture optimized and validated")
            print("  ✅ Raw data training pipeline prepared")
            print("  ✅ Ready for production-level multimodal training")
            print("\n🚀 Next step: Execute raw data training for 70-85% accuracy!")
        else:
            print("\n⚠️ Raw training setup had issues, but enhanced training succeeded")
    else:
        print("\n❌ Enhanced training failed. Check logs for details.")

def main():
    parser = argparse.ArgumentParser(description="ImpressionCore B2 Training Pipeline")
    parser.add_argument(
        '--phase',
        choices=['enhanced', 'raw', 'both'],
        default='both',
        help='Training phase to execute (default: both)'
    )

    args = parser.parse_args()

    # Check prerequisites
    if not os.path.exists('best_b2_enhanced_model.pth'):
        print("⚠️ Warning: No previous enhanced model found.")
        print("   The enhanced training will start from scratch.")
        print()

    # Activate virtual environment check
    if not sys.prefix != sys.base_prefix:
        print("⚠️ Warning: Virtual environment not activated.")
        print("   Please run: source .venv310/Scripts/activate")
        print()

    # Execute requested phase
    if args.phase == 'enhanced':
        run_enhanced_training()
    elif args.phase == 'raw':
        setup_raw_training()
    elif args.phase == 'both':
        run_both_phases()

if __name__ == "__main__":
    main()
