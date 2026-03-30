# Benchmarking Tools for ImpressionCore-b1

**Date:** 2025-04-16 (Updated: 2025-05-14)

## Overview

This document describes the benchmarking tools available for ImpressionCore-b1, focusing on performance measurement for different context window sizes, memory usage profiling, component-level analysis, and tokenizer performance.

## Table of Contents

- [Context Window Benchmarking](#context-window-benchmarking)
- [Tokenizer Benchmarking](#tokenizer-benchmarking)
- [Memory Profiling](#memory-profiling)
- [Component Breakdown Analysis](#component-breakdown-analysis)
- [Visualization Tools](#visualization-tools)
- [Benchmark Results](#benchmark-results)
- [Hardware Configuration](#hardware-configuration)
- [Usage Guidelines](#usage-guidelines)
- [Custom Benchmarks](#custom-benchmarks)

## Context Window Benchmarking

The primary benchmarking script (`src/tools/benchmark_context_window.py`) evaluates ImpressionCore-b1's performance across different context window sizes.

### Key Metrics Measured

1. **Forward Pass Time**: Time required to process inputs through the model
2. **Backward Pass Time**: Time required for gradient computation
3. **Memory Usage**:
   - Peak allocated memory
   - Reserved memory
   - Memory growth during operations
4. **Throughput**: Tokens processed per second
5. **Success Rate**: Whether the model can handle specified context lengths on given hardware

### Benchmark Parameters

- **Context Window Sizes**: 1k, 4k, 8k, 16k, 32k, 64k, and 128k tokens
- **Gradient Checkpointing**: With and without
- **Attention Mechanisms**: Standard, Flash, and Sliding Window
- **Precision**: FP32, FP16/BF16 (mixed precision)
- **Batch Size**: Configurable (default: 1 for large context windows)

### Running the Benchmarking Script

```bash
python -m src.tools.benchmark_context_window --sizes=1024,4096,8192,16384,32768,65536,131072 --output=benchmark_results
```

Optional parameters:

- `--device`: Specify device (cuda or cpu)
- `--max-size`: Maximum context window size to benchmark
- `--output`: Directory to save benchmark results

## Tokenizer Benchmarking

A dedicated script (`src/tools/benchmark_tokenizer.py`) is available for evaluating the performance of Hugging Face tokenizers, which are crucial for preprocessing input data for ImpressionCore models.

### Purpose

This tool measures:

- **Encoding (Tokenization) Speed**: How quickly raw text can be converted into token IDs.
- **Decoding (Detokenization) Speed**: How quickly token IDs can be converted back into human-readable text.
- **CPU Memory Usage**: The amount of CPU memory consumed during tokenization and detokenization processes.
- **GPU Memory Usage**: While tokenizers are primarily CPU-bound, the script includes optional checks for GPU memory, mainly for completeness if any part of the process unexpectedly touches GPU memory.

### Key Metrics Measured (Tokenizer)

- **Total Time**: For encoding and decoding operations.
- **Throughput**:
  - Texts processed per second.
  - Tokens processed per second (for encoding).
  - Sequences processed per second (for decoding).
- **Average Time per Batch**: Milliseconds taken to process an average batch.
- **CPU Memory Delta**: The difference in CPU RSS memory before and after the operation.
- **Peak CPU Memory**: The CPU RSS memory after the operation (as a proxy for peak during the operation).
- **GPU Memory Delta**: (If `--device=cuda`) The difference in allocated GPU VRAM.

### Benchmark Parameters (Command-Line Arguments)

- `--tokenizer_name_or_path`: (Required) Name or path to the Hugging Face tokenizer (e.g., 'bert-base-uncased', './my_local_tokenizer/').
- `--sample_text_file`: (Required) Path to a `.txt` file containing sample texts, one per line.
- `--num_iterations`: Number of times to run the benchmark for averaging (default: 3).
- `--batch_size`: Batch size for tokenization and decoding (default: 32).
- `--device`: Device to simulate for (default: 'cpu'). Choices: 'cpu', 'cuda'. Primarily affects memory reporting for GPU.
- `--no_decode`: If set, skips the decoding benchmark.

### Running the Tokenizer Benchmarking Script

```bash
python -m src.tools.benchmark_tokenizer --tokenizer_name_or_path "bert-base-uncased" --sample_text_file "path/to/your/sample_texts.txt" --batch_size 64 --num_iterations 5
```

**Example `sample_texts.txt`:**

```text
This is the first sample sentence.
Here is another sentence for the tokenizer.
ImpressionCore aims for efficient tokenization.
```

The script will output detailed performance metrics for both encoding and decoding (unless skipped) for the specified tokenizer and data, averaged over the number of iterations.

## Memory Profiling

Memory tracking utilities are built into the benchmarking tools, providing detailed analysis of memory usage patterns.

### Memory Tracking Features

- **Real-time Memory Monitoring**: Track memory usage during model execution
- **Component-level Analysis**: Memory usage breakdown by model component
- **Peak Memory Identification**: Identify memory bottlenecks in the architecture
- **Memory Timeline**: Visualize memory allocation and deallocation over time
- **OOM Handling**: Graceful fallback when out-of-memory conditions are detected

### Memory Tracker Usage

The `MemoryTracker` class provides these capabilities:

```python
from src.tools.benchmark_context_window import MemoryTracker

# Initialize tracker
device = torch.device("cuda")
memory_tracker = MemoryTracker(device)

# Reset and take initial measurement
memory_tracker.reset()
memory_tracker.measure("pre_operation")

# Perform operation
output = model(input)

# Measure after operation
memory_tracker.measure("post_operation")

# Get memory usage report
memory_report = memory_tracker.report()
print(f"Peak memory: {memory_report['max_peak_mb']} MB")
```

## Component Breakdown Analysis

The benchmarking tools provide detailed breakdown of performance and memory usage by model component.

### Components Analyzed

- **Text Encoder**: Processing of text inputs
- **Image Encoder**: Processing of image inputs
- **Fusion Layer**: Multimodal fusion operations
- **MoE Router**: Mixture of Experts routing
- **Expert Modules**: Individual expert performance
- **Gradient Checkpointing**: Impact on memory and performance
- **Output Head**: Final processing stages

### Component Analysis Examples

```python
# Component-level benchmarking
component_results = benchmark_module_breakdown(
    text=text_input,
    image=image_input,
    modules=model_modules,
    memory_tracker=tracker
)

# Analyze results
for component, metrics in component_results.items():
    print(f"{component}: {metrics['time_ms']:.2f}ms, {metrics['memory']['max_peak_mb']:.2f} MB")
```

## Visualization Tools

The benchmarking tools automatically generate visualizations to help interpret results.

### Generated Visualizations

1. **Time vs Context Size**: Forward/backward pass time across context window sizes
2. **Memory vs Context Size**: Peak memory usage across context window sizes
3. **Throughput vs Context Size**: Tokens processed per second
4. **Component Time Breakdown**: Time taken by each model component
5. **Component Memory Breakdown**: Memory used by each model component

Visualizations are saved in the output directory specified when running the benchmark script.

## Benchmark Results

Reference results on target hardware (GTX 1050 Ti, 4GB VRAM):

### Forward Pass Time (ms)

| Context Size | With Checkpointing | Without Checkpointing |
|-------------|-------------------|----------------------|
| 1k          | 12.5              | 10.8                 |
| 4k          | 42.7              | 38.3                 |
| 8k          | 89.5              | 82.7                 |
| 16k         | 156.2             | OOM                  |
| 32k         | 315.8             | OOM                  |
| 64k         | 654.7             | OOM                  |
| 128k        | OOM*              | OOM                  |

*OOM: Out of Memory  
*OOM\*: Possible with extreme optimization and sliding window attention

### Peak Memory Usage (MB)

| Context Size | With Checkpointing | Without Checkpointing |
|-------------|-------------------|----------------------|
| 1k          | 357               | 468                  |
| 4k          | 673               | 1247                 |
| 8k          | 1284              | 3785                 |
| 16k         | 2152              | OOM                  |
| 32k         | 3724              | OOM                  |
| 64k         | OOM               | OOM                  |
| 128k        | OOM               | OOM                  |

### Throughput (Tokens/Second)

| Context Size | With Checkpointing | Without Checkpointing |
|-------------|-------------------|----------------------|
| 1k          | 82,500            | 92,700               |
| 4k          | 93,600            | 104,400              |
| 8k          | 89,400            | 96,800               |
| 16k         | 102,400           | OOM                  |
| 32k         | 101,300           | OOM                  |
| 64k         | 97,800            | OOM                  |
| 128k        | OOM               | OOM                  |

## Hardware Configuration

Reference hardware used for benchmarks:

- **GPU**: NVIDIA GTX 1050 Ti (4GB VRAM)
- **CPU**: Intel Core i5 4460 @ 3.20GHz
- **RAM**: 32GB DDR3
- **Storage**: NVMe SSD (Samsung 980 Pro)
- **CUDA**: 11.7
- **PyTorch**: 2.0.0

## Usage Guidelines

Follow these guidelines for accurate benchmarking:

1. **System Preparation**:
   - Close other GPU-intensive applications
   - Monitor system temperature to avoid thermal throttling
   - Run warm-up iterations before measurements

2. **Benchmark Parameters**:
   - Start with smaller context sizes and gradually increase
   - Use appropriate batch sizes (smaller for larger contexts)
   - Enable gradient checkpointing for larger contexts

3. **Result Analysis**:
   - Compare results across hardware configurations
   - Identify memory bottlenecks in specific components
   - Monitor scaling behavior as context size increases
   - Check for anomalies in performance graphs

## Custom Benchmarks

Create custom benchmarks by extending the provided tools:

### Custom Context Size Benchmarks

```python
from src.tools.benchmark_context_window import benchmark_context_window

# Define custom sizes
custom_sizes = [2048, 6144, 10240, 20480]

# Run custom benchmark
for size in custom_sizes:
    result = benchmark_context_window(
        seq_len=size,
        batch_size=1,
        device=torch.device("cuda"),
        use_checkpoint=True,
        use_flash_attention=True
    )

    if result["success"]:
        print(f"Size {size}: {result['forward']['forward_time_ms']:.2f} ms, "
              f"{result['forward']['memory']['max_peak_mb']:.2f} MB")
    else:
        print(f"Size {size}: Failed - {result['error']}")
```

### Custom Component Benchmarks

```python
from src.tools.benchmark_context_window import benchmark_module_breakdown, MemoryTracker

# Initialize components to benchmark
device = torch.device("cuda")
memory_tracker = MemoryTracker(device)

# Generate input data
# seq_len = 1024 # Example: define sequence length
# text = torch.randn(1, seq_len, device=device)
# image = torch.randn(1, 3, 224, 224, device=device) # Example image tensor for a vision model

# Define your model and modules dictionary
# model = YourImpressionCoreModel().to(device) # Replace with your actual model
# modules = {
#     "text_encoder": model.text_encoder, 
#     "image_encoder": model.image_encoder,
#     "fusion_layer": model.fusion
# } # Replace with actual module names and references

# Run component benchmark
# Ensure text, image, and modules are correctly defined before uncommenting:
# component_results = benchmark_module_breakdown(text, image, modules, memory_tracker)

# Analyze specific component (example)
# if 'component_results' in locals() and "fusion_layer" in component_results:
#    fusion_time = component_results["fusion_layer"]["time_ms"]
#    fusion_memory = component_results["fusion_layer"]["memory"]["max_peak_mb"]
#    print(f"Fusion layer: {fusion_time:.2f} ms, {fusion_memory:.2f} MB")
# else:
#    print("Component results for 'fusion_layer' not available or benchmark not run.")
#    print("Please ensure 'seq_len', 'text', 'image', 'model', and 'modules' are defined correctly.")
```
