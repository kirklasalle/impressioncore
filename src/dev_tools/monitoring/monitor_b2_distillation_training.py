#!/usr/bin/env python3
r"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #attention_mechanism #cuda #gpu_optimization #memory_management #python #source_code #src/dev_tools/monitoring/monitor_b2_distillation_training.py #testing #training
**Category:** Development Tools
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:01
# Author:** ImpressionCore Team
# Tags:** #attention_mechanism #cuda #gpu_optimization #memory_management #python #source_code #src/dev_tools/monitoring/monitor_b2_distillation_training.py #testing #training
# Category:** Development Tools
# Status:** Active

"""
ImpressionCore B2 Distillation Training Monitor
Monitor Phase 1 training with comprehensive distillation preparation
"""

import json
import os
from datetime import datetime
from pathlib import Path

import h5py
import torch


def monitor_training_status():
    """Monitor current B2 training and distillation capture status"""

    print("🤖 ImpressionCore B2 Distillation Training Monitor")
    print("=" * 60)
    print(f"📅 Monitoring Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Check distillation directories
    phase1_dir = Path("src/training/phase1_outputs")
    Path("src/training/phase2_prep")

    if phase1_dir.exists():
        print("✅ Phase 1 Output Directory: ACTIVE")

        # Check for recent captures
        repr_dir = phase1_dir / "representations"
        pred_dir = phase1_dir / "predictions"
        meta_dir = phase1_dir / "metadata"

        if repr_dir.exists():
            repr_files = list(repr_dir.glob("*.h5"))
            print(f"📊 Representation Files: {len(repr_files)} captured")
            if repr_files:
                latest_repr = max(repr_files, key=os.path.getctime)
                print(f"   Latest: {latest_repr.name}")

        if pred_dir.exists():
            pred_files = list(pred_dir.glob("*.h5"))
            print(f"🎯 Prediction Files: {len(pred_files)} captured")
            if pred_files:
                latest_pred = max(pred_files, key=os.path.getctime)
                print(f"   Latest: {latest_pred.name}")

        if meta_dir.exists():
            meta_files = list(meta_dir.glob("*.json"))
            print(f"📋 Metadata Files: {len(meta_files)} captured")
            if meta_files:
                latest_meta = max(meta_files, key=os.path.getctime)
                print(f"   Latest: {latest_meta.name}")

                # Load and display latest metrics
                try:
                    with open(latest_meta) as f:
                        metadata = json.load(f)

                    if 'training_metrics' in metadata:
                        metrics = metadata['training_metrics']
                        print("\n📈 Latest Training Metrics:")
                        print(f"   Loss: {metrics.get('loss', 'N/A'):.4f}")
                        print(f"   Sentiment Accuracy: {metrics.get('sentiment_acc', 'N/A'):.3f}")
                        print(f"   Intent Accuracy: {metrics.get('intent_acc', 'N/A'):.3f}")
                        print(f"   Global Step: {metrics.get('global_step', 'N/A')}")

                    if 'distillation_config' in metadata:
                        dist_config = metadata['distillation_config']
                        print("\n🎯 Distillation Configuration:")
                        print(f"   Temperature: {dist_config.get('temperature', 'N/A')}")
                        capture_settings = dist_config.get('capture_settings', {})
                        print(f"   Capturing Representations: {'✅' if capture_settings.get('representations') else '❌'}")
                        print(f"   Capturing Attention Maps: {'✅' if capture_settings.get('attention_maps') else '❌'}")
                        print(f"   Capturing Predictions: {'✅' if capture_settings.get('prediction_patterns') else '❌'}")

                except Exception as e:
                    print(f"   Error reading metadata: {e}")
    else:
        print("❌ Phase 1 Output Directory: NOT FOUND")

    print()

    # Check checkpoint status
    checkpoint_dir = Path("checkpoints")
    if checkpoint_dir.exists():
        recent_checkpoints = []
        for checkpoint_subdir in checkpoint_dir.iterdir():
            if checkpoint_subdir.is_dir() and checkpoint_subdir.name.startswith("b2_"):
                recent_checkpoints.append((checkpoint_subdir, os.path.getctime(checkpoint_subdir)))

        if recent_checkpoints:
            recent_checkpoints.sort(key=lambda x: x[1], reverse=True)
            latest_checkpoint_dir = recent_checkpoints[0][0]
            latest_time = datetime.fromtimestamp(recent_checkpoints[0][1])

            print(f"💾 Latest Checkpoint: {latest_checkpoint_dir.name}")
            print(f"   Created: {latest_time.strftime('%Y-%m-%d %H:%M:%S')}")

            # Check for model files in latest checkpoint
            model_files = list(latest_checkpoint_dir.glob("*.pth"))
            if model_files:
                print(f"   Model Files: {len(model_files)}")
                for model_file in model_files[:3]:  # Show first 3
                    print(f"     - {model_file.name}")

    print()

    # Memory and system info
    if torch.cuda.is_available():
        device = torch.cuda.get_device_name(0)
        memory_allocated = torch.cuda.memory_allocated(0) / 1024**3  # GB
        memory_cached = torch.cuda.memory_reserved(0) / 1024**3  # GB

        print("🔧 Hardware Status:")
        print(f"   GPU: {device}")
        print(f"   VRAM Allocated: {memory_allocated:.2f} GB")
        print(f"   VRAM Cached: {memory_cached:.2f} GB")
    else:
        print("⚠️  CUDA not available - running on CPU")

    print()
    print("🎯 B2 Mode Status: ✅ ACTIVE - Distillation capture operational")
    print("📊 Teacher-Student Pipeline: Ready for Phase 2 transition")

def analyze_distillation_data():
    """Analyze captured distillation data quality"""

    print("\n🔍 Distillation Data Quality Analysis")
    print("-" * 40)

    phase1_dir = Path("src/training/phase1_outputs")

    if not phase1_dir.exists():
        print("❌ No distillation data found")
        return

    # Analyze representation files
    repr_dir = phase1_dir / "representations"
    if repr_dir.exists():
        repr_files = list(repr_dir.glob("*.h5"))

        total_samples = 0
        modalities_found = set()

        for repr_file in repr_files:
            try:
                with h5py.File(repr_file, 'r') as f:
                    step_groups = [key for key in f if key.startswith('step_')]
                    total_samples += len(step_groups)

                    # Check available modalities
                    if step_groups:
                        first_step = f[step_groups[0]]
                        modalities_found.update(first_step.keys())

            except Exception as e:
                print(f"   Error reading {repr_file.name}: {e}")

        print("📊 Representation Data:")
        print(f"   Total Samples: {total_samples}")
        print(f"   Modalities: {', '.join(sorted(modalities_found))}")

    # Analyze prediction files
    pred_dir = phase1_dir / "predictions"
    if pred_dir.exists():
        pred_files = list(pred_dir.glob("*.h5"))

        total_predictions = 0
        prediction_types = set()

        for pred_file in pred_files:
            try:
                with h5py.File(pred_file, 'r') as f:
                    step_groups = [key for key in f if key.startswith('step_')]
                    total_predictions += len(step_groups)

                    if step_groups:
                        first_step = f[step_groups[0]]
                        prediction_types.update(first_step.keys())

            except Exception as e:
                print(f"   Error reading {pred_file.name}: {e}")

        print("🎯 Prediction Data:")
        print(f"   Total Predictions: {total_predictions}")
        print(f"   Types: {', '.join(sorted(prediction_types))}")

    print(f"\n✅ Distillation data quality: {'EXCELLENT' if total_samples > 0 else 'COLLECTING'}")

if __name__ == "__main__":
    try:
        monitor_training_status()
        analyze_distillation_data()

        print(f"\n🔄 Monitor completed at {datetime.now().strftime('%H:%M:%S')}")
        print("💡 Run this script periodically to monitor training progress")

    except KeyboardInterrupt:
        print("\n⏹️  Monitoring stopped by user")
    except Exception as e:
        print(f"\n❌ Error during monitoring: {e}")
