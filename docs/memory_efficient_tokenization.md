# Memory-Efficient Tokenization in ImpressionCore

This guide provides detailed strategies and techniques for efficiently tokenizing and processing content on systems with limited hardware resources, particularly focusing on devices with constrained VRAM like the NVIDIA GTX 1050 Ti (4GB).

## Understanding Memory Constraints

### Common Memory Bottlenecks

Tokenization and model inference can encounter several memory bottlenecks:

1. **Large Batch Sizes**: Processing too many samples simultaneously
2. **High Resolution Images**: Large images consume significant VRAM
3. **Context Length**: Long sequences of tokens require more memory
4. **Model Size**: Parameters and activations occupy VRAM
5. **Inefficient Memory Usage**: Poor memory management leading to fragmentation

### Memory Usage in Tokenization

During tokenization, memory is primarily used for:

- **Input Content**: Raw text or images to be tokenized
- **Tokenizer Data**: Vocabulary, codebook, or other mapping data
- **Intermediate Representations**: Temporary data during processing
- **Output Tokens**: The resulting tokenized representations
- **Runtime Overhead**: Libraries like PyTorch and CUDA have memory overhead

## LiteModalEngine Architecture

ImpressionCore provides the `LiteModalEngine` specifically designed for memory-constrained environments.

### Key Features

1. **Chunked Processing**: Break large inputs into manageable pieces
2. **Dynamic Memory Management**: Automatic memory optimization based on device capabilities
3. **Configurable Parameters**: Adjust chunk size and other settings based on available VRAM
4. **Transparent API**: Same interface as the standard engine with memory optimization behind the scenes

### Implementation Details

```python
from impressioncore.src.core.lite_modal_engine import LiteModalEngine
from impressioncore.src.core.config.lite_engine_config import get_config_for_device
from impressioncore.src.core.modal_engine import ModalityType

# Create a memory-efficient engine
engine = LiteModalEngine()

# Configure based on device capabilities
config = get_config_for_device()  # Auto-detects VRAM
engine.chunk_size = config["chunk_size"]  # Sets appropriate chunk size
engine.memory_tracking = True  # Enables memory usage monitoring

# Register tokenizers
engine.register_tokenizer(ModalityType.TEXT, text_tokenizer)
engine.register_tokenizer(ModalityType.IMAGE, image_tokenizer)

# Process content memory-efficiently
token_ids = engine.tokenize(content, ModalityType.TEXT)
```

### Memory Optimization Parameters

| Parameter | Description | Default | Low Memory |
|-----------|-------------|---------|------------|
| `chunk_size` | Number of tokens to process at once | 128 | 32-64 |
| `max_context_size` | Maximum context window size | 2048 | 512-1024 |
| `use_chunking` | Enable/disable chunked processing | True | True |
| `memory_tracking` | Monitor memory usage | True | True |

## Device-Specific Optimizations

### GTX 1050 Ti (4GB VRAM)

The NVIDIA GTX 1050 Ti has 4GB VRAM, which requires specific optimizations:

```python
# GTX 1050 Ti specific configuration
engine = LiteModalEngine(chunk_size=64)  # Conservative chunk size
engine.set_device("cuda")  # Use GPU despite limited memory

# Configure based on device capabilities
from impressioncore.src.core.config.lite_engine_config import configure_engine_for_device
configure_engine_for_device(engine)  # Will detect 4GB and adjust accordingly
```

Pre-configured settings for 4GB cards:

- `chunk_size`: 64
- `max_context_size`: 1024
- Gradient checkpointing enabled
- Attention chunking enabled
- Automatic garbage collection after operations

### CPU Fallback

For extremely limited systems, CPU processing is available:

```python
# CPU-only processing
engine = LiteModalEngine(chunk_size=32)
engine.set_device("cpu")
```

## Memory-Efficient Strategies

### Text Processing Strategies

1. **Limit Context Window**: Truncate or chunk long texts

   ```python
   # Process text in chunks of 512 tokens
   max_context = 512
   for i in range(0, len(text), max_context):
       chunk = text[i:i+max_context]
       tokens = engine.tokenize(chunk, ModalityType.TEXT)
       # Process tokens...
   ```

2. **Batch Processing Control**: Process fewer examples at once

   ```python
   # Process small batches
   batch_size = 4  # Small batch size for memory efficiency
   for i in range(0, len(texts), batch_size):
       batch = texts[i:i+batch_size]
       for text in batch:
           tokens = engine.tokenize(text, ModalityType.TEXT)
           # Process tokens...
   ```

3. **Clear Cache Regularly**: Release memory after operations

   ```python
   import torch
   
   # Process content
   tokens = engine.tokenize(content, ModalityType.TEXT)
   
   # Clear cache to free up memory
   torch.cuda.empty_cache()
   ```

### Image Processing Strategies

1. **Resize Images**: Process at lower resolution when possible

   ```python
   from PIL import Image
   import torch
   import numpy as np
   
   # Load and downsample image
   image = Image.open("large_image.png")
   image = image.resize((256, 256))  # Smaller size for memory efficiency
   img_tensor = torch.from_numpy(np.array(image)).permute(2, 0, 1).float() / 255.0
   
   tokens = engine.tokenize(img_tensor, ModalityType.IMAGE)
   ```

2. **Tile Processing**: Process large images in tiles

   ```python
   def process_image_in_tiles(image, tile_size=256, overlap=32):
       """Process a large image in overlapping tiles."""
       width, height = image.size
       all_tokens = []
       
       for y in range(0, height, tile_size - overlap):
           for x in range(0, width, tile_size - overlap):
               # Extract tile
               tile = image.crop((x, y, min(x + tile_size, width), min(y + tile_size, height)))
               tile = tile.resize((256, 256))  # Resize to tokenizer's expected size
               
               # Convert to tensor and tokenize
               tile_tensor = torch.from_numpy(np.array(tile)).permute(2, 0, 1).float() / 255.0
               tile_tokens = engine.tokenize(tile_tensor, ModalityType.IMAGE)
               all_tokens.append(tile_tokens)
               
               # Clear cache after each tile
               torch.cuda.empty_cache()
               
       return all_tokens
   ```

3. **Increase Patch Size**: Use larger patches for memory savings at some quality cost

   ```python
   # Create a tokenizer with larger patch size (reduced memory usage)
   from impressioncore.src.tokenization.image_tokenizer import ImageTokenizer
   
   efficient_tokenizer = ImageTokenizer(
       image_size=224, 
       patch_size=32,  # Larger patch size (32×32 instead of 16×16)
       num_tokens=4096 
   )
   ```

---

# Memory-Efficient Tokenization

This document outlines the memory optimization techniques implemented in the `MultimodalTokenizer` class to support efficient tokenization on low-VRAM devices, such as the NVIDIA GTX 1050 Ti.

## Enhancements

### 1. CPU Offloading

- **Description:**
  - The `MultimodalTokenizer` now supports dynamic CPU offloading for text and image tokenization.
  - Tensors are offloaded to the CPU to free up GPU memory, enabling larger batch sizes and more complex operations.

- **Implementation:**
  - A `CPUOffloader` utility class manages the offloading and retrieval of tensors.
  - Offloading is optional and can be enabled during the initialization of the tokenizer.

- **Usage Example:**

  ```python
  tokenizer = MultimodalTokenizer(
      text_tokenizer_name="gpt2",
      enable_cpu_offloading=True
  )
  
  # Tokenize text with CPU offloading
  encodings = tokenizer.tokenize_text("Example text")
  ```

### 2. Caching Mechanism

- **Description:**
  - Frequently tokenized content is cached to avoid redundant computations.
  - Both text and image tokenization results are stored in memory for quick retrieval.

- **Usage Example:**

  ```python
  # Tokenize text and cache the result
  encodings = tokenizer.tokenize_text("Cached text")
  
  # Retrieve from cache
  cached_encodings = tokenizer.tokenize_text("Cached text")
  ```

### 3. Batched Tokenization

- **Description:**
  - Added support for batched tokenization of text inputs to improve throughput.

- **Usage Example:**

  ```python
  # Tokenize a batch of text inputs
  batch_encodings = tokenizer.batch_tokenize_text(["Text 1", "Text 2", "Text 3"])
  ```

## Benefits

- Reduces GPU memory usage by offloading tensors to the CPU.
- Improves performance for repeated tokenization tasks through caching.
- Enables efficient processing of large batches of text inputs.

## Future Work

- Extend CPU offloading to support additional modalities.
- Optimize the caching mechanism for distributed environments.
- Implement adaptive memory management based on real-time GPU usage.

---

## Dynamic Memory Management

The dynamic memory management system in ImpressionCore optimizes resource usage by:

1. **Dynamic Allocation:**
   - Automatically moves tensors between CPU and GPU based on available VRAM.
   - Ensures efficient utilization of limited GPU memory.

2. **Dynamic Deallocation:**
   - Clears unused memory to prevent fragmentation and optimize performance.

### Key Features

- **Dynamic Memory Allocation:**
  - Moves tensors to GPU if sufficient VRAM is available.
  - Falls back to CPU when VRAM is insufficient.

- **Dynamic Memory Deallocation:**
  - Uses garbage collection and clears GPU memory cache to free up resources.

### Usage Example

```python
from src.utils.memory_optimization import dynamic_memory_allocation, dynamic_memory_deallocation

# Allocate memory dynamically
tensor = torch.randn(100, 100)
allocated_tensor = dynamic_memory_allocation(tensor)

# Deallocate unused memory
dynamic_memory_deallocation()
```

### Benefits

- Reduces the risk of out-of-memory (OOM) errors.
- Improves performance on devices with limited VRAM, such as the NVIDIA GTX 1050 Ti.

For more details, refer to the [Memory Optimization Utilities](../src/utils/memory_optimization.py).
