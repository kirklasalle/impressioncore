# Modal Engine Tokenizer Integration Guide

This guide provides comprehensive information about integrating tokenizers with the ImpressionCore Modal Engine for multimodal processing.

## Introduction

The Modal Engine is the central component of ImpressionCore that coordinates processing across different modalities (text, images, audio, etc.). Integrating tokenizers with the Modal Engine allows for seamless tokenization and detokenization as part of a unified multimodal pipeline.

## Modal Engine Architecture

The Modal Engine provides:

1. **Modality Abstraction**: Unified interface for different content types
2. **Tokenizer Registry**: Management of tokenizers for each modality
3. **Model Registry**: Management of models for each modality
4. **Processing Pipeline**: Content flow from raw input to tokens to model processing
5. **Memory Management**: Efficient handling of resources across modalities

### Key Components

- `ModalEngine`: Standard processing engine for multimodal content
- `LiteModalEngine`: Memory-efficient version for constrained environments
- `ModalityType`: Enum defining supported modalities (TEXT, IMAGE, AUDIO, VIDEO)
- `TokenizationProcessor`: Helper class for tokenization operations

## Basic Integration

### Step 1: Import Required Components

```python
from impressioncore.src.core.modal_engine import ModalEngine, ModalityType
from impressioncore.src.tokenization import get_tokenizer
```

### Step 2: Create and Configure the Modal Engine

```python
# Create a new Modal Engine instance
engine = ModalEngine()

# Load tokenizers
text_tokenizer = get_tokenizer("text", "data/tokenizer/text_tokenizer.json")
image_tokenizer = get_tokenizer("image", "data/tokenizer/image_tokenizer.pt")

# Register tokenizers with the engine
engine.register_tokenizer(ModalityType.TEXT, text_tokenizer)
engine.register_tokenizer(ModalityType.IMAGE, image_tokenizer)
```

### Step 3: Process Content Through the Engine

```python
# Tokenize text
text = "Example text for tokenization"
text_token_ids = engine.tokenize(text, ModalityType.TEXT)

# Tokenize an image (assuming you have an image tensor)
import torch
from PIL import Image
import numpy as np

# Load and prepare the image
image = Image.open("example.png").convert("RGB")
image = image.resize((256, 256))  # Match tokenizer's expected size
img_tensor = torch.from_numpy(np.array(image)).permute(2, 0, 1).float() / 255.0

# Tokenize the image
image_token_ids = engine.tokenize(img_tensor, ModalityType.IMAGE)

# Detokenize back to original content
reconstructed_text = engine.detokenize(text_token_ids, ModalityType.TEXT)
reconstructed_image = engine.detokenize(image_token_ids, ModalityType.IMAGE)
```

## Using the TokenizationProcessor

For more advanced integration, ImpressionCore provides the `TokenizationProcessor` class:

```python
from impressioncore.src.tokenization.integration import TokenizationProcessor

# Create processor
processor = TokenizationProcessor()

# Load tokenizers (will use default paths if not specified)
processor.load_tokenizer("text", "path/to/text_tokenizer.json")
processor.load_tokenizer("image", "path/to/image_tokenizer.pt")

# Register with engine
processor.register_with_engine(engine)

# You can also use the processor directly
text_tokens = processor.tokenize("Example text", "text")
decoded_text = processor.detokenize(text_tokens, "text")
```

Benefits of using `TokenizationProcessor`:

- Automatic path resolution for tokenizers
- Consistent interface across modalities
- Simplified engine registration
- Error handling and fallbacks

## Memory-Efficient Integration

For systems with limited memory, use the `LiteModalEngine` instead:

```python
from impressioncore.src.core.lite_modal_engine import LiteModalEngine
from impressioncore.src.core.config.lite_engine_config import get_config_for_device

# Create a LiteModalEngine with appropriate configuration
engine = LiteModalEngine()
config = get_config_for_device()
engine.chunk_size = config["chunk_size"]

# Register tokenizers as with the standard engine
engine.register_tokenizer(ModalityType.TEXT, text_tokenizer)
engine.register_tokenizer(ModalityType.IMAGE, image_tokenizer)

# Set device (can use CPU fallback if needed)
engine.set_device("cuda" if torch.cuda.is_available() else "cpu")

# Process content in memory-efficient chunks
tokens = engine.tokenize(content, modality_type)
```

## Extended Examples

### Processing Multiple Modalities

```python
def process_multimodal_content(text_content, image_path, engine):
    """Process content with multiple modalities."""
    # Process text
    text_tokens = engine.tokenize(text_content, ModalityType.TEXT)
    
    # Load and process image
    image = Image.open(image_path).convert("RGB")
    image = image.resize((256, 256))
    img_tensor = torch.from_numpy(np.array(image)).permute(2, 0, 1).float() / 255.0
    image_tokens = engine.tokenize(img_tensor, ModalityType.IMAGE)
    
    # Combine tokens for multimodal model input
    # (Specific combination strategy depends on your model architecture)
    return {
        "text_tokens": text_tokens,
        "image_tokens": image_tokens
    }
```

### Using Modal Engine with Generation Models

```python
# Register models with the engine
from impressioncore.src.models import get_model

text_model = get_model("text_generation")
image_model = get_model("image_generation")

engine.register_model(ModalityType.TEXT, text_model)
engine.register_model(ModalityType.IMAGE, image_model)

# Generate content
generated_text = engine.generate("A story about", ModalityType.TEXT, max_tokens=100)
generated_image = engine.generate("A beautiful landscape", ModalityType.IMAGE, 
                                 params={"width": 512, "height": 512})
```

### Batch Processing

```python
def batch_tokenize(texts, engine, batch_size=8):
    """Tokenize a batch of texts efficiently."""
    all_tokens = []
    
    # Process in batches
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        batch_tokens = [engine.tokenize(text, ModalityType.TEXT) for text in batch]
        all_tokens.extend(batch_tokens)
        
        # Optional: clear cache between batches
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    
    return all_tokens
```

## Custom Integration Patterns

### Custom Tokenizer Registration

```python
# Create a custom tokenizer that conforms to the required interface
class CustomTokenizer:
    def __init__(self):
        self.custom_data = {}
    
    def encode(self, content):
        # Custom encoding logic
        return [1, 2, 3, 4]  # Return token IDs
    
    def decode(self, token_ids):
        # Custom decoding logic
        return "Decoded content"

# Register with the engine
custom_tokenizer = CustomTokenizer()
engine.register_tokenizer(ModalityType.CUSTOM, custom_tokenizer)
```

### Dynamic Modality Selection

```python
def process_content(content, engine):
    """Process content with automatic modality detection."""
    if isinstance(content, str):
        return engine.tokenize(content, ModalityType.TEXT)
    elif isinstance(content, torch.Tensor) and content.dim() >= 3:
        return engine.tokenize(content, ModalityType.IMAGE)
    elif isinstance(content, bytes):
        # Could be audio or other binary data
        pass
    else:
        raise ValueError(f"Unknown content type: {type(content)}")
```

## Error Handling

The Modal Engine provides several mechanisms for error handling:

```python
try:
    tokens = engine.tokenize(content, ModalityType.TEXT)
except ValueError as e:
    # Handle missing tokenizer or invalid content
    print(f"Error tokenizing content: {e}")
except RuntimeError as e:
    # Handle CUDA out of memory or other runtime issues
    print(f"Runtime error during tokenization: {e}")
    # Fall back to CPU
    engine.set_device("cpu")
    tokens = engine.tokenize(content, ModalityType.TEXT)
```

## Performance Considerations

### Memory Management

For systems with limited memory, follow these best practices:

1. Use `LiteModalEngine` instead of standard `ModalEngine`
2. Process content in smaller chunks with appropriate `chunk_size`
3. Clear CUDA cache between operations with `torch.cuda.empty_cache()`
4. Use CPU offloading for very large content

### Speed Optimization

For faster processing:

1. Batch similar modality content together
2. Pre-allocate tensors when possible
3. Use appropriate device placement (GPU for heavy computation, CPU for I/O)
4. Minimize data transfers between CPU and GPU

## Advanced Configuration

### Custom Modal Engine Configuration

```python
# Create custom configuration
engine_config = {
    "device": "cuda:0",
    "precision": "fp16",  # Use mixed precision
    "batch_size": 16,
    "max_sequence_length": 1024,
    "chunk_size": 128
}

# Configure the engine
engine = ModalEngine()
for key, value in engine_config.items():
    if hasattr(engine, key):
        setattr(engine, key, value)
```

### Environment-Specific Configuration

```python
# Configure based on environment
import os

if os.environ.get("IMPRESSIONCORE_MEMORY_EFFICIENT", "0") == "1":
    # Use memory-efficient settings
    engine = LiteModalEngine(chunk_size=32)
    engine.use_chunking = True
    engine.memory_tracking = True
else:
    # Use standard settings
    engine = ModalEngine()
```

## Conclusion

Integrating tokenizers with the Modal Engine provides a powerful and unified way to process multimodal content in ImpressionCore. The system is designed to be flexible, memory-efficient, and easy to use, making it suitable for a wide range of applications and hardware configurations.
