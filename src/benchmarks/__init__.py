#!/usr/bin/env python3
"""
ImpressionCore Benchmarks Package

File: src/benchmarks/__init__.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-01-06 (System Timestamp)
Status: B1-FOCUSED DEVELOPMENT

Purpose: Export benchmarking infrastructure for ImpressionCore performance
         testing, optimization, and validation specifically focused on B1 model.

Authors:
- GitHub Copilot (Performance Engineering Lead)
- Kirk LaSalle (Project Owner)

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [benchmarks, performance, optimization, b1, testing, 2025]
"""

# Core benchmark infrastructure
from .b1_performance_suite import B1PerformanceBenchmark

# Benchmark utilities and helpers
__all__ = [
    "B1PerformanceBenchmark"
]

# Version information
__version__ = "1.0.0"
__author__ = "ImpressionCore Team"
__description__ = "Performance benchmarking infrastructure for ImpressionCore-B1"

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
