"""
GPU Memory Manager for ImpressionCore.

This module provides utilities for managing GPU memory efficiently,
especially optimized for GPUs with limited VRAM like the GTX 1050 Ti.
"""

import os
import logging
import time
from typing import Dict, List, Optional, Tuple, Union
import csv
from pathlib import Path
import gc

import torch

# Configure logging
logger = logging.getLogger(__name__)

def get_gpu_memory_info(device: Optional[Union[int, torch.device]] = None) -> Dict[str, float]:
    """
    Get detailed information about GPU memory usage.
    
    Args:
        device: CUDA device ID or device object (None = default device)
        
    Returns:
        Dict containing memory info in MB:
        - total: Total memory on GPU
        - reserved: Memory reserved by PyTorch allocator
        - allocated: Memory actively allocated by tensors
        - free: Free memory (total - allocated)
        - uncached: Memory not yet cached by allocator (total - reserved)
        
    Raises:
        RuntimeError: If CUDA is not available
    """
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is not available. Unable to get GPU memory info.")
    
    if device is None:
        device = torch.cuda.current_device()
    elif isinstance(device, torch.device):
        device = device.index
    
    # Get memory stats
    props = torch.cuda.get_device_properties(device)
    total = props.total_memory / (1024 ** 2)  # Convert to MB
    
    # Get current allocation
    reserved = torch.cuda.memory_reserved(device) / (1024 ** 2)
    allocated = torch.cuda.memory_allocated(device) / (1024 ** 2)
    free = total - allocated
    uncached = total - reserved
    
    return {
        "total_mb": total,
        "reserved_mb": reserved,
        "allocated_mb": allocated,
        "free_mb": free,
        "uncached_mb": uncached,
        "device_name": props.name
    }

def calculate_optimal_batch_size(
    initial_batch_size: int,
    model: torch.nn.Module,
    sample_input: Union[torch.Tensor, List[torch.Tensor], Dict[str, torch.Tensor]],
    target_mem_usage: float = 0.8,
    max_attempts: int = 10,
    scale_factor: float = 0.75
) -> int:
    """
    Calculate the optimal batch size for a model based on available GPU memory.
    
    Args:
        initial_batch_size: Starting batch size to try
        model: PyTorch model to evaluate
        sample_input: Sample input(s) to the model (tensors will be resized for batch size)
        target_mem_usage: Target memory usage as a fraction of total available VRAM
        max_attempts: Maximum number of attempts to find optimal batch size
        scale_factor: Factor to scale batch size down by when out of memory
        
    Returns:
        Optimal batch size that fits in GPU memory
        
    Raises:
        RuntimeError: If couldn't find a working batch size after max_attempts
    """
    if not torch.cuda.is_available():
        logger.warning("CUDA not available, returning initial batch size")
        return initial_batch_size
    
    # Start with the provided batch size
    batch_size = initial_batch_size
    device = next(model.parameters()).device
    
    # Function to adjust tensor batch dimension
    def resize_batch(data, new_batch_size):
        if isinstance(data, torch.Tensor):
            shape = list(data.shape)
            if len(shape) > 0:  # Not a scalar
                current_batch = shape[0]
                scale = new_batch_size / current_batch
                # Handle case where we need to increase batch size
                if scale > 1:
                    return data.repeat(int(scale), *([1] * (len(shape) - 1)))
                else:
                    return data[:new_batch_size]
        elif isinstance(data, (list, tuple)) and len(data) > 0:
            return type(data)(resize_batch(x, new_batch_size) for x in data)
        elif isinstance(data, dict):
            return {k: resize_batch(v, new_batch_size) for k, v in data.items()}
        return data
    
    # Try to find optimal batch size
    attempts = 0
    while attempts < max_attempts:
        try:
            # Clear any existing allocations
            torch.cuda.empty_cache()
            gc.collect()
            
            # Prepare batch with current size
            inputs = resize_batch(sample_input, batch_size)
            
            # Record memory before forward pass
            mem_before = torch.cuda.memory_allocated(device)
            
            # Run forward pass to measure memory
            with torch.no_grad():
                _ = model(inputs)
            
            # Force synchronize to ensure all operations are completed
            torch.cuda.synchronize()
            
            # Check memory usage
            mem_after = torch.cuda.memory_allocated(device)
            mem_used = mem_after - mem_before
            total_mem = torch.cuda.get_device_properties(device).total_memory
            
            usage_fraction = mem_after / total_mem
            
            if usage_fraction <= target_mem_usage:
                # We found a good batch size
                logger.info(f"Optimal batch size: {batch_size} (using {usage_fraction:.1%} of GPU memory)")
                return batch_size
            else:
                # Memory usage too high, reduce batch size
                logger.info(f"Batch size {batch_size} uses {usage_fraction:.1%} of GPU memory (target: {target_mem_usage:.1%})")
                new_batch_size = max(1, int(batch_size * (target_mem_usage / usage_fraction)))
                
                if new_batch_size == batch_size:
                    # Can't reduce further, use scale factor
                    new_batch_size = max(1, int(batch_size * scale_factor))
                
                if new_batch_size == batch_size and batch_size > 1:
                    # Still can't reduce, just decrement
                    new_batch_size = batch_size - 1
                    
                batch_size = new_batch_size
        
        except RuntimeError as e:
            if "out of memory" in str(e).lower():
                # OOM error, reduce batch size
                logger.warning(f"Out of memory with batch size {batch_size}, reducing")
                batch_size = max(1, int(batch_size * scale_factor))
                if batch_size == 1:
                    logger.error("Cannot fit even batch size 1 in memory")
                    raise RuntimeError("Model is too large for available GPU memory even with batch size 1")
            else:
                # Some other error occurred
                raise
        
        attempts += 1
    
    # If we get here, we ran out of attempts
    logger.warning(f"Couldn't find optimal batch size after {max_attempts} attempts, using {batch_size}")
    return batch_size

def optimize_memory_usage(
    model: torch.nn.Module,
    precision: str = "float32",
    activation_checkpointing: bool = False,
    batch_accumulation: int = 1,
    optimize_transformer_attention: bool = True,
    use_gradient_checkpointing: bool = False,
    use_cpu_offload: bool = False,
    device: Optional[torch.device] = None
) -> torch.nn.Module:
    """
    Apply various memory optimization techniques to a PyTorch model.
    
    Args:
        model: PyTorch model to optimize
        precision: Numerical precision ("float32", "float16", "bfloat16")
        activation_checkpointing: Whether to enable activation checkpointing
        batch_accumulation: Number of microbatches for gradient accumulation
        optimize_transformer_attention: Whether to use optimized attention kernels
        use_gradient_checkpointing: Whether to use gradient checkpointing
        use_cpu_offload: Whether to offload modules to CPU when not in use
        device: Target device for the model
        
    Returns:
        Optimized model
    """
    import gc
    import logging
    from typing import Dict, Optional, Tuple, Union, List, Any
    
    logger = logging.getLogger(__name__)
    
    if not torch.cuda.is_available() and device is None:
        logger.warning("CUDA not available, skipping GPU memory optimizations")
        return model
        
    if device is None:
        device = torch.cuda.current_device()
        
    # Track original device for parameters
    original_device = next(model.parameters()).device
    
    # 1. Apply precision changes
    if precision == "float16":
        logger.info("Converting model to float16 precision")
        model.half()
    elif precision == "bfloat16" and torch.cuda.is_bf16_supported():
        logger.info("Converting model to bfloat16 precision") 
        model.to(dtype=torch.bfloat16)
    
    # 2. Apply activation checkpointing if requested
    if activation_checkpointing or use_gradient_checkpointing:
        # Look for transformer layers that support gradient checkpointing
        for name, module in model.named_modules():
            # Handle various model types that support checkpointing
            if hasattr(module, "gradient_checkpointing"):
                logger.info(f"Enabling gradient checkpointing for {name}")
                module.gradient_checkpointing = True
            
            # Try for Hugging Face transformer modules
            elif hasattr(module, "config") and hasattr(module.config, "gradient_checkpointing"):
                logger.info(f"Enabling HF gradient checkpointing for {name}")
                module.config.gradient_checkpointing = True
              
            # For custom transformer implementation  
            elif "transformer" in name.lower() and hasattr(module, "enable_gradient_checkpointing"):
                logger.info(f"Enabling custom gradient checkpointing for {name}")
                module.enable_gradient_checkpointing()

    # 3. Optimize transformer attention if requested
    if optimize_transformer_attention:
        # Check if we have attention modules that can be optimized
        try:
            import xformers
            import xformers.ops
            
            from src.core.utils.memory_optimization.attention import apply_xformers_attention
            logger.info("Applying xformers memory-efficient attention")
            apply_xformers_attention(model)
        except (ImportError, ModuleNotFoundError):
            try:
                # Try using Flash Attention as fallback
                from src.core.utils.memory_optimization.attention import apply_flash_attention
                logger.info("Applying Flash Attention optimizations")
                apply_flash_attention(model)
            except (ImportError, ModuleNotFoundError):
                logger.warning("Neither xformers nor Flash Attention available, skipping attention optimization")
    
    # 4. Apply CPU offloading if requested
    if use_cpu_offload:
        try:
            from src.core.utils.memory_optimization.cpu_offload import selective_cpu_offload, OffloadConfig
            
            # Identify suitable modules for offloading
            # Generally, encoder/decoder blocks are good candidates
            offload_candidates = []
            for name, _ in model.named_children():
                if any(x in name.lower() for x in ["encoder", "decoder", "embedd"]):
                    offload_candidates.append(name)
            
            if offload_candidates:
                logger.info(f"Setting up CPU offloading for modules: {offload_candidates}")
                config = OffloadConfig(modules_to_offload=offload_candidates)
                model = selective_cpu_offload(model, device=device, config=config)
            else:
                logger.warning("No suitable modules found for CPU offloading")
        except Exception as e:
            logger.warning(f"Failed to apply CPU offloading: {e}")
    
    # 5. Clear CUDA cache to maximize available memory
    torch.cuda.empty_cache()
    gc.collect()
    
    # Log memory usage after optimization
    if torch.cuda.is_available():
        mem_info = get_gpu_memory_info(device)
        logger.info(f"GPU memory after optimization: {mem_info['allocated_mb']:.2f}MB allocated, "
                   f"{mem_info['free_mb']:.2f}MB free")
    
    return model

class GPUMemoryManager:
    """
    Memory manager for efficient GPU operations.
    
    Provides utilities for tracking memory usage and optimizing memory allocation
    for better performance on limited VRAM devices like the GTX 1050 Ti.
    
    Args:
        vram_target_usage: Target VRAM usage as a fraction of total available (0-1)
        enable_shared_memory: Whether to use CUDA shared memory optimizations
        enable_monitoring: Whether to collect memory usage statistics
        log_file: Path to save memory usage logs (CSV format)
        log_interval: Interval in seconds for logging memory statistics
    """
    
    def __init__(
        self,
        vram_target_usage: float = 0.85,
        enable_shared_memory: bool = True,
        enable_monitoring: bool = False,
        log_file: Optional[str] = None,
        log_interval: float = 5.0
    ):
        self.vram_target_usage = min(max(0.1, vram_target_usage), 0.95)  # Constrain between 0.1 and 0.95
        self.enable_shared_memory = enable_shared_memory
        self.enable_monitoring = enable_monitoring
        self.log_interval = log_interval
        self.log_file = log_file
        
        # Initialize monitoring
        self.start_time = time.time()
        self.last_log_time = self.start_time
        self.memory_log = []
        
        # Track device availability
        self.has_cuda = torch.cuda.is_available()
        
        # Set up logging file if needed
        if self.enable_monitoring and self.log_file:
            log_path = Path(self.log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Initialize CSV file with headers
            with open(log_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp', 'elapsed_seconds', 
                    'total_vram_mb', 'allocated_vram_mb', 'reserved_vram_mb',
                    'percent_used', 'percent_reserved'
                ])
        
        # Log initialization
        if self.has_cuda:
            device = torch.cuda.current_device()
            device_name = torch.cuda.get_device_name(device)
            total_memory = torch.cuda.get_device_properties(device).total_memory / (1024 ** 2)
            logger.info(
                f"Initialized GPU Memory Manager: {device_name}, "
                f"Total VRAM: {total_memory:.2f}MB, "
                f"Target usage: {self.vram_target_usage * 100:.1f}%"
            )
            
            # Enable shared memory if requested
            if self.enable_shared_memory:
                self._setup_shared_memory()
                
            # Start monitoring if enabled
            if self.enable_monitoring:
                self._log_memory_usage()
        else:
            logger.warning("CUDA not available, GPU Memory Manager will operate in limited mode")
    
    def get_memory_stats(self) -> Dict[str, float]:
        """
        Get current memory statistics.
        
        Returns:
            Dictionary containing memory statistics in MB
        """
        if not self.has_cuda:
            return {
                "total_vram_mb": 0,
                "allocated_vram_mb": 0,
                "reserved_vram_mb": 0,
                "free_vram_mb": 0,
                "percent_used": 0.0,
                "percent_reserved": 0.0
            }
        
        device = torch.cuda.current_device()
        total_memory = torch.cuda.get_device_properties(device).total_memory / (1024 ** 2)
        allocated_memory = torch.cuda.memory_allocated(device) / (1024 ** 2)
        reserved_memory = torch.cuda.memory_reserved(device) / (1024 ** 2)
        
        return {
            "total_vram_mb": total_memory,
            "allocated_vram_mb": allocated_memory,
            "reserved_vram_mb": reserved_memory,
            "free_vram_mb": total_memory - allocated_memory,
            "percent_used": (allocated_memory / total_memory) * 100 if total_memory > 0 else 0,
            "percent_reserved": (reserved_memory / total_memory) * 100 if total_memory > 0 else 0
        }
    
    def is_memory_available(self, requested_mb: float, buffer_percent: float = 5.0) -> bool:
        """
        Check if the requested amount of memory is available.
        
        Args:
            requested_mb: Requested memory in MB
            buffer_percent: Additional buffer percentage to keep free
            
        Returns:
            Boolean indicating if memory is available
        """
        if not self.has_cuda:
            return False
        
        stats = self.get_memory_stats()
        total_mb = stats["total_vram_mb"]
        allocated_mb = stats["allocated_vram_mb"]
        
        # Calculate target limit with buffer
        effective_target = self.vram_target_usage * (1.0 - buffer_percent / 100.0)
        target_limit_mb = total_mb * effective_target
        
        # Check if we have enough memory available
        available_mb = target_limit_mb - allocated_mb
        
        return available_mb >= requested_mb
    
    def defragment_memory(self) -> float:
        """
        Attempt to defragment GPU memory by forcing cache clearing.
        
        Returns:
            Amount of memory freed in MB
        """
        if not self.has_cuda:
            return 0.0
        
        before_stats = self.get_memory_stats()
        
        # Force garbage collection
        gc.collect()
        
        # Clear CUDA cache
        torch.cuda.empty_cache()
        
        # Log memory stats after defragmentation
        after_stats = self.get_memory_stats()
        memory_freed = before_stats["allocated_vram_mb"] - after_stats["allocated_vram_mb"]
        
        if memory_freed > 1.0:  # Only log if significant amount freed
            logger.info(f"Memory defragmentation freed {memory_freed:.2f}MB of VRAM")
        
        return memory_freed
    
    def _setup_shared_memory(self) -> None:
        """Configure CUDA for shared memory optimizations."""
        if not self.has_cuda:
            return
        
        try:
            # Enable peer access if multiple GPUs are available
            if torch.cuda.device_count() > 1:
                for i in range(torch.cuda.device_count()):
                    for j in range(torch.cuda.device_count()):
                        if i != j:
                            if torch.cuda.can_device_access_peer(i, j):
                                torch.cuda.device(i).enable_peer_access(j)
                                logger.info(f"Enabled peer access between GPU {i} and {j}")
            
            # Set memory allocation strategy for better shared memory efficiency
            if hasattr(torch.cuda, 'set_allocator_settings'):
                # Modern PyTorch API
                torch.cuda.set_allocator_settings(
                    "expandable_segments:True,max_split_size_mb:512"
                )
            
            logger.info("Configured CUDA for shared memory optimizations")
        except Exception as e:
            logger.warning(f"Failed to configure shared memory optimizations: {str(e)}")
    
    def _log_memory_usage(self) -> None:
        """Log current memory usage statistics."""
        if not self.enable_monitoring or not self.has_cuda:
            return
        
        # Get current time
        current_time = time.time()
        elapsed = current_time - self.start_time
        
        # Only log at the specified interval
        if current_time - self.last_log_time < self.log_interval:
            return
        
        # Get memory stats
        stats = self.get_memory_stats()
        
        # Add to memory log
        log_entry = {
            "timestamp": current_time,
            "elapsed_seconds": elapsed,
            "total_vram_mb": stats["total_vram_mb"],
            "allocated_vram_mb": stats["allocated_vram_mb"],
            "reserved_vram_mb": stats["reserved_vram_mb"],
            "percent_used": stats["percent_used"],
            "percent_reserved": stats["percent_reserved"]
        }
        
        self.memory_log.append(log_entry)
        
        # Write to CSV if we have a log file
        if self.log_file:
            with open(self.log_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    log_entry["timestamp"],
                    log_entry["elapsed_seconds"],
                    log_entry["total_vram_mb"],
                    log_entry["allocated_vram_mb"],
                    log_entry["reserved_vram_mb"],
                    log_entry["percent_used"],
                    log_entry["percent_reserved"]
                ])
        
        # Update last log time
        self.last_log_time = current_time
    
    def get_memory_log(self) -> List[Dict[str, float]]:
        """
        Get the collected memory usage log.
        
        Returns:
            List of memory usage log entries
        """
        return self.memory_log
    
    def cleanup(self) -> None:
        """Clean up resources and flush logs."""
        if self.has_cuda:
            # Force cache clearing
            self.defragment_memory()
            
            # Final memory logging
            if self.enable_monitoring:
                self._log_memory_usage()
        
        logger.info("GPU Memory Manager cleanup completed")

def tensor_size_mb(tensor: torch.Tensor) -> float:
    """
    Calculate the memory size of a tensor in MB.
    
    Args:
        tensor: PyTorch tensor
        
    Returns:
        Size in megabytes
    """
    return tensor.element_size() * tensor.numel() / (1024 * 1024)

def estimate_matmul_memory(a: torch.Tensor, b: torch.Tensor) -> float:
    """
    Estimate the peak memory for torch.matmul(a, b) in MB.
    
    Args:
        a: First tensor
        b: Second tensor
        
    Returns:
        Estimated peak memory in MB
    """
    if not (a.dim() == 2 and b.dim() == 2):
        # For simplicity, only handle 2D tensors
        return 0.0
    
    # Output tensor size
    output_elements = a.size(0) * b.size(1)
    output_size_mb = output_elements * a.element_size() / (1024 * 1024)
    
    # Intermediate memory for computation (depends on implementation)
    # This is a rough estimate and may vary
    intermediate_size_mb = output_size_mb * 0.5
    
    # Total peak memory: input tensors + output + intermediate
    input_size_mb = tensor_size_mb(a) + tensor_size_mb(b)
    peak_memory_mb = input_size_mb + output_size_mb + intermediate_size_mb
    
    return peak_memory_mb

def allocate_max_tensor(
    shape: Tuple[int, ...] = None,
    dtype: torch.dtype = torch.float32,
    target_usage: float = 0.8,
    device: torch.device = None
) -> Optional[torch.Tensor]:
    """
    Allocate the largest possible tensor with the given shape pattern.
    
    Args:
        shape: Base shape pattern (first dimension will be adjusted)
        dtype: Tensor data type
        target_usage: Target VRAM usage as fraction of available
        device: Target device
        
    Returns:
        Tensor of maximum size that fits in memory, or None if allocation failed
    """
    if not torch.cuda.is_available():
        return None
    
    if device is None:
        device = torch.device("cuda")
    
    if shape is None:
        shape = (1000, 1000)  # Default square matrix
    
    # Get current memory stats
    free_bytes = torch.cuda.get_device_properties(device).total_memory - torch.cuda.memory_allocated(device)
    target_bytes = int(free_bytes * target_usage)
    
    # Calculate bytes per element
    element_size = torch.empty(1, dtype=dtype).element_size()
    
    # Calculate the shape multiplier
    total_elements = 1
    for dim in shape[1:]:
        total_elements *= dim
    
    # Calculate maximum first dimension
    max_first_dim = target_bytes // (total_elements * element_size)
    
    if max_first_dim <= 0:
        logger.warning("Not enough memory to allocate tensor")
        return None
    
    try:
        # Create tensor with adjusted first dimension
        adjusted_shape = (max_first_dim,) + shape[1:]
        tensor = torch.empty(adjusted_shape, dtype=dtype, device=device)
        logger.info(f"Allocated tensor with shape {adjusted_shape}, "
                  f"size: {tensor_size_mb(tensor):.2f}MB")
        
        return tensor
    except RuntimeError as e:
        logger.warning(f"Failed to allocate tensor: {e}")
        return None
