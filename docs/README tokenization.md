# ImpressionCore Tokenization System

The ImpressionCore tokenization system enables multimodal content processing by converting text and images into discrete token representations for use with transformer-based models.

## Overview

This system includes:

- Text tokenizers with byte-pair encoding
- Image tokenizers with patch-based vector quantization
- Memory-efficient processing for hardware with limited VRAM (e.g., GTX 1050 Ti)
- Integration with the ImpressionCore modal engine
- Command-line tools for working with tokenized content
- Comprehensive documentation and examples

## Components

### Core Components

- `BPETokenizer`: Text tokenizer with byte-pair encoding
- `ImageTokenizer`: Image tokenizer with vector quantization
- `TokenizationProcessor`: Integration layer for modal engines
- `LiteModalEngine`: Memory-efficient modal engine for tokenization and generation

### Tools and Utilities

- `token_converter_tool.py`: Convert between token file formats
- `tokenize_utility.py`: Tokenize and detokenize content
- `view_tokens.py`: Analyze tokenized content
- `validate_tokenizers.py`: Validate tokenizer functionality
- `train_tokenizer.py`: Train custom tokenizers

## Getting Started

### Installation

The tokenization system is included with ImpressionCore. Ensure you have the required dependencies:

```bash
pip install torch numpy pillow
```

### Training Tokenizers

Train text and image tokenizers with:

```bash
# Train a text tokenizer
python -m training.train_tokenizer --type text --text-corpus data/text_corpus

# Train an image tokenizer
python -m training.train_tokenizer --type image --image-dir data/image_dataset
```

### Using Tokenizers

```python
from impressioncore.src.tokenization import get_tokenizer

# Load tokenizers
text_tokenizer = get_tokenizer("text", "data/tokenizer/text_tokenizer.json")
image_tokenizer = get_tokenizer("image", "data/tokenizer/image_tokenizer.pt")

# Text tokenization
text = "Hello, world!"
token_ids = text_tokenizer.encode(text)
decoded_text = text_tokenizer.decode(token_ids)

# Image tokenization (with a torch tensor image)
token_ids = image_tokenizer.encode(image_tensor)
reconstructed = image_tokenizer.decode(token_ids)
```

### Memory-Efficient Processing

For systems with limited VRAM:

```python
from impressioncore.src.core.lite_modal_engine import LiteModalEngine
from impressioncore.src.core.config.lite_engine_config import get_config_for_device

# Create engine optimized for your GPU
engine = LiteModalEngine()
config = get_config_for_device()  # Auto-detects VRAM
engine.chunk_size = config["chunk_size"]
```

## Documentation

- [Tokenization Guide](../tokenization_guide.md): Comprehensive guide to tokenization
- [Memory-Efficient Tokenization](../memory_efficient_tokenization.md): Optimizing for limited hardware
- [Modal Engine Integration](../modal_engine_tokenizer_integration.md): Using tokenizers with the modal engine
- [Token Converter Guide](../token_converter_guide.md): Working with token formats

## Examples

- `examples/test_tokenizers.py`: Basic tokenizer testing
- `examples/test_tokenizers_example.py`: Comprehensive tokenizer examples
- `examples/tokenizer_integration_example.py`: Modal engine integration examples
- `examples/tokenization_demo.py`: Full demo of tokenization capabilities
- `examples/tokenizer_analysis.py`: Analyze tokenizer performance
- `examples/tokenizer_training_example.py`: Custom training configurations

## Command-Line Tools

```bash
# Test tokenizers
python -m examples.test_tokenizers --text --image

# Convert token formats
python -m impressioncore.token_converter_tool tokens.json tokens.pt

# Tokenize content
python -m impressioncore.tokenize_utility tokenize-text input.txt tokens.json

# View tokenized content
python -m impressioncore.view_tokens tokens.json --stats --visualize
```
