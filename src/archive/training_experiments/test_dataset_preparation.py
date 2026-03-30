#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #python #source_code #src/training/test_dataset_preparation.py #testing #training
**Category:** Training System
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** October 15, 2024
# Updated:** August 4, 2025
# Author:** ImpressionCore Team
# Tags:** #python #source_code #src\\training\\test_dataset_preparation.py #testing #training
# Category:** Training System
# Status:** Active

"""
B1 Dataset Preparation Test Runner

Quick test runner for the B1 Dataset Preparation Pipeline.
Tests the analysis and planning phases of dataset enhancement.

File: training/test_dataset_preparation.py
Created: 2025-06-28
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent.parent
sys.path.insert(0, str(src_path))

def test_dataset_preparation():
    """Test the B1 Dataset Preparation Pipeline"""
    try:
        from training.b1_dataset_preparation_pipeline import B1DatasetPreparationPipeline

        print("🤖 Testing B1 Dataset Preparation Pipeline...")
        print("=" * 60)

        # Initialize pipeline
        pipeline = B1DatasetPreparationPipeline()

        # Test dataset analysis
        print("\n📊 Phase 1: Dataset Analysis")
        quality_metrics = pipeline.analyze_current_dataset()

        # Test enhancement planning
        print("\n📋 Phase 2: Enhancement Planning")
        enhancement_plan = pipeline.create_enhancement_plan()

        # Display status report
        print("\n📈 Phase 3: Status Report")
        status = pipeline.get_status_report()

        # Print key results
        print(f"\n✅ SUCCESS: Pipeline test completed!")
        print(f"📊 Analyzed {quality_metrics.total_files:,} files ({quality_metrics.total_size_mb:.1f} MB)")
        print(f"🎯 Quality Score: {quality_metrics.quality_score:.2f}/1.0")
        print(f"🚀 Planned Improvement: +{enhancement_plan.estimated_improvement:.2f} quality points")
        print(f"⏱️ Test Duration: {status['elapsed_time_seconds']:.1f} seconds")
        print(f"🛡️ Sacred Covenant: {'ACTIVE' if status['sacred_covenant_active'] else 'INACTIVE'}")

        return True

    except Exception as e:
        print(f"❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_dataset_preparation()
    sys.exit(0 if success else 1)
