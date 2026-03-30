# Memory Optimization API Reference

### `MemoryProfiler`

```python
class MemoryProfiler:
    """
    Profile memory usage of models and operations
    """
    
    def __init__(self, enabled: bool = True):
        """
        Initialize the memory profiler
        
        Args:
            enabled: Whether profiling is enabled
        """
        
    def start_module_profile(self, name: str) -> None:
        """
        Start profiling a specific module or operation
        
        Args:
            name: Name to identify this profiling section
        """
        
    def end_module_profile(self, name: str) -> Dict[str, float]:
        """
        End profiling for a module and get statistics
        
        Args:
            name: Name of the profiling section to end
            
        Returns:
            Dictionary with memory statistics for this module
        """
        
    def module_summary(self) -> Dict[str, Dict[str, float]]:
        """
        Get memory usage summary for all profiled modules
        
        Returns:
            Dictionary mapping module names to their memory statistics
        """
        
    def visualize(self, output_path: Optional[str] = None) -> None:
        """
        Generate memory usage visualization
        
        Args:
            output_path: Path to save visualization (None for interactive display)
        """
```

Usage example:

```python
from src.utils.memory_optimization import MemoryProfiler

# Create a profiler
profiler = MemoryProfiler()

# Profile specific model components
for i, layer in enumerate(model.layers):
    profiler.start_module_profile(f"layer_{i}")
    output = layer(input_tensor)
    profiler.end_module_profile(f"layer_{i}")

# Get memory usage summary
summary = profiler.module_summary()
for module_name, stats in summary.items():
    print(f"{module_name}: {stats['peak_gb']:.2f} GB peak, {stats['duration_ms']:.1f}ms")

# Generate visualization
profiler.visualize("memory_profile.png")
```

## Low-Level Functions

### `dtype_size`

```python
def dtype_size(dtype: torch.dtype) -> int:
    """
    Get size in bytes for a given dtype
    
    Args:
        dtype: PyTorch data type
        
    Returns:
        Size in bytes
    """
```

Returns the memory size in bytes for a given PyTorch data type.

**Example usage:**

```python
from src.utils.memory_optimization import dtype_size
import torch

# Check memory requirements for different data types
print(f"FP32: {dtype_size(torch.float32)} bytes per element")
print(f"FP16: {dtype_size(torch.float16)} bytes per element")
print(f"INT8: {dtype_size(torch.int8)} bytes per element")
```

### `estimate_activation_size`

```python
def estimate_activation_size(
    model: torch.nn.Module,
    batch_size: int,
    seq_length: int,
    dtype: torch.dtype
) -> float:
    """
    Estimate activation memory requirements based on model architecture
    
    Args:
        model: PyTorch model
        batch_size: Batch size for estimation
        seq_length: Sequence length for estimation
        dtype: Data type for estimation
        
    Returns:
        Estimated activation size in bytes
    """
```

Provides a rough estimate of activation memory requirements for a given model and input dimensions.

**Example usage:**

```python
from src.utils.memory_optimization import estimate_activation_size
import torch

# Estimate activation memory for a model
activation_size = estimate_activation_size(
    model,
    batch_size=2,
    seq_length=1024,
    dtype=torch.float16
)
print(f"Estimated activation memory: {activation_size / 1e9:.2f} GB")
```

## Optimization Presets

### `optimize_for_inference`

```python
def optimize_for_inference(
    model: torch.nn.Module,
    precision: str = "float16",
    device: str = "cuda"
) -> torch.nn.Module:
    """
    Apply optimizations specific to inference scenarios
    
    Args:
        model: PyTorch model to optimize
        precision: Precision to use ("float32", "float16", "int8")
        device: Device to run inference on
        
    Returns:
        Optimized model
    """
```

Applies a preset of optimizations tailored specifically for inference scenarios.

**Example usage:**

```python
from src.utils.memory_optimization import optimize_for_inference

# Optimize model for inference
model = optimize_for_inference(model, precision="float16")

# Run inference
with torch.no_grad():
    outputs = model(inputs)
```

### `optimize_for_training`

```python
def optimize_for_training(
    model: torch.nn.Module,
    precision: str = "float16",
    gradient_accumulation_steps: int = 1
) -> torch.nn.Module:
    """
    Apply optimizations specific to training scenarios
    
    Args:
        model: PyTorch model to optimize
        precision: Precision to use ("float32", "float16", "bfloat16")
        gradient_accumulation_steps: Number of steps to accumulate gradients
        
    Returns:
        Optimized model and training configuration
    """
```

Applies a preset of optimizations tailored specifically for training scenarios.

**Example usage:**

```python
from src.utils.memory_optimization import optimize_for_training

# Optimize model for training
model, training_config = optimize_for_training(
    model, 
    precision="bfloat16",
    gradient_accumulation_steps=8
)

# Use the optimized model and configuration
optimizer = torch.optim.AdamW(
    model.parameters(),
    lr=training_config.learning_rate
)
```

## Utility Functions

### `debug_memory_usage`

```python
def debug_memory_usage(
    model: torch.nn.Module, 
    sample_input: torch.Tensor
) -> Dict[str, Any]:
    """
    Analyze model for memory bottlenecks and provide suggestions
    
    Args:
        model: PyTorch model to analyze
        sample_input: Sample input tensor
        
    Returns:
        Dictionary containing analysis results and suggestions
    """
```

Performs detailed analysis of a model to identify memory bottlenecks and suggest optimizations.

**Example usage:**

```python
from src.utils.memory_optimization import debug_memory_usage
import torch

# Create sample input
sample_input = torch.randn(1, 3, 512, 512).cuda()

# Debug memory usage
debug_results = debug_memory_usage(model, sample_input)

# Print memory bottlenecks
print("Memory bottlenecks:")
for module_name, memory_gb in debug_results["bottlenecks"]:
    print(f"- {module_name}: {memory_gb:.2f} GB")

# Print optimization suggestions
print("\nSuggested optimizations:")
for suggestion in debug_results["suggestions"]:
    print(f"- {suggestion}")
```

### `optimize_rng_state`

```python
def optimize_rng_state(seed: int = 42) -> None:
    """
    Configure random number generators for memory-efficient operations
    
    Args:
        seed: Random seed for reproducibility
    """
```

Configures random number generators for more memory-efficient operations.

**Example usage:**

```python
from src.utils.memory_optimization import optimize_rng_state

# Configure RNG for memory efficiency
optimize_rng_state(seed=42)
```

## Environment Functions

### `get_available_memory`

```python
def get_available_memory() -> Dict[str, float]:
    """
    Get available memory on current device
    
    Returns:
        Dictionary with memory statistics in GB
    """
```

Retrieves information about available memory on the current device.

**Example usage:**

```python
from src.utils.memory_optimization import get_available_memory

# Check available memory
memory_info = get_available_memory()
print(f"Total GPU memory: {memory_info['total_gb']:.2f} GB")
print(f"Available GPU memory: {memory_info['available_gb']:.2f} GB")
```

### `check_hardware_compatibility`

```python
def check_hardware_compatibility(
    min_vram: float = 4.0,
    recommended_vram: float = 8.0
) -> Dict[str, Any]:
    """
    Check if hardware is compatible with model requirements
    
    Args:
        min_vram: Minimum VRAM required in GB
        recommended_vram: Recommended VRAM in GB
        
    Returns:
        Dictionary with compatibility information
    """
```

Checks whether the current hardware meets the requirements for running ImpressionCore models.

**Example usage:**

```python
from src.utils.memory_optimization import check_hardware_compatibility

# Check if hardware is compatible
compatibility = check_hardware_compatibility()
if compatibility["is_compatible"]:
    print("Hardware is compatible for running models")
    print(f"Available VRAM: {compatibility['vram_gb']:.2f} GB")
else:
    print("Warning: Hardware may be insufficient")
    print(compatibility["recommendations"])
```

## Conclusion

This API documentation covers the key memory optimization utilities provided by ImpressionCore. By using these tools, developers can efficiently run sophisticated models on hardware with limited VRAM, such as the GTX 1050 Ti (4GB).

For more detailed implementation examples and advanced usage patterns, refer to:

- [Memory Optimization Guide](../user_guide/memory_optimization.md)
- [Model Training Guide](../user_guide/model_training.md)
- [Technical Implementation Details](../technical/memory_optimizations.md)
