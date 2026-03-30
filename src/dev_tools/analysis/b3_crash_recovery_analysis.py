#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #multimodal #python #source_code #src/dev_tools/analysis/b3_crash_recovery_analysis.py
**Category:** Development Tools
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:01
# Author:** ImpressionCore Team
# Tags:** #multimodal #python #source_code #src\\dev_tools\\analysis\\b3_crash_recovery_analysis.py
# Category:** Development Tools
# Status:** Active

"""
🔍 B3 CRASH RECOVERY & PROGRESS ANALYSIS
Quick assessment of what was generated before the crash
"""

from datetime import datetime
from pathlib import Path

import numpy as np


def analyze_crash_recovery():
    """Analyze what was generated before the crash"""

    print("🔍 B3 CRASH RECOVERY ANALYSIS")
    print("=" * 50)
    print(f"📅 Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    f_drive = Path("F:\\")
    embeddings_dir = f_drive / "b3_professional_dataset" / "embeddings"

    if not embeddings_dir.exists():
        print("❌ Embeddings directory not found!")
        return

    total_embeddings = 0
    total_size_mb = 0

    modalities = {
        'text_embeddings': 0,
        'image_embeddings': 0,
        'audio_embeddings': 0,
        'multimodal_embeddings': 0
    }

    print("\n📊 CRASH RECOVERY PROGRESS ANALYSIS:")

    for modality in modalities:
        modality_dir = embeddings_dir / modality
        if modality_dir.exists():
            files = list(modality_dir.glob("*.npy"))
            modality_count = 0
            modality_size = 0

            for file in files:
                try:
                    # Load to get actual count
                    data = np.load(file)
                    file_count = data.shape[0] if len(data.shape) > 1 else 1
                    modality_count += file_count
                    modality_size += file.stat().st_size
                except Exception as e:
                    print(f"   ⚠️ Could not load {file}: {e}")

            modalities[modality] = modality_count
            total_embeddings += modality_count
            total_size_mb += modality_size / (1024 * 1024)

            print(f"   📝 {modality.replace('_', ' ').title()}: {modality_count:,}")

    print(f"\n🎯 TOTAL RECOVERED: {total_embeddings:,} embeddings")
    print(f"💾 Total Size: {total_size_mb:.1f} MB")

    # Calculate what we still need
    target = 500000
    remaining = max(0, target - total_embeddings)

    print("\n📈 PROGRESS STATUS:")
    print(f"   🎯 Target: {target:,}")
    print(f"   ✅ Generated: {total_embeddings:,}")
    print(f"   📊 Progress: {(total_embeddings/target)*100:.1f}%")
    print(f"   🚨 Remaining: {remaining:,}")

    if remaining > 0:
        print("\n🚀 RECOVERY PLAN:")
        print(f"   💡 Continue generation for {remaining:,} more embeddings")
        print("   ⚡ Use robust monitoring this time!")
    else:
        print("\n🎉 TARGET ACHIEVED! Ready for next phase!")

    return {
        'total_embeddings': total_embeddings,
        'modalities': modalities,
        'remaining': remaining,
        'progress_percent': (total_embeddings/target)*100
    }

if __name__ == "__main__":
    analyze_crash_recovery()
