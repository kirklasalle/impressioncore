#!/usr/bin/env python3
r"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #memory_management #python #source_code #src/dev_tools/examples/demo_embedding_discovery.py #testing #training
**Category:** Development Tools
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:01
# Author:** ImpressionCore Team
# Tags:** #memory_management #python #source_code #src/dev_tools/examples/demo_embedding_discovery.py #testing #training
# Category:** Development Tools
# Status:** Active

"""
ImpressionCore EDS Embedding Dataset Discovery Demo

This script demonstrates how to use the eds_discover_embedding_datasets tool
to find suitable datasets for embedding training with annotation support.

Usage:
    python demo_embedding_discovery.py
"""

import asyncio
import os
import sys

# Add the EDS server path to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '.mcp', 'impressioncore-eds'))

from enhanced_server import EnhancedEDSMCPServer


async def demo_basic_discovery():
    """Demonstrate basic embedding dataset discovery."""
    print("🔍 Demo 1: Basic Embedding Dataset Discovery")
    print("=" * 60)

    server = EnhancedEDSMCPServer()

    # Basic discovery with default parameters
    result = await server.handle_tool_call("eds_discover_embedding_datasets", {})

    if result["success"]:
        data = result["data"]
        print(f"✅ Found {data['total_found']} embedding-suitable datasets")
        print("📊 Annotation Summary:")
        summary = data["annotation_summary"]
        print(f"   - Datasets with validation: {summary.get('datasets_with_validation', 0)}")
        print(f"   - Average annotation coverage: {summary.get('average_annotation_coverage', 0):.1%}")
        print(f"   - Annotation types available: {len(summary.get('annotation_types_available', []))}")

        # Show top 3 datasets
        print("\n🏆 Top 3 Datasets:")
        for i, dataset in enumerate(data["embedding_datasets"][:3], 1):
            print(f"   {i}. {dataset['name']}")
            print(f"      - Suitability Score: {dataset['embedding_suitability_score']:.2f}")
            print(f"      - Quality Score: {dataset['quality_score']:.2f}")
            print(f"      - Memory Estimate: {dataset['estimated_memory_gb']:.1f}GB")
            print(f"      - Annotation Coverage: {dataset['annotation_coverage']:.1%}")
    else:
        print(f"❌ Error: {result['error']}")

    print("\n" + "=" * 60 + "\n")


async def demo_modality_specific():
    """Demonstrate modality-specific discovery."""
    print("🎯 Demo 2: Modality-Specific Discovery")
    print("=" * 60)

    server = EnhancedEDSMCPServer()

    modalities = ["text", "image", "audio"]

    for modality in modalities:
        print(f"\n📁 Discovering {modality} datasets...")

        result = await server.handle_tool_call("eds_discover_embedding_datasets", {
            "modality": modality,
            "min_annotation_coverage": 0.85,
            "require_validation_split": True
        })

        if result["success"]:
            data = result["data"]
            print(f"   ✅ Found {data['total_found']} {modality} datasets")

            if data["embedding_datasets"]:
                best = data["embedding_datasets"][0]
                print(f"   🥇 Best: {best['name']} (Score: {best['embedding_suitability_score']:.2f})")
            else:
                print("   ⚠️  No datasets found with current criteria")
        else:
            print(f"   ❌ Error: {result['error']}")

    print("\n" + "=" * 60 + "\n")


async def demo_hardware_constraints():
    """Demonstrate hardware-constrained discovery."""
    print("🖥️ Demo 3: Hardware-Constrained Discovery")
    print("=" * 60)

    server = EnhancedEDSMCPServer()

    # Different hardware configurations
    hardware_configs = [
        {"name": "GTX 1050 Ti", "vram_gb": 4, "max_dataset_size_gb": 10},
        {"name": "RTX 3060", "vram_gb": 12, "max_dataset_size_gb": 50},
        {"name": "RTX 4090", "vram_gb": 24, "max_dataset_size_gb": 100}
    ]

    for config in hardware_configs:
        print(f"\n💻 Testing {config['name']} configuration...")

        result = await server.handle_tool_call("eds_discover_embedding_datasets", {
            "hardware_constraints": {
                "vram_gb": config["vram_gb"],
                "max_dataset_size_gb": config["max_dataset_size_gb"]
            },
            "min_annotation_coverage": 0.8
        })

        if result["success"]:
            data = result["data"]
            datasets = data["embedding_datasets"]

            print(f"   ✅ Found {len(datasets)} compatible datasets")

            if datasets:
                # Show memory distribution
                memory_usage = [d["estimated_memory_gb"] for d in datasets]
                avg_memory = sum(memory_usage) / len(memory_usage)
                max_memory = max(memory_usage)

                print(f"   📊 Memory Usage: Avg {avg_memory:.1f}GB, Max {max_memory:.1f}GB")

                # Count datasets by size categories
                small = sum(1 for m in memory_usage if m <= 2)
                medium = sum(1 for m in memory_usage if 2 < m <= 8)
                large = sum(1 for m in memory_usage if m > 8)

                print(f"   📈 Size Distribution: Small({small}) Medium({medium}) Large({large})")
        else:
            print(f"   ❌ Error: {result['error']}")

    print("\n" + "=" * 60 + "\n")


async def demo_use_case_filtering():
    """Demonstrate use case specific filtering."""
    print("🎯 Demo 4: Use Case Specific Filtering")
    print("=" * 60)

    server = EnhancedEDSMCPServer()

    use_cases = ["classification", "similarity", "retrieval"]

    for use_case in use_cases:
        print(f"\n🔍 Discovering datasets for {use_case}...")

        result = await server.handle_tool_call("eds_discover_embedding_datasets", {
            "use_case": use_case,
            "modality": "text",
            "min_annotation_coverage": 0.8,
            "require_validation_split": True
        })

        if result["success"]:
            data = result["data"]
            datasets = data["embedding_datasets"]

            print(f"   ✅ Found {len(datasets)} datasets for {use_case}")

            if datasets:
                # Show top dataset with annotation details
                top_dataset = datasets[0]
                print(f"   🏆 Top Dataset: {top_dataset['name']}")
                print(f"      - Suitability: {top_dataset['embedding_suitability_score']:.2f}")
                print(f"      - Annotation Types: {', '.join(top_dataset['annotation_types'][:3])}")
                print(f"      - Notable Datasets: {', '.join(top_dataset['notable_datasets'][:3])}")
        else:
            print(f"   ❌ Error: {result['error']}")

    print("\n" + "=" * 60 + "\n")


async def demo_progressive_filtering():
    """Demonstrate progressive filtering strategy."""
    print("📈 Demo 5: Progressive Filtering Strategy")
    print("=" * 60)

    server = EnhancedEDSMCPServer()

    # Start with strict requirements, then progressively relax
    filters = [
        {"name": "Strict", "min_annotation_coverage": 0.95, "require_validation_split": True},
        {"name": "Moderate", "min_annotation_coverage": 0.85, "require_validation_split": True},
        {"name": "Relaxed", "min_annotation_coverage": 0.75, "require_validation_split": False},
        {"name": "Minimal", "min_annotation_coverage": 0.6, "require_validation_split": False}
    ]

    print("🔄 Applying progressive filtering for text similarity tasks...")

    for filter_config in filters:
        print(f"\n📊 {filter_config['name']} Filtering:")

        result = await server.handle_tool_call("eds_discover_embedding_datasets", {
            "modality": "text",
            "use_case": "similarity",
            "min_annotation_coverage": filter_config["min_annotation_coverage"],
            "require_validation_split": filter_config["require_validation_split"],
            "hardware_constraints": {"vram_gb": 4}
        })

        if result["success"]:
            data = result["data"]
            datasets = data["embedding_datasets"]

            print(f"   ✅ Found {len(datasets)} datasets")

            if datasets:
                # Calculate quality distribution
                scores = [d["embedding_suitability_score"] for d in datasets]
                avg_score = sum(scores) / len(scores)
                high_quality = sum(1 for s in scores if s > 0.8)

                print(f"   📊 Average Suitability: {avg_score:.2f}")
                print(f"   🏆 High Quality (>0.8): {high_quality}/{len(datasets)}")

                # Show validation split statistics
                summary = data["annotation_summary"]
                validation_pct = summary.get("validation_percentage", 0)
                print(f"   ✅ Validation Coverage: {validation_pct:.0f}%")
        else:
            print(f"   ❌ Error: {result['error']}")

    print("\n" + "=" * 60 + "\n")


async def demo_annotation_analysis():
    """Demonstrate annotation analysis."""
    print("📝 Demo 6: Annotation Analysis")
    print("=" * 60)

    server = EnhancedEDSMCPServer()

    result = await server.handle_tool_call("eds_discover_embedding_datasets", {
        "modality": "all",
        "min_annotation_coverage": 0.8,
        "require_validation_split": True
    })

    if result["success"]:
        data = result["data"]
        datasets = data["embedding_datasets"]

        print(f"📊 Annotation Analysis for {len(datasets)} datasets:")

        # Analyze annotation types
        all_annotation_types = set()
        annotation_type_counts = {}

        for dataset in datasets:
            types = dataset.get("annotation_types", [])
            all_annotation_types.update(types)

            for ann_type in types:
                annotation_type_counts[ann_type] = annotation_type_counts.get(ann_type, 0) + 1

        print(f"\n🏷️  Annotation Types ({len(all_annotation_types)} unique):")
        for ann_type, count in sorted(annotation_type_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(datasets)) * 100
            print(f"   - {ann_type}: {count} datasets ({percentage:.1f}%)")

        # Analyze annotation coverage distribution
        coverages = [d["annotation_coverage"] for d in datasets]
        avg_coverage = sum(coverages) / len(coverages)
        min_coverage = min(coverages)
        max_coverage = max(coverages)

        print("\n📈 Annotation Coverage Distribution:")
        print(f"   - Average: {avg_coverage:.1%}")
        print(f"   - Range: {min_coverage:.1%} - {max_coverage:.1%}")

        # Coverage brackets
        high_coverage = sum(1 for c in coverages if c >= 0.9)
        medium_coverage = sum(1 for c in coverages if 0.8 <= c < 0.9)
        low_coverage = sum(1 for c in coverages if c < 0.8)

        print(f"   - High (≥90%): {high_coverage} datasets")
        print(f"   - Medium (80-90%): {medium_coverage} datasets")
        print(f"   - Low (<80%): {low_coverage} datasets")

        # Show datasets with best annotation support
        print("\n🏆 Top 3 Datasets by Annotation Quality:")
        top_annotated = sorted(datasets, key=lambda x: x["annotation_coverage"], reverse=True)[:3]

        for i, dataset in enumerate(top_annotated, 1):
            print(f"   {i}. {dataset['name']}")
            print(f"      - Coverage: {dataset['annotation_coverage']:.1%}")
            print(f"      - Types: {', '.join(dataset['annotation_types'])}")
            print(f"      - Validation: {'✅' if dataset['validation_sets'] else '❌'}")
    else:
        print(f"❌ Error: {result['error']}")

    print("\n" + "=" * 60 + "\n")


async def main():
    """Run all demonstration scenarios."""
    print("🚀 ImpressionCore EDS Embedding Dataset Discovery Demo")
    print("=" * 60)
    print("This demo showcases the eds_discover_embedding_datasets tool")
    print("capabilities for finding annotation-rich datasets suitable for")
    print("embedding training on consumer hardware.")
    print("=" * 60)

    try:
        # Run all demos
        await demo_basic_discovery()
        await demo_modality_specific()
        await demo_hardware_constraints()
        await demo_use_case_filtering()
        await demo_progressive_filtering()
        await demo_annotation_analysis()

        print("✅ All demos completed successfully!")
        print("\n💡 Key Takeaways:")
        print("   - Use progressive filtering when strict criteria yield no results")
        print("   - Consider hardware constraints early in dataset selection")
        print("   - Annotation coverage and validation splits are crucial for quality")
        print("   - Different modalities and use cases require different strategies")
        print("   - The tool provides comprehensive metadata for informed decisions")

    except Exception as e:
        print(f"❌ Demo failed: {e!s}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
