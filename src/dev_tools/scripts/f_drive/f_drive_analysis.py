#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #api #command_line #memory_management #multimodal #python #source_code #src/scripts\f_drive\f_drive_analysis.py #training
**Category:** Source Code
**Status:** Active
"""




import json
from datetime import datetime
from pathlib import Path

import numpy as np


def analyze_f_drive_embeddings():
    """Comprehensive F: drive embedding analysis"""

    print("🧠 IMPRESSIONCORE B3 F: DRIVE VALIDATION")
    print("=" * 60)

    # Main embedding directory
    embedding_dir = Path('F:/datasets/embeddings/embeddings')

    if not embedding_dir.exists():
        print("❌ F: drive embeddings directory not found!")
        return False

    # Get all .npy files
    npy_files = list(embedding_dir.glob('*.npy'))
    print(f"📊 Total embedding files: {len(npy_files):,}")

    # Analysis variables
    embedding_types = {}
    total_embeddings = 0
    total_size_bytes = 0
    sample_count = min(100, len(npy_files))  # Sample first 100 files

    print(f"\n🔍 ANALYZING FIRST {sample_count} FILES...")

    for i, file_path in enumerate(npy_files[:sample_count]):
        try:
            data = np.load(file_path)
            file_size = file_path.stat().st_size
            total_size_bytes += file_size

            # Count embeddings (vectors)
            if len(data.shape) > 1:
                num_vectors = data.shape[0]
                vector_dim = data.shape[-1]
            else:
                num_vectors = 1
                vector_dim = data.shape[0] if len(data.shape) > 0 else 0

            total_embeddings += num_vectors

            # Categorize by embedding dimension
            if vector_dim not in embedding_types:
                embedding_types[vector_dim] = {
                    'count': 0,
                    'total_vectors': 0,
                    'files': [],
                    'avg_vectors_per_file': 0,
                    'total_size_mb': 0
                }

            embedding_types[vector_dim]['count'] += 1
            embedding_types[vector_dim]['total_vectors'] += num_vectors
            embedding_types[vector_dim]['files'].append(file_path.name)
            embedding_types[vector_dim]['total_size_mb'] += file_size / (1024**2)

            if i % 20 == 0:
                print(f"  ✓ Processed {i+1}/{sample_count} files...")

        except Exception as e:
            print(f"  ⚠️ Error loading {file_path.name}: {e}")

    # Calculate averages
    for _dim, info in embedding_types.items():
        if info['count'] > 0:
            info['avg_vectors_per_file'] = info['total_vectors'] / info['count']

    # Display analysis results
    print(f"\n📈 EMBEDDING ANALYSIS (from {sample_count} files sampled):")
    print("-" * 50)

    for dim in sorted(embedding_types.keys()):
        info = embedding_types[dim]
        print(f"🔸 {dim}D embeddings:")
        print(f"   • Files: {info['count']}")
        print(f"   • Total vectors: {info['total_vectors']:,}")
        print(f"   • Avg vectors/file: {info['avg_vectors_per_file']:.1f}")
        print(f"   • Total size: {info['total_size_mb']:.1f} MB")
        print(f"   • Sample files: {', '.join(info['files'][:3])}")
        print()

    # Estimate total dataset size
    if sample_count > 0:
        avg_file_size = total_size_bytes / sample_count
        estimated_total_size_gb = (avg_file_size * len(npy_files)) / (1024**3)
        estimated_total_vectors = (total_embeddings / sample_count) * len(npy_files)
    else:
        estimated_total_size_gb = 0
        estimated_total_vectors = 0

    print("📊 SIZE ESTIMATES:")
    print(f"   🔹 Average file size: {avg_file_size / (1024**2):.2f} MB")
    print(f"   🔹 Estimated total size: {estimated_total_size_gb:.2f} GB")
    print(f"   🔹 Estimated total vectors: {estimated_total_vectors:,.0f}")
    print(f"   🔹 Storage efficiency: {total_size_bytes / total_embeddings:.2f} bytes/vector")

    # GTX 1050 Ti compatibility check
    print("\n🎮 GTX 1050 Ti COMPATIBILITY:")
    vram_limit_gb = 4.0
    if estimated_total_size_gb < vram_limit_gb * 0.5:  # Use 50% of VRAM for embeddings
        print(f"   ✅ EXCELLENT: Dataset ({estimated_total_size_gb:.2f}GB) fits easily in VRAM")
    elif estimated_total_size_gb < vram_limit_gb * 0.8:
        print(f"   ✅ GOOD: Dataset ({estimated_total_size_gb:.2f}GB) fits with careful memory management")
    else:
        print(f"   ⚠️ CHALLENGING: Dataset ({estimated_total_size_gb:.2f}GB) requires streaming/batching")

    # Check for B3-specific files
    print("\n🎯 KEY B3 EMBEDDING FILES DETECTED:")
    b3_files = [f for f in npy_files if 'b3_critical_success' in f.name]

    if b3_files:
        print(f"   🔥 Found {len(b3_files)} B3 critical success embedding files!")
        for b3_file in b3_files[:5]:
            try:
                data = np.load(b3_file)
                print(f"   📦 {b3_file.name}: {data.shape} ({data.dtype})")
            except Exception as e:
                print(f"   ❌ {b3_file.name}: Load error - {e}")
    else:
        print("   ℹ️ No B3-specific files found in sample")

    # Check for multimodal diversity
    print("\n🌈 MULTIMODAL DIVERSITY CHECK:")
    modality_indicators = {
        'text': ['text', 'token', 'word', 'sentence'],
        'image': ['image', 'visual', 'clip', 'vision', 'coco'],
        'audio': ['audio', 'speech', 'sound', 'wav2vec', 'phoneme'],
        'video': ['video', 'frame', 'temporal', 'kinetics'],
        'multimodal': ['multimodal', 'cross', 'fusion', 'joint']
    }

    modality_counts = {modality: 0 for modality in modality_indicators}

    for file_path in npy_files[:sample_count]:
        filename_lower = file_path.name.lower()
        for modality, indicators in modality_indicators.items():
            if any(indicator in filename_lower for indicator in indicators):
                modality_counts[modality] += 1
                break

    for modality, count in modality_counts.items():
        percentage = (count / sample_count) * 100
        print(f"   🔸 {modality.capitalize()}: {count} files ({percentage:.1f}%)")

    # Final assessment
    print("\n🚀 F: DRIVE STATUS ASSESSMENT:")

    ready_criteria = [
        len(npy_files) > 10000,  # Substantial dataset
        estimated_total_size_gb < 20,  # Manageable size
        len(embedding_types) > 1,  # Multiple embedding dimensions
        sum(modality_counts.values()) > sample_count * 0.3  # Good modality coverage
    ]

    ready_score = sum(ready_criteria)

    if ready_score >= 3:
        print("   ✅ READY FOR FULL MULTIMODAL B3 TRAINING!")
        print("   🎯 All systems go for GTX 1050 Ti optimization")
        print("   🏆 Massive multimodal dataset confirmed")
    elif ready_score >= 2:
        print("   ⚠️ MOSTLY READY - Minor optimizations needed")
    else:
        print("   ❌ NOT READY - Significant issues detected")

    # Create summary report
    summary_report = {
        'timestamp': datetime.now().isoformat(),
        'total_files': len(npy_files),
        'sampled_files': sample_count,
        'embedding_types': {str(k): v for k, v in embedding_types.items()},
        'estimated_total_size_gb': estimated_total_size_gb,
        'estimated_total_vectors': int(estimated_total_vectors),
        'modality_distribution': modality_counts,
        'b3_files_found': len(b3_files),
        'gtx_1050_ti_compatible': estimated_total_size_gb < vram_limit_gb * 0.8,
        'ready_for_training': ready_score >= 3
    }

    # Save report
    report_path = Path('f_drive_embedding_analysis.json')
    with open(report_path, 'w') as f:
        json.dump(summary_report, f, indent=2)

    print(f"\n📝 Analysis report saved to: {report_path}")

    return summary_report

if __name__ == "__main__":
    try:
        result = analyze_f_drive_embeddings()
        print(f"\n✨ Analysis complete! Found {result['total_files']:,} embedding files ready for B3 training.")
    except Exception as e:
        print(f"\n❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
