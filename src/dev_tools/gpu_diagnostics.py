#!/usr/bin/env python3
"""
ImpressionCore: GPU Diagnostics and VRAM Optimization Utility

A comprehensive tool for diagnosing GPU performance, monitoring VRAM usage,
and optimizing memory allocation for the GTX 1050 Ti (4GB VRAM) target.

File: src/dev_tools/gpu_diagnostics.py
Created: 2025-01-06
Modified: 2025-01-06
"""

import gc
import logging
import sys
import time
import torch
import traceback
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import pynvml
    PYNVML_AVAILABLE = True
except ImportError:
    PYNVML_AVAILABLE = False
    print("Warning: pynvml not available, GPU monitoring will be limited")

try:
    import nvidia_ml_py3 as nvml
    NVIDIA_ML_AVAILABLE = True
except ImportError:
    NVIDIA_ML_AVAILABLE = False

try:
    from core.utils.rich_enhancements import create_progress, create_panel
    from core.utils.rich_logging import setup_rich_logging
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# Setup rich logging if available
if RICH_AVAILABLE:
    logger = setup_rich_logging(__name__)
else:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

class GPUDiagnostics:
    """Comprehensive GPU diagnostics and optimization utility"""
    
    def __init__(self):
        """Initialize GPU diagnostics"""
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.gpu_available = torch.cuda.is_available()
        self.device_count = torch.cuda.device_count() if self.gpu_available else 0
        
        # Initialize NVIDIA ML if available
        self.nvml_initialized = False
        if NVIDIA_ML_AVAILABLE and self.gpu_available:
            try:
                nvml.nvmlInit()
                self.nvml_initialized = True
            except Exception as e:
                logger.warning(f"Failed to initialize NVIDIA ML: {e}")
    
    def get_gpu_info(self) -> Dict:
        """Get comprehensive GPU information"""
        info = {
            "cuda_available": self.gpu_available,
            "device_count": self.device_count,
            "devices": []
        }
        
        if not self.gpu_available:
            return info
        
        for i in range(self.device_count):
            device_info = {
                "id": i,
                "name": torch.cuda.get_device_name(i),
                "capability": torch.cuda.get_device_capability(i),
                "total_memory": torch.cuda.get_device_properties(i).total_memory,
                "total_memory_gb": torch.cuda.get_device_properties(i).total_memory / 1e9,
                "multi_processor_count": torch.cuda.get_device_properties(i).multi_processor_count,
            }
            
            # Add current memory usage
            torch.cuda.set_device(i)
            device_info.update({
                "allocated_memory": torch.cuda.memory_allocated(i),
                "allocated_memory_gb": torch.cuda.memory_allocated(i) / 1e9,
                "reserved_memory": torch.cuda.memory_reserved(i),
                "reserved_memory_gb": torch.cuda.memory_reserved(i) / 1e9,
                "free_memory": device_info["total_memory"] - torch.cuda.memory_allocated(i),
                "free_memory_gb": (device_info["total_memory"] - torch.cuda.memory_allocated(i)) / 1e9,
            })
            
            # Add NVIDIA ML info if available
            if self.nvml_initialized:
                try:
                    handle = nvml.nvmlDeviceGetHandleByIndex(i)
                    meminfo = nvml.nvmlDeviceGetMemoryInfo(handle)
                    utilization = nvml.nvmlDeviceGetUtilizationRates(handle)
                    temperature = nvml.nvmlDeviceGetTemperature(handle, nvml.NVML_TEMPERATURE_GPU)
                    power = nvml.nvmlDeviceGetPowerUsage(handle) / 1000.0  # Convert to watts
                    
                    device_info.update({
                        "nvml_memory_total": meminfo.total,
                        "nvml_memory_used": meminfo.used,
                        "nvml_memory_free": meminfo.free,
                        "gpu_utilization": utilization.gpu,
                        "memory_utilization": utilization.memory,
                        "temperature": temperature,
                        "power_usage": power,
                    })
                except Exception as e:
                    logger.warning(f"Failed to get NVIDIA ML info for device {i}: {e}")
            
            info["devices"].append(device_info)
        
        return info
    
    def memory_test(self, size_mb: int = 100) -> Dict:
        """Test GPU memory allocation and deallocation"""
        if not self.gpu_available:
            return {"status": "failed", "reason": "CUDA not available"}
        
        try:
            # Record initial memory
            initial_allocated = torch.cuda.memory_allocated()
            initial_reserved = torch.cuda.memory_reserved()
              # Allocate test tensor
            size_bytes = size_mb * 1024 * 1024
            num_elements = size_bytes // 4  # 4 bytes per float32
            test_tensor = torch.randn(num_elements, device=self.device, dtype=torch.float32)
            
            # Record after allocation
            after_alloc_allocated = torch.cuda.memory_allocated()
            after_alloc_reserved = torch.cuda.memory_reserved()
              # Perform some operations (keep it simple for memory safety)
            result_tensor = test_tensor * 2.0
            torch.cuda.synchronize()
            
            # Record after operations
            after_ops_allocated = torch.cuda.memory_allocated()
            after_ops_reserved = torch.cuda.memory_reserved()
            
            # Clean up
            del test_tensor, result_tensor
            torch.cuda.empty_cache()
            gc.collect()
            
            # Record after cleanup
            final_allocated = torch.cuda.memory_allocated()
            final_reserved = torch.cuda.memory_reserved()
            
            return {
                "status": "success",
                "target_size_mb": size_mb,
                "memory_stages": {
                    "initial": {"allocated": initial_allocated, "reserved": initial_reserved},
                    "after_alloc": {"allocated": after_alloc_allocated, "reserved": after_alloc_reserved},
                    "after_ops": {"allocated": after_ops_allocated, "reserved": after_ops_reserved},
                    "final": {"allocated": final_allocated, "reserved": final_reserved},
                },
                "memory_leak": final_allocated - initial_allocated,
                "cache_cleanup": (after_ops_reserved - final_reserved) > 0
            }
            
        except Exception as e:
            return {
                "status": "failed",
                "reason": str(e),
                "traceback": traceback.format_exc()
            }
    
    def performance_benchmark(self, iterations: int = 100) -> Dict:
        """Run GPU performance benchmark"""
        if not self.gpu_available:
            return {"status": "failed", "reason": "CUDA not available"}
        
        try:
            # Small tensors for GTX 1050 Ti
            size = 512
            
            # Warmup
            a = torch.randn(size, size, device=self.device)
            b = torch.randn(size, size, device=self.device)
            torch.matmul(a, b)
            torch.cuda.synchronize()
            
            # Benchmark matrix multiplication
            start_time = time.perf_counter()
            for _ in range(iterations):
                c = torch.matmul(a, b)
                torch.cuda.synchronize()
            end_time = time.perf_counter()
            
            matmul_time = (end_time - start_time) / iterations
            
            # Benchmark memory transfer
            cpu_tensor = torch.randn(size, size)
            start_time = time.perf_counter()
            for _ in range(iterations):
                gpu_tensor = cpu_tensor.to(self.device)
                torch.cuda.synchronize()
            end_time = time.perf_counter()
            
            transfer_time = (end_time - start_time) / iterations
            
            # Calculate performance metrics
            flops = 2 * size**3  # Matrix multiplication FLOPS
            tflops = flops / (matmul_time * 1e12)
            
            # Cleanup
            del a, b, c, cpu_tensor, gpu_tensor
            torch.cuda.empty_cache()
            
            return {
                "status": "success",
                "iterations": iterations,
                "matrix_size": size,
                "matmul_time_ms": matmul_time * 1000,
                "transfer_time_ms": transfer_time * 1000,
                "tflops": tflops,
                "memory_bandwidth_gbps": (size * size * 4) / (transfer_time * 1e9)
            }
            
        except Exception as e:
            return {
                "status": "failed",
                "reason": str(e),
                "traceback": traceback.format_exc()
            }
    
    def optimize_for_gtx_1050_ti(self) -> Dict:
        """Provide GTX 1050 Ti specific optimization recommendations"""
        recommendations = {
            "memory_management": [
                "Use gradient checkpointing to reduce VRAM usage",
                "Enable mixed precision training with torch.cuda.amp",
                "Implement batch size reduction for large models",
                "Use cpu_offload for optimizer states",
                "Clear cache regularly with torch.cuda.empty_cache()",
            ],
            "training_settings": [
                "Batch size: 2-8 for most models",
                "Gradient accumulation steps: 4-8",
                "Mixed precision: torch.float16 or torch.bfloat16",
                "Model sharding: Use accelerate library",
                "Sequence length: Limit to 512-1024 tokens",
            ],
            "model_settings": [
                "Use smaller model variants (7B → 3B parameters)",
                "Enable parameter sharing where possible",
                "Use LoRA/QLoRA for fine-tuning",
                "Implement dynamic batching",
                "Consider model pruning and quantization",
            ],
            "system_settings": [
                "Ensure adequate system RAM (16GB+ recommended)",
                "Use fast SSD for model storage and swapping",
                "Monitor system temperature and throttling",
                "Close unnecessary applications",
                "Use TensorFlow memory growth or PyTorch memory fraction",
            ]
        }
        
        gpu_info = self.get_gpu_info()
        if gpu_info["devices"]:
            device = gpu_info["devices"][0]
            memory_gb = device["total_memory_gb"]
            
            if memory_gb <= 4.5:
                recommendations["immediate_actions"] = [
                    "Enable memory optimization in all training scripts",
                    "Use batch_size=1 for initial testing",
                    "Enable cpu_offload for large models",
                    "Monitor memory usage with tools like this diagnostic script",
                ]
        
        return recommendations
    
    def clear_gpu_memory(self) -> Dict:
        """Clear GPU memory and provide cleanup report"""
        if not self.gpu_available:
            return {"status": "failed", "reason": "CUDA not available"}
        
        try:
            # Record before cleanup
            before_allocated = torch.cuda.memory_allocated()
            before_reserved = torch.cuda.memory_reserved()
            
            # Perform cleanup
            gc.collect()
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
            
            # Force garbage collection multiple times
            for _ in range(3):
                gc.collect()
            
            # Record after cleanup
            after_allocated = torch.cuda.memory_allocated()
            after_reserved = torch.cuda.memory_reserved()
            
            return {
                "status": "success",
                "memory_freed": {
                    "allocated_mb": (before_allocated - after_allocated) / 1e6,
                    "reserved_mb": (before_reserved - after_reserved) / 1e6,
                },
                "final_usage": {
                    "allocated_mb": after_allocated / 1e6,
                    "reserved_mb": after_reserved / 1e6,
                }
            }
            
        except Exception as e:
            return {
                "status": "failed",
                "reason": str(e)
            }

def main():
    """Main diagnostic routine"""
    try:
        if RICH_AVAILABLE:
            print(create_panel("🔧 ImpressionCore GPU Diagnostics & VRAM Optimizer", "bold green"))
        else:
            print("=" * 60)
            print("🔧 ImpressionCore GPU Diagnostics & VRAM Optimizer")
            print("=" * 60)
        print("🎯 Optimized for NVIDIA GTX 1050 Ti (4GB VRAM)")
        print("=" * 60)
        
        diagnostics = GPUDiagnostics()
        
        # Basic GPU Information
        print("\n📊 GPU Information:")
        print("-" * 30)
        gpu_info = diagnostics.get_gpu_info()
        
        if not gpu_info["cuda_available"]:
            print("❌ CUDA is not available!")
            return
        
        for device in gpu_info["devices"]:
            print(f"🎮 Device {device['id']}: {device['name']}")
            print(f"   💾 Memory: {device['total_memory_gb']:.1f} GB total")
            print(f"   📈 Used: {device['allocated_memory_gb']:.2f} GB ({device['allocated_memory_gb']/device['total_memory_gb']*100:.1f}%)")
            print(f"   🆓 Free: {device['free_memory_gb']:.2f} GB")
            print(f"   🔢 Compute Capability: {device['capability'][0]}.{device['capability'][1]}")
            
            if "temperature" in device:
                print(f"   🌡️ Temperature: {device['temperature']}°C")
                print(f"   ⚡ Power: {device['power_usage']:.1f}W")
                print(f"   🎯 GPU Utilization: {device['gpu_utilization']}%")
          # Memory Test
        print("\n🧪 Memory Allocation Test:")
        print("-" * 30)
        memory_test = diagnostics.memory_test(50)  # Reduced to 50MB test for GTX 1050 Ti
        if memory_test["status"] == "success":
            print("✅ Memory allocation test passed")
            stages = memory_test["memory_stages"]
            print(f"   Initial: {stages['initial']['allocated']/1e6:.1f}MB allocated")
            print(f"   After alloc: {stages['after_alloc']['allocated']/1e6:.1f}MB allocated")
            print(f"   After ops: {stages['after_ops']['allocated']/1e6:.1f}MB allocated")
            print(f"   Final: {stages['final']['allocated']/1e6:.1f}MB allocated")
            if memory_test["memory_leak"] > 1e6:  # > 1MB leak
                print(f"   ⚠️ Memory leak detected: {memory_test['memory_leak']/1e6:.1f}MB")
            else:
                print("   ✅ No significant memory leaks detected")
        else:
            print(f"❌ Memory test failed: {memory_test['reason']}")
        
        # Performance Benchmark
        print("\n⚡ Performance Benchmark:")
        print("-" * 30)
        benchmark = diagnostics.performance_benchmark(50)  # Reduced iterations for GTX 1050 Ti
        if benchmark["status"] == "success":
            print("✅ Performance benchmark completed")
            print(f"   Matrix multiplication: {benchmark['matmul_time_ms']:.2f}ms")
            print(f"   Memory transfer: {benchmark['transfer_time_ms']:.2f}ms")
            print(f"   Performance: {benchmark['tflops']:.3f} TFLOPS")
            print(f"   Memory bandwidth: {benchmark['memory_bandwidth_gbps']:.1f} GB/s")
        else:
            print(f"❌ Benchmark failed: {benchmark['reason']}")
        
        # GTX 1050 Ti Optimization Recommendations
        print("\n🎯 GTX 1050 Ti Optimization Recommendations:")
        print("-" * 50)
        recommendations = diagnostics.optimize_for_gtx_1050_ti()
        
        for category, items in recommendations.items():
            if category == "immediate_actions":
                print(f"\n🚨 {category.replace('_', ' ').title()}:")
            else:
                print(f"\n📋 {category.replace('_', ' ').title()}:")
            for item in items:
                print(f"   • {item}")
        
        # Memory Cleanup
        print("\n🧹 GPU Memory Cleanup:")
        print("-" * 30)
        cleanup = diagnostics.clear_gpu_memory()
        if cleanup["status"] == "success":
            freed = cleanup["memory_freed"]
            final = cleanup["final_usage"]
            print(f"✅ Memory cleanup completed")
            print(f"   Freed: {freed['allocated_mb']:.1f}MB allocated, {freed['reserved_mb']:.1f}MB reserved")
            print(f"   Final usage: {final['allocated_mb']:.1f}MB allocated, {final['reserved_mb']:.1f}MB reserved")
        else:
            print(f"❌ Cleanup failed: {cleanup['reason']}")
        
        print("\n" + "=" * 60)
        print("🎉 GPU diagnostics completed successfully!")
        print("💡 Use these recommendations to optimize your ImpressionCore training")
        
    except Exception as e:
        logger.error(f"Diagnostic script failed: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
