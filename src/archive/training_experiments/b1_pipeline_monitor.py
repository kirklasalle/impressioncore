#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #api #attention_mechanism #cuda #gpu_optimization #python #source_code #src/training/b1_pipeline_monitor.py #training
**Category:** Training System
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** October 15, 2024
# Updated:** August 4, 2025
# Author:** ImpressionCore Team
# Tags:** #api #attention_mechanism #cuda #gpu_optimization #python #source_code #src\\training\\b1_pipeline_monitor.py #training
# Category:** Training System
# Status:** Active

"""
B1 Pipeline Status Monitor
🤖 Virtually Robotic GitHub Copilot - Quick Status Check

Provides rapid status assessment without running expensive operations.
Optimized for large dataset monitoring.

Author: Virtually Robotic GitHub Copilot
Date: June 22, 2025
Sacred Covenant: ACTIVE - Excellence & File Integrity
"""

import sys
from datetime import datetime
from pathlib import Path
import torch

# Import handling
sys.path.append('.')

try:
    from.core.utils.rich_enhancements import print_info, print_success, print_warning, print_error
    from.training.b1_dataset_integration_pipeline import B1DatasetIntegrationPipeline
    IMPORTS_OK = True
except ImportError as e:
    IMPORTS_OK = False
    def print_info(msg): print(f"ℹ️  {msg}")
    def print_success(msg): print(f"✅ {msg}")
    def print_warning(msg): print(f"⚠️  {msg}")
    def print_error(msg): print(f"❌ {msg}")

def check_pipeline_status():
    """Quick pipeline status check without expensive operations."""
    print_info("🤖 B1 Pipeline Status Monitor - Quick Assessment")
    print_info("=" * 60)

    if not IMPORTS_OK:
        print_error("❌ Failed to import required modules")
        return

    try:
        # Hardware check
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        if device.type == "cuda":
            gpu_name = torch.cuda.get_device_name(0)
            print_success(f"✅ GPU: {gpu_name}")
        else:
            print_warning("⚠️  No CUDA GPU detected")

        # Initialize pipeline
        dataset_root = Path("F:/datasets")
        embedding_target = Path("F:/impressioncore-b1-embeddings-062125")

        pipeline = B1DatasetIntegrationPipeline(
            dataset_root=str(dataset_root),
            embedding_target=str(embedding_target)
        )

        print_info("\n📊 Running fast dataset assessment...")

        # Get fast summary
        summary = pipeline.get_fast_dataset_summary()

        print_info(f"\n📋 Dataset Status Summary:")
        print_info(f"   📁 Dataset root: {summary['dataset_root']}")
        print_info(f"   ✅ Structure validation: {summary['structure_validation']}")
        print_info(f"   🎯 Modalities ready: {summary['readiness_score']['modalities_ready']}")
        print_info(f"   📂 Main directories: {summary['readiness_score']['main_dirs_ready']}")
        print_info(f"   🚀 Overall ready: {summary['readiness_score']['overall_ready']}")

        print_info(f"\n🎯 Modality Details:")
        for modality, details in summary['modalities'].items():
            if details.get('exists'):
                status = "✅ READY" if details.get('has_content') else "⚠️  EMPTY"
                print_info(f"   {modality}: {status}")
            else:
                print_warning(f"   {modality}: ❌ MISSING")

        print_info(f"\n📊 Quick Metrics:")
        for key, value in summary['quick_metrics'].items():
            if isinstance(value, bool):
                status = "✅" if value else "❌"
                print_info(f"   {key}: {status}")
            else:
                print_info(f"   {key}: {value}")

        # Check embeddings directory
        if embedding_target.exists():
            print_success(f"✅ Embedding target exists: {embedding_target}")
        else:
            print_warning(f"⚠️  Embedding target missing: {embedding_target}")

        # Overall assessment
        if summary['readiness_score']['overall_ready']:
            print_success("\n🚀 B1 PIPELINE STATUS: READY FOR TRAINING")
            print_success("⚡ All major components are available and accessible")
        else:
            print_warning("\n⚠️  B1 PIPELINE STATUS: NEEDS ATTENTION")
            print_warning("🔧 Some components require configuration or data")

        print_info(f"\n⏱️  Status check completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    except Exception as e:
        print_error(f"❌ Status check failed: {e}")

if __name__ == "__main__":
    check_pipeline_status()
