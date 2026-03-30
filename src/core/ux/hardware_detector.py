"""
Hardware Detection and Capability Assessment System for ImpressionCore

This module provides comprehensive hardware detection, performance profiling,
and capability assessment for optimal configuration adaptation.

Key Features:
- GPU capability assessment with memory and compute benchmarking
- CPU performance profiling with multi-core optimization
- Memory bandwidth testing and optimization
- Real-time resource monitoring and adaptation

Hardware Target: GTX 1050 Ti (4GB VRAM) with broader compatibility
"""

import time
import psutil
import platform
import subprocess
import asyncio
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import json
import threading
from concurrent.futures import ThreadPoolExecutor

# Import rich enhancements for better user experience
try:
    from ..utils.rich_enhancements import create_enhanced_console
    from ..utils.rich_logging import setup_rich_logging
    from ..utils.rich_status_animation import create_status_animation
except ImportError:
    # Fallback imports if rich utilities are not available
    create_enhanced_console = lambda: None
    setup_rich_logging = lambda x: None
    create_status_animation = lambda x: None


class HardwareType(str, Enum):
    """Hardware type classifications."""
    DISCRETE_GPU = "discrete_gpu"
    INTEGRATED_GPU = "integrated_gpu"
    CPU_ONLY = "cpu_only"
    UNKNOWN = "unknown"


class PerformanceTier(str, Enum):
    """Performance tier classifications."""
    HIGH_END = "high_end"      # RTX 4070+, 12GB+ VRAM
    MAINSTREAM = "mainstream"  # RTX 3060, 8GB VRAM
    ENTRY_LEVEL = "entry_level"  # GTX 1050 Ti, 4GB VRAM
    LOW_END = "low_end"        # Integrated graphics, <4GB
    UNKNOWN = "unknown"


@dataclass
class GPUCapabilities:
    """GPU capability assessment results."""
    name: str
    memory_total_gb: float
    memory_available_gb: float
    compute_capability: Optional[str] = None
    cuda_cores: Optional[int] = None
    tensor_cores: Optional[int] = None
    memory_bandwidth_gbps: Optional[float] = None
    max_frequency_mhz: Optional[int] = None
    power_limit_watts: Optional[int] = None
    performance_tier: PerformanceTier = PerformanceTier.UNKNOWN
    
    # Benchmarking results
    memory_bandwidth_actual: Optional[float] = None
    compute_score: Optional[float] = None
    inference_score: Optional[float] = None
    
    # Optimization recommendations
    recommended_precision: str = "fp16"
    recommended_batch_size: int = 1
    recommended_context_length: int = 32768
    supports_mixed_precision: bool = True


@dataclass
class CPUCapabilities:
    """CPU capability assessment results."""
    name: str
    cores_physical: int
    cores_logical: int
    base_frequency_ghz: float
    max_frequency_ghz: float
    cache_l3_mb: float
    architecture: str
    instruction_sets: List[str] = field(default_factory=list)
    
    # Benchmarking results
    single_core_score: Optional[float] = None
    multi_core_score: Optional[float] = None
    memory_bandwidth_score: Optional[float] = None
    
    # Performance characteristics
    numa_nodes: int = 1
    supports_avx512: bool = False
    supports_avx2: bool = False
    thermal_throttling_threshold: Optional[float] = None


@dataclass
class MemoryCapabilities:
    """System memory capability assessment."""
    total_gb: float
    available_gb: float
    speed_mhz: Optional[int] = None
    type: Optional[str] = None  # DDR4, DDR5, etc.
    channels: Optional[int] = None
    
    # Performance metrics
    bandwidth_gbps: Optional[float] = None
    latency_ns: Optional[float] = None
    
    # Usage patterns
    baseline_usage_gb: float = 0.0
    peak_usage_gb: float = 0.0
    fragmentation_score: float = 0.0


@dataclass
class SystemCapabilities:
    """Complete system capability assessment."""
    hardware_type: HardwareType
    performance_tier: PerformanceTier
    gpu: Optional[GPUCapabilities] = None
    cpu: CPUCapabilities = None
    memory: MemoryCapabilities = None
    
    # System-level characteristics
    platform: str = ""
    python_version: str = ""
    cuda_version: Optional[str] = None
    pytorch_version: Optional[str] = None
    
    # Optimization recommendations
    recommended_config: Dict[str, Any] = field(default_factory=dict)
    optimization_notes: List[str] = field(default_factory=list)
    
    # Benchmarking timestamp
    assessment_timestamp: float = field(default_factory=time.time)


class HardwareDetector:
    """
    Comprehensive hardware detection and capability assessment system.
    
    Provides detailed analysis of GPU, CPU, and memory capabilities with
    performance benchmarking and optimization recommendations.
    """
    
    def __init__(self, enable_benchmarking: bool = True, cache_results: bool = True):
        """
        Initialize the hardware detector.
        
        Args:
            enable_benchmarking: Whether to run performance benchmarks
            cache_results: Whether to cache detection results
        """
        self.enable_benchmarking = enable_benchmarking
        self.cache_results = cache_results
        self.cached_capabilities: Optional[SystemCapabilities] = None
        self.benchmark_executor = ThreadPoolExecutor(max_workers=4)
        
        # Rich console for enhanced output
        self.console = create_enhanced_console()
        self.logger = setup_rich_logging("hardware_detector")
        
        # Performance monitoring
        self.monitoring_active = False
        self.monitoring_thread: Optional[threading.Thread] = None
        self.resource_history: List[Dict[str, float]] = []
    
    async def detect_system_capabilities(self) -> SystemCapabilities:
        """
        Perform comprehensive system capability detection.
        
        Returns:
            Complete system capabilities assessment
        """
        if self.cache_results and self.cached_capabilities:
            # Check if cached results are still valid (within 1 hour)
            if time.time() - self.cached_capabilities.assessment_timestamp < 3600:
                return self.cached_capabilities
        
        with create_status_animation("🔍 Detecting Hardware Capabilities..."):
            # Basic system information
            capabilities = SystemCapabilities(
                hardware_type=HardwareType.UNKNOWN,
                performance_tier=PerformanceTier.UNKNOWN,
                platform=platform.platform(),
                python_version=platform.python_version()
            )
            
            # Detect CPU capabilities
            capabilities.cpu = await self._detect_cpu_capabilities()
            
            # Detect memory capabilities
            capabilities.memory = await self._detect_memory_capabilities()
            
            # Detect GPU capabilities
            capabilities.gpu = await self._detect_gpu_capabilities()
            
            # Determine hardware type and performance tier
            capabilities.hardware_type = self._classify_hardware_type(capabilities)
            capabilities.performance_tier = self._classify_performance_tier(capabilities)
            
            # Generate optimization recommendations
            capabilities.recommended_config = self._generate_optimization_config(capabilities)
            capabilities.optimization_notes = self._generate_optimization_notes(capabilities)
            
            # Cache results
            if self.cache_results:
                self.cached_capabilities = capabilities
            
            return capabilities
    
    async def _detect_gpu_capabilities(self) -> Optional[GPUCapabilities]:
        """Detect GPU capabilities with benchmarking."""
        try:
            # Try to detect NVIDIA GPU first
            gpu_info = await self._detect_nvidia_gpu()
            if gpu_info:
                return gpu_info
            
            # Try to detect AMD GPU
            gpu_info = await self._detect_amd_gpu()
            if gpu_info:
                return gpu_info
            
            # Try to detect Intel GPU
            gpu_info = await self._detect_intel_gpu()
            if gpu_info:
                return gpu_info
            
            return None
            
        except Exception as e:
            if self.logger:
                self.logger.warning(f"GPU detection failed: {e}")
            return None
    
    async def _detect_nvidia_gpu(self) -> Optional[GPUCapabilities]:
        """Detect NVIDIA GPU capabilities."""
        try:
            # Check if nvidia-ml-py is available
            try:
                import pynvml
                pynvml.nvmlInit()
                device_count = pynvml.nvmlDeviceGetCount()
                
                if device_count == 0:
                    return None
                
                # Get first GPU (primary)
                handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                
                # Basic information
                name = pynvml.nvmlDeviceGetName(handle).decode('utf-8')
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                
                gpu_caps = GPUCapabilities(
                    name=name,
                    memory_total_gb=memory_info.total / (1024**3),
                    memory_available_gb=memory_info.free / (1024**3)
                )
                
                # Detailed capabilities
                try:
                    # CUDA compute capability
                    major, minor = pynvml.nvmlDeviceGetCudaComputeCapability(handle)
                    gpu_caps.compute_capability = f"{major}.{minor}"
                    
                    # Power limit
                    power_limit = pynvml.nvmlDeviceGetPowerManagementLimitConstraints(handle)[1]
                    gpu_caps.power_limit_watts = power_limit // 1000  # Convert mW to W
                    
                    # Memory clock
                    mem_clock = pynvml.nvmlDeviceGetMaxClockInfo(handle, pynvml.NVML_CLOCK_MEM)
                    gpu_caps.max_frequency_mhz = mem_clock
                    
                except Exception:
                    pass  # Some information may not be available
                
                # Performance tier classification
                gpu_caps.performance_tier = self._classify_gpu_performance(gpu_caps)
                
                # Optimization recommendations
                self._set_gpu_optimization_recommendations(gpu_caps)
                
                # Run benchmarks if enabled
                if self.enable_benchmarking:
                    await self._benchmark_gpu(gpu_caps)
                
                return gpu_caps
                
            except ImportError:
                # Fall back to nvidia-smi if pynvml is not available
                return await self._detect_nvidia_gpu_fallback()
                
        except Exception as e:
            if self.logger:
                self.logger.debug(f"NVIDIA GPU detection failed: {e}")
            return None
    
    async def _detect_nvidia_gpu_fallback(self) -> Optional[GPUCapabilities]:
        """Fallback NVIDIA GPU detection using nvidia-smi."""
        try:
            # Run nvidia-smi to get GPU information
            result = subprocess.run([
                "nvidia-smi", 
                "--query-gpu=name,memory.total,memory.free,compute_cap",
                "--format=csv,noheader,nounits"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                return None
            
            lines = result.stdout.strip().split('\n')
            if not lines or not lines[0]:
                return None
            
            # Parse first GPU
            parts = [p.strip() for p in lines[0].split(',')]
            if len(parts) < 4:
                return None
            
            name, total_mem, free_mem, compute_cap = parts
            
            gpu_caps = GPUCapabilities(
                name=name,
                memory_total_gb=float(total_mem) / 1024,  # Convert MB to GB
                memory_available_gb=float(free_mem) / 1024,
                compute_capability=compute_cap
            )
            
            # Performance tier and recommendations
            gpu_caps.performance_tier = self._classify_gpu_performance(gpu_caps)
            self._set_gpu_optimization_recommendations(gpu_caps)
            
            return gpu_caps
            
        except Exception as e:
            if self.logger:
                self.logger.debug(f"NVIDIA GPU fallback detection failed: {e}")
            return None
    
    async def _detect_amd_gpu(self) -> Optional[GPUCapabilities]:
        """Detect AMD GPU capabilities."""
        # AMD GPU detection would go here
        # For now, return None as AMD support is not implemented
        return None
    
    async def _detect_intel_gpu(self) -> Optional[GPUCapabilities]:
        """Detect Intel GPU capabilities."""
        # Intel GPU detection would go here
        # For now, return None as Intel GPU support is not implemented
        return None
    
    async def _detect_cpu_capabilities(self) -> CPUCapabilities:
        """Detect CPU capabilities with performance assessment."""
        # Basic CPU information
        cpu_info = CPUCapabilities(
            name=platform.processor() or "Unknown CPU",
            cores_physical=psutil.cpu_count(logical=False) or 1,
            cores_logical=psutil.cpu_count(logical=True) or 1,
            base_frequency_ghz=0.0,  # Will be detected
            max_frequency_ghz=0.0,   # Will be detected
            cache_l3_mb=0.0,         # Will be detected
            architecture=platform.machine()
        )
        
        # Get CPU frequency information
        try:
            freq_info = psutil.cpu_freq()
            if freq_info:
                cpu_info.base_frequency_ghz = freq_info.current / 1000.0
                cpu_info.max_frequency_ghz = freq_info.max / 1000.0
        except Exception:
            # Default values for unknown frequencies
            cpu_info.base_frequency_ghz = 2.5
            cpu_info.max_frequency_ghz = 3.5
        
        # Detect instruction set support
        cpu_info.instruction_sets = self._detect_cpu_instruction_sets()
        cpu_info.supports_avx2 = "AVX2" in cpu_info.instruction_sets
        cpu_info.supports_avx512 = "AVX512" in cpu_info.instruction_sets
        
        # Run CPU benchmarks if enabled
        if self.enable_benchmarking:
            await self._benchmark_cpu(cpu_info)
        
        return cpu_info
    
    async def _detect_memory_capabilities(self) -> MemoryCapabilities:
        """Detect system memory capabilities."""
        memory_info = psutil.virtual_memory()
        
        memory_caps = MemoryCapabilities(
            total_gb=memory_info.total / (1024**3),
            available_gb=memory_info.available / (1024**3),
            baseline_usage_gb=(memory_info.total - memory_info.available) / (1024**3)
        )
          # Run memory benchmarks if enabled
        if self.enable_benchmarking:
            await self._benchmark_memory(memory_caps)
        
        return memory_caps
    
    def _detect_cpu_instruction_sets(self) -> List[str]:
        """Detect supported CPU instruction sets."""
        instruction_sets = []
        
        try:
            import cpuinfo
            cpu_info = cpuinfo.get_cpu_info()
            
            # Common instruction sets
            flags = cpu_info.get('flags', [])
            
            if 'sse' in flags:
                instruction_sets.append('SSE')
            if 'sse2' in flags:
                instruction_sets.append('SSE2')
            if 'sse3' in flags:
                instruction_sets.append('SSE3')
            if 'sse4_1' in flags:
                instruction_sets.append('SSE4.1')
            if 'sse4_2' in flags:
                instruction_sets.append('SSE4.2')
            if 'avx' in flags:
                instruction_sets.append('AVX')
            if 'avx2' in flags:
                instruction_sets.append('AVX2')
            if 'avx512f' in flags:
                instruction_sets.append('AVX512')
            if 'fma' in flags:
                instruction_sets.append('FMA')
                
        except ImportError:
            # Fallback without cpuinfo library
            instruction_sets = ['SSE', 'SSE2']  # Safe defaults
        except Exception as e:
            self.logger.warning(f"CPU instruction set detection failed: {e}")
            instruction_sets = ['SSE', 'SSE2']  # Safe defaults
        
        return instruction_sets
    
    async def _benchmark_gpu(self, gpu_caps: GPUCapabilities):
        """Run GPU performance benchmarks."""
        try:
            # Memory bandwidth test
            memory_bandwidth = await self._test_gpu_memory_bandwidth()
            if memory_bandwidth:
                gpu_caps.memory_bandwidth_actual = memory_bandwidth
            
            # Compute performance test
            compute_score = await self._test_gpu_compute_performance()
            if compute_score:
                gpu_caps.compute_score = compute_score
            
            # Inference performance test
            inference_score = await self._test_gpu_inference_performance()
            if inference_score:
                gpu_caps.inference_score = inference_score
                
        except Exception as e:
            if self.logger:
                self.logger.debug(f"GPU benchmarking failed: {e}")
    
    async def _benchmark_cpu(self, cpu_caps: CPUCapabilities):
        """Run CPU performance benchmarks."""
        try:
            # Single-core performance test
            single_score = await self._test_cpu_single_core()
            if single_score:
                cpu_caps.single_core_score = single_score
            
            # Multi-core performance test
            multi_score = await self._test_cpu_multi_core()
            if multi_score:
                cpu_caps.multi_core_score = multi_score
            
            # Memory bandwidth test
            memory_score = await self._test_cpu_memory_bandwidth()
            if memory_score:
                cpu_caps.memory_bandwidth_score = memory_score
                
        except Exception as e:
            if self.logger:
                self.logger.debug(f"CPU benchmarking failed: {e}")
    
    async def _benchmark_memory(self, memory_caps: MemoryCapabilities):
        """Run memory performance benchmarks."""
        try:
            # Memory bandwidth test
            bandwidth = await self._test_memory_bandwidth()
            if bandwidth:
                memory_caps.bandwidth_gbps = bandwidth
            
            # Memory latency test
            latency = await self._test_memory_latency()
            if latency:
                memory_caps.latency_ns = latency
                
        except Exception as e:
            if self.logger:
                self.logger.debug(f"Memory benchmarking failed: {e}")
    
    async def _test_gpu_memory_bandwidth(self) -> Optional[float]:
        """Test GPU memory bandwidth (GB/s)."""
        # Placeholder for GPU memory bandwidth test
        # Would implement actual GPU memory transfer benchmarks
        return None
    
    async def _test_gpu_compute_performance(self) -> Optional[float]:
        """Test GPU compute performance (GFLOPS)."""
        # Placeholder for GPU compute benchmark
        # Would implement matrix multiplication or similar compute-intensive test
        return None
    
    async def _test_gpu_inference_performance(self) -> Optional[float]:
        """Test GPU inference performance (tokens/sec)."""
        # Placeholder for inference performance test
        # Would run a small model inference benchmark
        return None
    
    async def _test_cpu_single_core(self) -> Optional[float]:
        """Test CPU single-core performance."""
        # Simple CPU benchmark - prime number calculation
        start_time = time.time()
        
        def is_prime(n):
            if n < 2:
                return False
            for i in range(2, int(n ** 0.5) + 1):
                if n % i == 0:
                    return False
            return True
        
        # Count primes up to 10000
        prime_count = sum(1 for i in range(2, 10000) if is_prime(i))
        end_time = time.time()
        
        # Score is primes per second
        elapsed = end_time - start_time
        return prime_count / elapsed if elapsed > 0 else None
    
    async def _test_cpu_multi_core(self) -> Optional[float]:
        """Test CPU multi-core performance."""
        # Multi-threaded prime counting
        import concurrent.futures
        
        def count_primes_range(start, end):
            def is_prime(n):
                if n < 2:
                    return False
                for i in range(2, int(n ** 0.5) + 1):
                    if n % i == 0:
                        return False
                return True
            
            return sum(1 for i in range(start, end) if is_prime(i))
        
        start_time = time.time()
        
        # Split work across CPU cores
        num_cores = psutil.cpu_count(logical=True)
        range_size = 10000 // num_cores
        
        with ThreadPoolExecutor(max_workers=num_cores) as executor:
            futures = []
            for i in range(num_cores):
                start = i * range_size
                end = (i + 1) * range_size if i < num_cores - 1 else 10000
                futures.append(executor.submit(count_primes_range, start, end))
            
            total_primes = sum(future.result() for future in futures)
        
        end_time = time.time()
        elapsed = end_time - start_time
        
        return total_primes / elapsed if elapsed > 0 else None
    
    async def _test_cpu_memory_bandwidth(self) -> Optional[float]:
        """Test CPU memory bandwidth."""
        # Simple memory copy test
        import array
        
        # Create large arrays
        size = 1024 * 1024  # 1MB
        source = array.array('d', range(size))
        
        start_time = time.time()
        
        # Copy data multiple times
        for _ in range(100):
            destination = array.array('d', source)
        
        end_time = time.time()
        elapsed = end_time - start_time
        
        # Calculate bandwidth (GB/s)
        bytes_copied = size * 8 * 100  # 8 bytes per double, 100 iterations
        return (bytes_copied / elapsed) / (1024**3) if elapsed > 0 else None
    
    async def _test_memory_bandwidth(self) -> Optional[float]:
        """Test system memory bandwidth."""
        return await self._test_cpu_memory_bandwidth()  # Same test
    
    async def _test_memory_latency(self) -> Optional[float]:
        """Test memory latency (nanoseconds)."""
        # Placeholder for memory latency test
        # Would implement random access pattern test
        return None
    
    def _classify_hardware_type(self, capabilities: SystemCapabilities) -> HardwareType:
        """Classify hardware type based on capabilities."""
        if capabilities.gpu:
            if capabilities.gpu.memory_total_gb >= 2.0:
                return HardwareType.DISCRETE_GPU
            else:
                return HardwareType.INTEGRATED_GPU
        else:
            return HardwareType.CPU_ONLY
    
    def _classify_performance_tier(self, capabilities: SystemCapabilities) -> PerformanceTier:
        """Classify overall performance tier."""
        if capabilities.gpu:
            return capabilities.gpu.performance_tier
        else:
            # CPU-only classification
            if capabilities.cpu.cores_physical >= 8:
                return PerformanceTier.MAINSTREAM
            elif capabilities.cpu.cores_physical >= 4:
                return PerformanceTier.ENTRY_LEVEL
            else:
                return PerformanceTier.LOW_END
    
    def _classify_gpu_performance(self, gpu: GPUCapabilities) -> PerformanceTier:
        """Classify GPU performance tier."""
        memory_gb = gpu.memory_total_gb
        
        if memory_gb >= 12.0:
            return PerformanceTier.HIGH_END
        elif memory_gb >= 8.0:
            return PerformanceTier.MAINSTREAM
        elif memory_gb >= 4.0:
            return PerformanceTier.ENTRY_LEVEL
        else:
            return PerformanceTier.LOW_END
    
    def _set_gpu_optimization_recommendations(self, gpu: GPUCapabilities):
        """Set optimization recommendations based on GPU capabilities."""
        memory_gb = gpu.memory_total_gb
        
        if memory_gb >= 12.0:
            # High-end GPU
            gpu.recommended_precision = "bf16"
            gpu.recommended_batch_size = 4
            gpu.recommended_context_length = 256000
        elif memory_gb >= 8.0:
            # Mainstream GPU  
            gpu.recommended_precision = "fp16"
            gpu.recommended_batch_size = 2
            gpu.recommended_context_length = 128000
        elif memory_gb >= 4.0:
            # Entry-level GPU (GTX 1050 Ti target)
            gpu.recommended_precision = "fp16"
            gpu.recommended_batch_size = 1
            gpu.recommended_context_length = 64000
        else:
            # Low-end GPU
            gpu.recommended_precision = "int8"
            gpu.recommended_batch_size = 1
            gpu.recommended_context_length = 32000
    
    def _generate_optimization_config(self, capabilities: SystemCapabilities) -> Dict[str, Any]:
        """Generate optimized configuration recommendations."""
        config = {
            "device": "cpu",
            "precision": "fp32",
            "batch_size": 1,
            "max_context_length": 16384,
            "memory_limit_gb": 2.0,
            "enable_mixed_precision": False,
            "enable_gradient_checkpointing": True,
            "enable_cpu_offload": False
        }
        
        # GPU-specific optimizations
        if capabilities.gpu:
            config["device"] = "cuda"
            config["precision"] = capabilities.gpu.recommended_precision
            config["batch_size"] = capabilities.gpu.recommended_batch_size
            config["max_context_length"] = capabilities.gpu.recommended_context_length
            config["memory_limit_gb"] = capabilities.gpu.memory_total_gb * 0.9  # 90% of GPU memory
            config["enable_mixed_precision"] = capabilities.gpu.supports_mixed_precision
            
            # Enable CPU offload for lower-end GPUs
            if capabilities.gpu.performance_tier in [PerformanceTier.ENTRY_LEVEL, PerformanceTier.LOW_END]:
                config["enable_cpu_offload"] = True
        
        # CPU optimizations
        if capabilities.cpu:
            if capabilities.cpu.cores_logical >= 8:
                config["num_workers"] = min(4, capabilities.cpu.cores_logical // 2)
            else:
                config["num_workers"] = 1
            
            # Enable optimizations for supported instruction sets
            if capabilities.cpu.supports_avx2:
                config["enable_avx2"] = True
            if capabilities.cpu.supports_avx512:
                config["enable_avx512"] = True
        
        # Memory optimizations
        if capabilities.memory:
            # Reserve memory for system
            available_memory = capabilities.memory.available_gb * 0.8
            if config["device"] == "cpu":
                config["memory_limit_gb"] = min(available_memory, 8.0)
        
        return config
    
    def _generate_optimization_notes(self, capabilities: SystemCapabilities) -> List[str]:
        """Generate human-readable optimization notes."""
        notes = []
        
        # Hardware-specific notes
        if capabilities.hardware_type == HardwareType.DISCRETE_GPU:
            notes.append(f"✅ Discrete GPU detected: {capabilities.gpu.name}")
            notes.append(f"💾 GPU Memory: {capabilities.gpu.memory_total_gb:.1f}GB")
            
            if capabilities.gpu.performance_tier == PerformanceTier.ENTRY_LEVEL:
                notes.append("⚡ Entry-level GPU detected - optimizing for GTX 1050 Ti profile")
                notes.append("🔧 Enabling memory-efficient settings and CPU offload")
            elif capabilities.gpu.performance_tier == PerformanceTier.MAINSTREAM:
                notes.append("🚀 Mainstream GPU detected - balanced performance settings")
            elif capabilities.gpu.performance_tier == PerformanceTier.HIGH_END:
                notes.append("🏆 High-end GPU detected - maximum performance settings")
        
        elif capabilities.hardware_type == HardwareType.CPU_ONLY:
            notes.append("🖥️ CPU-only processing mode")
            notes.append(f"⚡ CPU: {capabilities.cpu.cores_physical} cores @ {capabilities.cpu.max_frequency_ghz:.1f}GHz")
            
            if capabilities.cpu.supports_avx2:
                notes.append("✅ AVX2 support detected - enabling optimized CPU operations")
            if capabilities.cpu.supports_avx512:
                notes.append("✅ AVX512 support detected - maximum CPU optimization")
        
        # Memory notes
        if capabilities.memory:
            notes.append(f"💾 System Memory: {capabilities.memory.total_gb:.1f}GB available")
            
            if capabilities.memory.total_gb < 8.0:
                notes.append("⚠️ Limited system memory - enabling aggressive memory optimization")
            elif capabilities.memory.total_gb >= 16.0:
                notes.append("✅ Sufficient system memory for optimal performance")
        
        return notes
    
    def start_resource_monitoring(self, interval_seconds: float = 1.0):
        """Start continuous resource monitoring."""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(
            target=self._resource_monitoring_loop,
            args=(interval_seconds,),
            daemon=True
        )
        self.monitoring_thread.start()
    
    def stop_resource_monitoring(self):
        """Stop resource monitoring."""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5.0)
            self.monitoring_thread = None
    
    def _resource_monitoring_loop(self, interval: float):
        """Resource monitoring background loop."""
        while self.monitoring_active:
            try:
                # Collect current resource usage
                cpu_percent = psutil.cpu_percent(interval=None)
                memory = psutil.virtual_memory()
                
                resource_data = {
                    "timestamp": time.time(),
                    "cpu_percent": cpu_percent,
                    "memory_used_gb": (memory.total - memory.available) / (1024**3),
                    "memory_available_gb": memory.available / (1024**3),
                    "memory_percent": memory.percent
                }
                
                # Add GPU metrics if available
                try:
                    import pynvml
                    handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                    gpu_memory = pynvml.nvmlDeviceGetMemoryInfo(handle)
                    gpu_util = pynvml.nvmlDeviceGetUtilizationRates(handle)
                    
                    resource_data.update({
                        "gpu_memory_used_gb": gpu_memory.used / (1024**3),
                        "gpu_memory_free_gb": gpu_memory.free / (1024**3),
                        "gpu_utilization_percent": gpu_util.gpu,
                        "gpu_memory_utilization_percent": gpu_util.memory
                    })
                except Exception:
                    pass  # GPU monitoring not available
                
                # Store resource data
                self.resource_history.append(resource_data)
                
                # Keep only recent history (last 1000 samples)
                if len(self.resource_history) > 1000:
                    self.resource_history = self.resource_history[-1000:]
                
                time.sleep(interval)
                
            except Exception as e:
                if self.logger:
                    self.logger.debug(f"Resource monitoring error: {e}")
                time.sleep(interval)
    
    def get_current_resource_usage(self) -> Dict[str, float]:
        """Get current resource usage metrics."""
        if not self.resource_history:
            return {}
        
        return self.resource_history[-1]
    
    def get_resource_usage_history(self, duration_seconds: float = 60.0) -> List[Dict[str, float]]:
        """Get resource usage history for specified duration."""
        if not self.resource_history:
            return []
        
        cutoff_time = time.time() - duration_seconds
        return [
            data for data in self.resource_history 
            if data.get("timestamp", 0) >= cutoff_time
        ]
    
    def get_resource_usage_stats(self, duration_seconds: float = 60.0) -> Dict[str, Dict[str, float]]:
        """Get resource usage statistics for specified duration."""
        history = self.get_resource_usage_history(duration_seconds)
        if not history:
            return {}
        
        stats = {}
        
        # Calculate statistics for each metric
        for key in ["cpu_percent", "memory_percent", "gpu_utilization_percent", "gpu_memory_utilization_percent"]:
            values = [data.get(key, 0) for data in history if key in data]
            if values:
                stats[key] = {
                    "min": min(values),
                    "max": max(values),
                    "mean": sum(values) / len(values),
                    "current": values[-1] if values else 0
                }
        
        return stats


# Factory function for easy usage
def create_hardware_detector(enable_benchmarking: bool = True, cache_results: bool = True) -> HardwareDetector:
    """
    Factory function to create a HardwareDetector instance.
    
    Args:
        enable_benchmarking: Whether to run performance benchmarks
        cache_results: Whether to cache detection results
        
    Returns:
        Configured HardwareDetector instance
    """
    return HardwareDetector(enable_benchmarking, cache_results)


# Example usage
if __name__ == "__main__":
    async def main():
        detector = create_hardware_detector()
        capabilities = await detector.detect_system_capabilities()
        
        print(f"Hardware Type: {capabilities.hardware_type}")
        print(f"Performance Tier: {capabilities.performance_tier}")
        
        if capabilities.gpu:
            print(f"GPU: {capabilities.gpu.name}")
            print(f"GPU Memory: {capabilities.gpu.memory_total_gb:.1f}GB")
        
        print(f"CPU: {capabilities.cpu.cores_physical} cores")
        print(f"Memory: {capabilities.memory.total_gb:.1f}GB")
        
        print("\nOptimization Notes:")
        for note in capabilities.optimization_notes:
            print(f"  {note}")
    
    # asyncio.run(main())
