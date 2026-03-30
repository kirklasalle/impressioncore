# ImpressionCore Tokenization Guide

This guide provides comprehensive information about the tokenization system in ImpressionCore, including its components, usage patterns, and best practices.

## Introduction to Tokenization

Tokenization is the process of converting raw content (such as text or images) into discrete tokens that can be processed by neural network models. In ImpressionCore, tokenization is a fundamental component that enables both text and image processing in a unified framework.

### Why Tokenization Matters

- **Model Input Preparation**: Transformers and other neural networks require discrete token inputs
- **Vocabulary Management**: Control over the size and composition of your model's vocabulary
- **Multimodal Processing**: Consistent handling of different content types (text, images, etc.)
- **Compression**: Efficient representation of content for memory-constrained environments

## System Architecture

The ImpressionCore tokenization system consists of several key components:

1. **Tokenizers**: Implementations for different modalities (text, images)
2. **Integration Layer**: Components for working with the Modal Engine
3. **Configuration System**: Settings and parameters for tokenizer behavior
4. **Training Framework**: Tools for training custom tokenizers
5. **Utility Tools**: Command-line tools for working with tokenized content

## Text Tokenization

### BPETokenizer

ImpressionCore implements a simplified Byte-Pair Encoding (BPE) tokenizer for text processing. BPE is a subword tokenization algorithm that starts with character-level tokens and iteratively merges the most frequent adjacent pairs.

#### Basic Usage

```python
from impressioncore.src.tokenization import get_tokenizer

# Load a text tokenizer
tokenizer = get_tokenizer("text", "data/tokenizer/text_tokenizer.json")

# Encode text to tokens
text = "ImpressionCore is a multimodal AI framework"
token_ids = tokenizer.encode(text)
print(f"Encoded to {len(token_ids)} tokens: {token_ids}")

# Decode tokens back to text
decoded_text = tokenizer.decode(token_ids)
print(f"Decoded: {decoded_text}")
```

#### Special Tokens

The text tokenizer supports special tokens for various tasks:

- `<unk>`: Unknown token (ID: 0)
- `<pad>`: Padding token (ID: 1)
- `<bos>`: Beginning of sequence token (ID: 2)
- `<eos>`: End of sequence token (ID: 3)
- `<mask>`: Mask token for masked language modeling (ID: 4)

To add special tokens to your encoding:

```python
# Add BOS and EOS tokens
token_ids = tokenizer.encode(text, add_special_tokens=True)

# Skip special tokens during decoding
decoded_text = tokenizer.decode(token_ids, skip_special_tokens=True)
```

#### Training Text Tokenizers

To train a custom text tokenizer:

```bash
python -m training.train_tokenizer --type text --text-corpus path/to/corpus --vocab-size 50000
```

The training process will:

1. Process the corpus to identify frequent patterns
2. Create a vocabulary based on character-level tokens
3. Save the tokenizer to the specified location

## Image Tokenization

### ImageTokenizer

ImpressionCore includes a patch-based vector quantization tokenizer for images. This approach divides images into patches and maps each patch to the closest entry in a learned codebook.

#### Basic Usage

```python
from impressioncore.src.tokenization import get_tokenizer
import torch
from PIL import Image
import numpy as np

# Load an image tokenizer
tokenizer = get_tokenizer("image", "data/tokenizer/image_tokenizer.pt")

# Load and prepare an image
image = Image.open("example.png").convert("RGB")
image = image.resize((tokenizer.image_size, tokenizer.image_size))
img_tensor = torch.from_numpy(np.array(image)).permute(2, 0, 1).float() / 255.0

# Encode image to tokens
token_ids = tokenizer.encode(img_tensor)
print(f"Encoded to {len(token_ids)} tokens")

# Decode tokens back to image
reconstructed = tokenizer.decode(token_ids)
reconstructed_array = (reconstructed.permute(1, 2, 0).numpy() * 255).astype(np.uint8)
reconstructed_image = Image.fromarray(reconstructed_array)
reconstructed_image.save("reconstructed.png")
```

#### Image Tokenizer Architecture

The image tokenizer consists of:

- **Patch Extraction**: Dividing images into fixed-size patches
- **Vector Quantization**: Mapping patches to the nearest codebook entry
- **Codebook**: Learned representation of visual patterns

Key parameters:

- `image_size`: Input image dimensions (defaults to 256×256)
- `patch_size`: Size of image patches (defaults to 16×16)
- `num_tokens`: Codebook size (defaults to 8192)

#### Training Image Tokenizers

To train a custom image tokenizer:

```bash
python -m training.train_tokenizer --type image --image-dir path/to/images --num-tokens 16384
```

The training process will:

1. Process a set of images to extract patches
2. Learn a codebook using clustering techniques
3. Save the tokenizer to the specified location

## Working with Tokenized Content

### Saving and Loading Token IDs

You can save tokenized content to various formats:

```python
from impressioncore.src.tokenization.converter import save_token_ids, load_token_ids

# Tokenize content
token_ids = tokenizer.encode("Example content")

# Save to different formats
save_token_ids(token_ids, "tokens.json")  # JSON format
save_token_ids(token_ids, "tokens.npy")   # NumPy format
save_token_ids(token_ids, "tokens.pt")    # PyTorch format
save_token_ids(token_ids, "tokens.txt")   # Text format

# Load from a file
loaded_tokens = load_token_ids("tokens.json")
```

### Token Analysis

Analyze tokenized content to understand patterns:

```python
from collections import Counter

# Analyze token distribution
token_counts = Counter(token_ids)
print(f"Unique tokens: {len(token_counts)}")
print(f"Most common: {token_counts.most_common(5)}")

# Calculate statistics
token_entropy = -sum((count/len(token_ids)) * math.log2(count/len(token_ids)) 
                    for count in token_counts.values())
print(f"Token entropy: {token_entropy:.2f} bits")
```

Or use the provided utility:

```bash
python -m impressioncore.view_tokens tokens.json --stats --visualize --output stats.png
```

## Advanced Tokenization Features

### Multimodal Tokenization

Process multiple modalities with a unified approach:

```python
from impressioncore.src.core.modal_engine import ModalEngine, ModalityType

# Initialize engine
engine = ModalEngine()

# Register tokenizers
engine.register_tokenizer(ModalityType.TEXT, text_tokenizer)
engine.register_tokenizer(ModalityType.IMAGE, image_tokenizer)

# Process different content types
text_tokens = engine.tokenize("Example text", ModalityType.TEXT)
image_tokens = engine.tokenize(image_tensor, ModalityType.IMAGE)
```

### Memory-Efficient Processing

For systems with limited memory, use the LiteModalEngine:

```python
from impressioncore.src.core.lite_modal_engine import LiteModalEngine

# Create engine optimized for low memory environments
engine = LiteModalEngine(chunk_size=64)

# Register tokenizers as before
# ...

# Process in memory-efficient chunks
tokens = engine.tokenize(content, modality)
```

### Custom Tokenizer Development

Create custom tokenizers by implementing a minimal interface:

```python
class CustomTokenizer:
    def encode(self, content):
        # Implementation for encoding
        return token_ids
        
    def decode(self, token_ids):
        # Implementation for decoding
        return content
```

## Command-Line Interface

ImpressionCore provides several command-line tools for working with tokenized content:

### Tokenize Content

```bash
# Tokenize text file
python -m impressioncore.tokenize_utility tokenize-text input.txt tokens.json

# Tokenize image file
python -m impressioncore.tokenize_utility tokenize-image input.png tokens.json
```

### Convert Token Formats

```bash
# Convert between token formats
python -m impressioncore.token_converter_tool tokens.json tokens.pt
```

### View and Analyze Tokens

```bash
# Analyze token distribution
python -m impressioncore.view_tokens tokens.json --stats --visualize
```

### Train Custom Tokenizers

```bash
# Train a text tokenizer
python -m training.train_tokenizer --type text --text-corpus data/corpus

# Train an image tokenizer
python -m training.train_tokenizer --type image --image-dir data/images
```

## Best Practices

### Text Tokenization

1. **Corpus Selection**: Use a representative corpus for training tokenizers
2. **Vocabulary Size**: Balance between 10,000-100,000 tokens for most applications
3. **Special Tokens**: Define application-specific special tokens as needed
4. **Unicode Support**: Ensure your tokenizer handles all necessary languages and symbols
5. **Normalization**: Apply consistent text normalization before tokenization

### Image Tokenization

1. **Resolution**: Train on images with consistent resolution
2. **Patch Size**: 16×16 works well for most applications; adjust based on detail requirements
3. **Codebook Size**: 8,192 to 16,384 tokens balances quality and memory usage
4. **Data Augmentation**: Use diverse images during training for robust tokenization
5. **Performance**: Monitor quantization quality using metrics like PSNR

## Troubleshooting

### Common Issues

1. **Out of Memory Errors**: Use the LiteModalEngine with appropriate chunk sizes
2. **Slow Tokenization**: Use batch processing for large datasets
3. **Reconstruction Quality**: Train with more diverse data or increase codebook size
4. **Tokenizer Loading Errors**: Ensure correct paths and formats for saved tokenizers
5. **Unknown Token Issues**: Check preprocessing and normalization for unexpected content

### Debugging Tools

```bash
# Test tokenizers
python -m examples.test_tokenizers --text-tokenizer path/to/tokenizer.json

# Analyze tokenizer performance
python -m examples.tokenizer_analysis --text-tokenizer path/to/tokenizer.json
```

## References

- [Tokenizers Documentation](https://huggingface.co/docs/tokenizers)
- [Vector Quantization](https://en.wikipedia.org/wiki/Vector_quantization)
- [BPE Algorithm](https://huggingface.co/docs/transformers/tokenizer_summary#bytepairtokenizer)
- [ImpressionCore Tokenization API](../impressioncore/src/tokenization/README.md)
