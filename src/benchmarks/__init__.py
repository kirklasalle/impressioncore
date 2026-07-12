#!/usr/bin/env python3
"""
ImpressionCore Benchmarks Package

File: src/benchmarks/__init__.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-01-06 (System Timestamp)
Updated: April 2026
Status: B1 + B3 DEVELOPMENT

Purpose: Export benchmarking infrastructure for ImpressionCore performance
         testing, optimization, and validation for B1 and B3 models.

Authors:
- GitHub Copilot (Performance Engineering Lead)
- Kirk LaSalle (Project Owner)

License: MIT
Copyright (c) 2025-2026 ImpressionCore Team

Tags: [benchmarks, performance, optimization, b1, b3, testing, 2026]
"""

# Core benchmark infrastructure
from .b1_performance_suite import B1PerformanceBenchmark
from .b3_performance_suite import B3PerformanceBenchmark

__all__ = [
    "B1PerformanceBenchmark",
    "B3PerformanceBenchmark",
]

__version__ = "2.0.0"
__author__ = "ImpressionCore Team"
__description__ = "Performance benchmarking infrastructure for ImpressionCore B1 and B3"

def quick_b1_benchmark(output_dir: str = "benchmarks/results") -> dict:
    """
    Quick B1 performance benchmark function.
    
    Args:
        output_dir: Directory for saving benchmark results
        
    Returns:
        dict: Benchmark results summary
    """
    try:
        benchmark = B1PerformanceBenchmark(output_dir=output_dir)
        results = benchmark.run_comprehensive_benchmark()
        
        print(f"✅ B1 Quick Benchmark Complete!")
        return results
        
    except Exception as e:
        print(f"❌ B1 Quick Benchmark Failed: {e}")
        return {"success": False, "error": str(e)}

def validate_b1_hardware_compatibility() -> bool:
    """
    Quick validation of B1 hardware compatibility.
    
    Returns:
        bool: True if hardware is compatible with B1 requirements
    """
    try:
        benchmark = B1PerformanceBenchmark()
        results = benchmark.benchmark_hardware_compatibility()
        
        return results.get("success", False) and \
               results.get("metrics", {}).get("overall_compatibility", False)
               
    except Exception:
        return False

# Quick access functions for common benchmarking tasks
def benchmark_b1_instantiation():
    """Quick B1 model instantiation benchmark."""
    benchmark = B1PerformanceBenchmark()
    return benchmark.benchmark_b1_model_instantiation()

def benchmark_b1_inference():
    """Quick B1 inference speed benchmark."""
    benchmark = B1PerformanceBenchmark()
    return benchmark.benchmark_b1_inference_speed()

def benchmark_b1_compatibility():
    """Quick B1 hardware compatibility benchmark."""
    benchmark = B1PerformanceBenchmark()
    return benchmark.benchmark_hardware_compatibility()


# ── B3 Quick Access Functions ────────────────────────────────────────────

def quick_b3_benchmark(output_dir: str = "benchmarks/results/b3") -> dict:
    """Quick B3 performance benchmark (all 8 dimensions)."""
    try:
        benchmark = B3PerformanceBenchmark(output_dir=output_dir)
        return benchmark.run_comprehensive_benchmark()
    except Exception as e:
        print(f"❌ B3 Quick Benchmark Failed: {e}")
        return {"success": False, "error": str(e)}

def benchmark_b3_latency():
    """Quick B3 inference latency benchmark."""
    return B3PerformanceBenchmark().benchmark_inference_latency()

def benchmark_b3_vram():
    """Quick B3 VRAM utilization benchmark."""
    return B3PerformanceBenchmark().benchmark_vram_utilization()
