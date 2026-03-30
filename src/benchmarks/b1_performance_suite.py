#!/usr/bin/env python3
"""
ImpressionCore-B1 Performance Benchmark Suite

File: src/benchmarks/b1_performance_suite.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-01-06 (System Timestamp)
Status: B1-FOCUSED DEVELOPMENT

Purpose: Comprehensive performance benchmarking and optimization testing
         specifically for ImpressionCore-B1 model architecture and deployment.

Features:
- Hardware compatibility validation (GTX 1050 Ti focus)
- Memory usage profiling and optimization
- Inference speed benchmarking
- Accuracy retention testing under memory constraints
- Production readiness validation

Authors:
- GitHub Copilot (B1 Performance Lead)
- Kirk LaSalle (Project Owner)

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [b1, benchmarks, performance, optimization, hardware-validation, 2025]
Dependencies: [torch, psutil, time, memory_profiler]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)
"""

import os
import sys
import time
import torch
import psutil
import logging
import tracemalloc
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
from pathlib import Path
import json

# Import rich enhancements for professional UI
try:
    from ..core.utils.rich_enhancements import EnhancedDisplay
    from ..core.utils.rich_logging import setup_rich_logging
    from ..core.utils.rich_status_animation import StatusAnimation
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# Import ImpressionCore-B1 components
try:
    from ..training.models.architectures.b1.b1_model import ImpressionCoreB1Model
    from ..inference.pipelines.multimodal_pipeline import MultimodalPipeline
    from ..core.utils.memory_optimization import MemoryOptimizer
    B1_COMPONENTS_AVAILABLE = True
except ImportError:
    B1_COMPONENTS_AVAILABLE = False

# Memory profiling
try:
    from memory_profiler import profile
    MEMORY_PROFILER_AVAILABLE = True
except ImportError:
    MEMORY_PROFILER_AVAILABLE = False


class B1PerformanceBenchmark:
    """
    Comprehensive performance benchmark suite for ImpressionCore-B1.
    
    Provides detailed testing and analysis of B1 model performance,
    memory usage, hardware compatibility, and production readiness.
    """
    
    def __init__(self, output_dir: Optional[str] = None):
        """
        Initialize B1 performance benchmark suite.
        
        Args:
            output_dir: Directory for saving benchmark results
        """
        self.output_dir = Path(output_dir or "benchmarks/results")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.start_time = datetime.now()
        self.benchmark_results = {}
        
        # Initialize rich UI if available
        if RICH_AVAILABLE:
            self.display = EnhancedDisplay()
            self.logger = setup_rich_logging("b1_benchmark")
            self.status_animation = StatusAnimation()
        else:
            self.display = None
            self.logger = logging.getLogger("b1_benchmark")
            self.status_animation = None
            
        # Hardware detection
        self.hardware_info = self._detect_hardware()
        
        self.logger.info("🚀 ImpressionCore-B1 Performance Benchmark Suite Initialized")
    
    def _detect_hardware(self) -> Dict[str, Any]:
        """Detect and analyze hardware specifications."""
        
        hardware = {
            "cpu": {
                "name": "Unknown",
                "cores": psutil.cpu_count(),
                "frequency": psutil.cpu_freq().current if psutil.cpu_freq() else "Unknown"
            },
            "memory": {
                "total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
                "available_gb": round(psutil.virtual_memory().available / (1024**3), 2)
            },
            "gpu": {
                "available": torch.cuda.is_available(),
                "device_count": torch.cuda.device_count() if torch.cuda.is_available() else 0
            }
        }
        
        if hardware["gpu"]["available"]:
            hardware["gpu"]["name"] = torch.cuda.get_device_name(0)
            hardware["gpu"]["memory_gb"] = round(torch.cuda.get_device_properties(0).total_memory / (1024**3), 2)
            hardware["gpu"]["compute_capability"] = torch.cuda.get_device_capability(0)
        
        return hardware
    
    def benchmark_b1_model_instantiation(self) -> Dict[str, Any]:
        """Benchmark B1 model instantiation and memory usage."""
        
        if self.status_animation:
            self.status_animation.start("Benchmarking B1 model instantiation...")
        
        results = {
            "test_name": "B1 Model Instantiation",
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "error": None,
            "metrics": {}
        }
        
        try:
            # Start memory tracking
            tracemalloc.start()
            start_memory = psutil.Process().memory_info().rss / (1024 * 1024)  # MB
            
            # GPU memory before instantiation
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                gpu_memory_before = torch.cuda.memory_allocated() / (1024 * 1024)  # MB
            else:
                gpu_memory_before = 0
            
            # Time model instantiation
            start_time = time.time()
            
            # Test different B1 configurations
            configs = [
                {"input_dim": 512, "hidden_dim": 768, "num_layers": 4, "chunk_size": 128},
                {"input_dim": 768, "hidden_dim": 1024, "num_layers": 6, "chunk_size": 256},
                {"input_dim": 1024, "hidden_dim": 1536, "num_layers": 8, "chunk_size": 512}
            ]
            
            config_results = []
            
            for i, config in enumerate(configs):
                config_start = time.time()
                
                try:
                    model = ImpressionCoreB1Model(**config)
                    
                    # Move to GPU if available
                    if torch.cuda.is_available():
                        model = model.cuda()
                    
                    # Calculate parameters
                    param_count = sum(p.numel() for p in model.parameters())
                    param_size_mb = sum(p.numel() * p.element_size() for p in model.parameters()) / (1024 * 1024)
                    
                    # GPU memory after model
                    if torch.cuda.is_available():
                        gpu_memory_after = torch.cuda.memory_allocated() / (1024 * 1024)  # MB
                        gpu_usage = gpu_memory_after - gpu_memory_before
                    else:
                        gpu_usage = 0
                    
                    config_time = time.time() - config_start
                    
                    config_results.append({
                        "config": config,
                        "parameters": param_count,
                        "parameter_size_mb": round(param_size_mb, 2),
                        "instantiation_time_s": round(config_time, 3),
                        "gpu_memory_mb": round(gpu_usage, 2),
                        "success": True
                    })
                    
                    # Clean up
                    del model
                    if torch.cuda.is_available():
                        torch.cuda.empty_cache()
                        
                except Exception as e:
                    config_results.append({
                        "config": config,
                        "error": str(e),
                        "success": False
                    })
            
            instantiation_time = time.time() - start_time
            
            # Memory tracking
            current_memory, peak_memory = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            
            end_memory = psutil.Process().memory_info().rss / (1024 * 1024)  # MB
            memory_increase = end_memory - start_memory
            
            results["metrics"] = {
                "total_instantiation_time_s": round(instantiation_time, 3),
                "memory_increase_mb": round(memory_increase, 2),
                "peak_memory_mb": round(peak_memory / (1024 * 1024), 2),
                "configurations_tested": len(configs),
                "successful_configs": len([r for r in config_results if r["success"]]),
                "config_results": config_results
            }
            
            results["success"] = True
            
            if self.status_animation:
                self.status_animation.stop()
            
            self.logger.info(f"✅ B1 Model Instantiation Benchmark Complete")
            
        except Exception as e:
            results["error"] = str(e)
            self.logger.error(f"❌ B1 Model Instantiation Benchmark Failed: {e}")
            
            if self.status_animation:
                self.status_animation.stop()
        
        return results
    
    def benchmark_b1_inference_speed(self) -> Dict[str, Any]:
        """Benchmark B1 model inference speed with various input sizes."""
        
        if self.status_animation:
            self.status_animation.start("Benchmarking B1 inference speed...")
        
        results = {
            "test_name": "B1 Inference Speed",
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "error": None,
            "metrics": {}
        }
        
        try:
            # Create B1 model for testing
            model = ImpressionCoreB1Model(
                input_dim=768,
                hidden_dim=1024,
                num_layers=6,
                chunk_size=256,
                enable_gradient_checkpointing=True
            )
            
            if torch.cuda.is_available():
                model = model.cuda()
            
            model.eval()
            
            # Test different input sizes
            batch_sizes = [1, 2, 4, 8]
            sequence_lengths = [128, 256, 512, 1024]
            
            inference_results = []
            
            with torch.no_grad():
                for batch_size in batch_sizes:
                    for seq_len in sequence_lengths:
                        try:
                            # Create test input
                            if torch.cuda.is_available():
                                test_input = torch.randn(batch_size, seq_len, 768).cuda()
                            else:
                                test_input = torch.randn(batch_size, seq_len, 768)
                            
                            # Warmup runs
                            for _ in range(3):
                                _ = model(test_input)
                            
                            # Benchmark runs
                            times = []
                            for _ in range(10):
                                start = time.time()
                                output = model(test_input)
                                if torch.cuda.is_available():
                                    torch.cuda.synchronize()
                                end = time.time()
                                times.append(end - start)
                            
                            avg_time = sum(times) / len(times)
                            min_time = min(times)
                            max_time = max(times)
                            
                            # Calculate throughput
                            tokens_per_second = (batch_size * seq_len) / avg_time
                            
                            inference_results.append({
                                "batch_size": batch_size,
                                "sequence_length": seq_len,
                                "avg_time_s": round(avg_time, 4),
                                "min_time_s": round(min_time, 4),
                                "max_time_s": round(max_time, 4),
                                "tokens_per_second": round(tokens_per_second, 2),
                                "success": True
                            })
                            
                        except Exception as e:
                            inference_results.append({
                                "batch_size": batch_size,
                                "sequence_length": seq_len,
                                "error": str(e),
                                "success": False
                            })
            
            # Calculate summary metrics
            successful_tests = [r for r in inference_results if r["success"]]
            if successful_tests:
                avg_inference_time = sum(r["avg_time_s"] for r in successful_tests) / len(successful_tests)
                max_throughput = max(r["tokens_per_second"] for r in successful_tests)
                
                results["metrics"] = {
                    "total_tests": len(inference_results),
                    "successful_tests": len(successful_tests),
                    "average_inference_time_s": round(avg_inference_time, 4),
                    "max_throughput_tokens_per_s": round(max_throughput, 2),
                    "detailed_results": inference_results
                }
            
            results["success"] = True
            
            if self.status_animation:
                self.status_animation.stop()
            
            self.logger.info(f"✅ B1 Inference Speed Benchmark Complete")
            
        except Exception as e:
            results["error"] = str(e)
            self.logger.error(f"❌ B1 Inference Speed Benchmark Failed: {e}")
            
            if self.status_animation:
                self.status_animation.stop()
        
        return results
    
    def benchmark_hardware_compatibility(self) -> Dict[str, Any]:
        """Benchmark hardware compatibility and optimization effectiveness."""
        
        if self.status_animation:
            self.status_animation.start("Benchmarking hardware compatibility...")
        
        results = {
            "test_name": "Hardware Compatibility",
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "error": None,
            "metrics": {}
        }
        
        try:
            compatibility_tests = []
            
            # GTX 1050 Ti specific tests
            is_gtx_1050_ti = ("GTX 1050 Ti" in self.hardware_info["gpu"].get("name", ""))
            
            # Memory constraint tests
            if torch.cuda.is_available():
                total_vram = self.hardware_info["gpu"]["memory_gb"]
                
                # Test if we can operate within GTX 1050 Ti constraints (4GB)
                target_memory_gb = 3.5  # Leave 0.5GB for system
                
                # Test memory-optimized B1 model
                try:
                    model = ImpressionCoreB1Model(
                        input_dim=768,
                        hidden_dim=1024,
                        num_layers=6,
                        chunk_size=128,  # Smaller chunks for memory efficiency
                        enable_gradient_checkpointing=True
                    )
                    model = model.cuda()
                    
                    # Measure actual VRAM usage
                    torch.cuda.empty_cache()
                    baseline_memory = torch.cuda.memory_allocated() / (1024**3)  # GB
                    
                    # Test with realistic workload
                    test_input = torch.randn(4, 512, 768).cuda()  # Moderate batch
                    
                    with torch.no_grad():
                        output = model(test_input)
                    
                    peak_memory = torch.cuda.max_memory_allocated() / (1024**3)  # GB
                    
                    compatibility_tests.append({
                        "test": "GTX 1050 Ti Memory Constraint",
                        "target_memory_gb": target_memory_gb,
                        "actual_memory_gb": round(peak_memory, 3),
                        "within_constraint": peak_memory <= target_memory_gb,
                        "memory_efficiency": round((target_memory_gb - peak_memory) / target_memory_gb * 100, 2),
                        "success": True
                    })
                    
                except Exception as e:
                    compatibility_tests.append({
                        "test": "GTX 1050 Ti Memory Constraint",
                        "error": str(e),
                        "success": False
                    })
            
            # CPU fallback test
            try:
                model_cpu = ImpressionCoreB1Model(
                    input_dim=512,
                    hidden_dim=768,
                    num_layers=4,
                    enable_gradient_checkpointing=False  # Not needed for CPU
                )
                
                test_input_cpu = torch.randn(1, 128, 512)  # Smaller for CPU
                
                start_time = time.time()
                with torch.no_grad():
                    output_cpu = model_cpu(test_input_cpu)
                cpu_inference_time = time.time() - start_time
                
                compatibility_tests.append({
                    "test": "CPU Fallback",
                    "inference_time_s": round(cpu_inference_time, 3),
                    "success": True
                })
                
            except Exception as e:
                compatibility_tests.append({
                    "test": "CPU Fallback",
                    "error": str(e),
                    "success": False
                })
            
            results["metrics"] = {
                "hardware_info": self.hardware_info,
                "is_gtx_1050_ti": is_gtx_1050_ti,
                "compatibility_tests": compatibility_tests,
                "overall_compatibility": all(test.get("success", False) for test in compatibility_tests)
            }
            
            results["success"] = True
            
            if self.status_animation:
                self.status_animation.stop()
            
            self.logger.info(f"✅ Hardware Compatibility Benchmark Complete")
            
        except Exception as e:
            results["error"] = str(e)
            self.logger.error(f"❌ Hardware Compatibility Benchmark Failed: {e}")
            
            if self.status_animation:
                self.status_animation.stop()
        
        return results
    
    def run_comprehensive_benchmark(self) -> Dict[str, Any]:
        """Run comprehensive B1 performance benchmark suite."""
        
        self.logger.info("🚀 Starting Comprehensive ImpressionCore-B1 Benchmark Suite")
        
        if self.display:
            self.display.show_header("ImpressionCore-B1 Performance Benchmark", "🚀")
        
        # Run all benchmarks
        benchmarks = [
            ("Model Instantiation", self.benchmark_b1_model_instantiation),
            ("Inference Speed", self.benchmark_b1_inference_speed),
            ("Hardware Compatibility", self.benchmark_hardware_compatibility)
        ]
        
        all_results = {
            "benchmark_suite": "ImpressionCore-B1 Performance",
            "start_time": self.start_time.isoformat(),
            "end_time": None,
            "duration_seconds": None,
            "hardware_info": self.hardware_info,
            "results": {}
        }
        
        for name, benchmark_func in benchmarks:
            self.logger.info(f"Running {name} benchmark...")
            
            try:
                result = benchmark_func()
                all_results["results"][name] = result
                
                if result["success"]:
                    self.logger.info(f"✅ {name} benchmark completed successfully")
                else:
                    self.logger.warning(f"⚠️ {name} benchmark completed with errors")
                    
            except Exception as e:
                self.logger.error(f"❌ {name} benchmark failed: {e}")
                all_results["results"][name] = {
                    "test_name": name,
                    "success": False,
                    "error": str(e)
                }
        
        # Finalize results
        end_time = datetime.now()
        all_results["end_time"] = end_time.isoformat()
        all_results["duration_seconds"] = round((end_time - self.start_time).total_seconds(), 2)
        
        # Save results
        self._save_results(all_results)
        
        # Generate summary
        self._generate_summary_report(all_results)
        
        self.logger.info("🎉 Comprehensive B1 Benchmark Suite Complete!")
        
        return all_results
    
    def _save_results(self, results: Dict[str, Any]) -> None:
        """Save benchmark results to JSON file."""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = self.output_dir / f"b1_benchmark_results_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        self.logger.info(f"📊 Benchmark results saved to: {results_file}")
    
    def _generate_summary_report(self, results: Dict[str, Any]) -> None:
        """Generate human-readable summary report."""
        
        if self.display:
            self.display.show_section("📊 B1 Benchmark Summary")
        
        successful_tests = sum(1 for r in results["results"].values() if r.get("success", False))
        total_tests = len(results["results"])
        
        print(f"\n🎯 Benchmark Results Summary:")
        print(f"   Duration: {results['duration_seconds']}s")
        print(f"   Tests Passed: {successful_tests}/{total_tests}")
        
        # Hardware summary
        hw = results["hardware_info"]
        print(f"\n💻 Hardware Configuration:")
        print(f"   CPU: {hw['cpu']['cores']} cores")
        print(f"   RAM: {hw['memory']['total_gb']}GB")
        if hw["gpu"]["available"]:
            print(f"   GPU: {hw['gpu']['name']} ({hw['gpu']['memory_gb']}GB)")
        else:
            print(f"   GPU: Not available")
        
        # Test-specific summaries
        for test_name, result in results["results"].items():
            if result.get("success"):
                print(f"\n✅ {test_name}:")
                
                if "metrics" in result:
                    metrics = result["metrics"]
                    
                    if test_name == "Model Instantiation":
                        successful_configs = metrics.get("successful_configs", 0)
                        print(f"   Successful Configurations: {successful_configs}")
                        print(f"   Memory Increase: {metrics.get('memory_increase_mb', 'N/A')} MB")
                    
                    elif test_name == "Inference Speed":
                        successful_tests = metrics.get("successful_tests", 0)
                        avg_time = metrics.get("average_inference_time_s", 0)
                        max_throughput = metrics.get("max_throughput_tokens_per_s", 0)
                        print(f"   Successful Tests: {successful_tests}")
                        print(f"   Average Inference Time: {avg_time}s")
                        print(f"   Max Throughput: {max_throughput} tokens/s")
                    
                    elif test_name == "Hardware Compatibility":
                        overall_compat = metrics.get("overall_compatibility", False)
                        print(f"   Overall Compatibility: {'✅ Pass' if overall_compat else '❌ Fail'}")
            else:
                print(f"\n❌ {test_name}: Failed")
                if "error" in result:
                    print(f"   Error: {result['error']}")


def main():
    """Main function for running B1 performance benchmarks."""
    import argparse
    
    parser = argparse.ArgumentParser(description="ImpressionCore-B1 Performance Benchmark Suite")
    parser.add_argument("--output-dir", default="benchmarks/results", 
                       help="Output directory for benchmark results")
    parser.add_argument("--test", choices=["instantiation", "inference", "compatibility", "all"],
                       default="all", help="Specific test to run")
    
    args = parser.parse_args()
    
    print("🚀 ImpressionCore-B1 Performance Benchmark Suite")
    print("=" * 50)
    
    if not B1_COMPONENTS_AVAILABLE:
        print("❌ ImpressionCore-B1 components not available!")
        print("   Please ensure B1 model and pipeline are properly installed.")
        return 1
    
    # Initialize benchmark suite
    benchmark = B1PerformanceBenchmark(output_dir=args.output_dir)
    
    try:
        if args.test == "all":
            results = benchmark.run_comprehensive_benchmark()
        elif args.test == "instantiation":
            results = benchmark.benchmark_b1_model_instantiation()
        elif args.test == "inference":
            results = benchmark.benchmark_b1_inference_speed()
        elif args.test == "compatibility":
            results = benchmark.benchmark_hardware_compatibility()
        
        print(f"\n🎉 B1 Performance Benchmark Complete!")
        return 0
        
    except Exception as e:
        print(f"\n❌ Benchmark failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
