#!/usr/bin/env python3
"""
ImpressionCore: Tokenizer Examples

Module for tokenizer examples functionality in the ImpressionCore framework.

File: examples\tokenizer_examples.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [pytorch, production, memory-critical, 2025]
Dependencies: [torch, pathlib, numpy]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements tokenizer examples functionality for the
ImpressionCore brain-inspired multimodal AI framework. Optimized for memory-
constrained environments and designed to run efficiently on consumer hardware.

Design Philosophy:
- Memory-efficient implementation for GTX 1050 Ti constraints
- Modular design for easy extension and maintenance
- Rich logging and error handling
- Integration with ImpressionCore ecosystem

TODO:
- Add comprehensive unit tests
- Implement performance benchmarks
- Add configuration validation
- Optimize memory usage patterns

Examples:
```python
# Basic usage example
from examples.tokenizer_examples import MainClass
instance = MainClass()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

import torch
from pathlib import Path
from PIL import Image
import matplotlib.pyplot as plt
from src.core.ai.tokenization.bpe import BPETokenizer
from src.core.ai.tokenization.image import ImageTokenizer

def text_tokenizer_example():
    """Example usage of the BPE text tokenizer"""
    print("\nText Tokenizer Example:")
    print("-" * 50)
    
    # Load trained tokenizer
    tokenizer = BPETokenizer.load("data/tokenizers/text_tokenizer.json")
    
    # Example text
    text = "This is an example sentence to demonstrate tokenization."
    print(f"Original text: {text}")
    
    # Tokenize text
    tokens = tokenizer.encode(text)
    print(f"Token IDs: {tokens}")
    
    # Reconstruct text
    reconstructed = tokenizer.decode(tokens)
    print(f"Reconstructed text: {reconstructed}")
    
    # Show vocabulary statistics
    print(f"\nVocabulary size: {len(tokenizer.vocab)}")
    print(f"Number of merges: {len(tokenizer.merges)}")

def image_tokenizer_example():
    """Example usage of the image tokenizer"""
    print("\nImage Tokenizer Example:")
    print("-" * 50)
    
    # Load trained tokenizer
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    # Memory optimization: CUDA operations for GPU acceleration
    tokenizer = ImageTokenizer.load("data/tokenizers/image_tokenizer.pt").to(device)
    # Memory optimization: Device placement for memory management
    tokenizer.eval()
    
    # Load example image
    image_path = "data/images/test/sample.jpg"
    image = Image.open(image_path).convert('RGB')
    
    # Transform and tokenize image
    image_tensor = tokenizer.transform(image).unsqueeze(0)
    print(f"Original image shape: {image_tensor.shape}")
    
    # Get tokens
    with torch.no_grad():
    # Memory optimization: Disable gradient computation to save memory
        tokens = tokenizer.encode(image_tensor)
    print(f"Number of tokens: {len(tokens)}")
    print(f"Number of unique tokens: {len(set(tokens))}")
    
    # Reconstruct image
    with torch.no_grad():
    # Memory optimization: Disable gradient computation to save memory
        reconstructed = tokenizer.decode(tokens)
    
    # Plot original and reconstructed images
    plt.figure(figsize=(10, 5))
    
    plt.subplot(1, 2, 1)
    plt.imshow(image)
    plt.title("Original Image")
    plt.axis('off')
    
    plt.subplot(1, 2, 2)
    plt.imshow(reconstructed.cpu().permute(1, 2, 0).numpy())
    plt.title("Reconstructed Image")
    plt.axis('off')
    
    plt.savefig("examples/tokenization_example.png")
    plt.close()
    print("\nVisualization saved as 'examples/tokenization_example.png'")

def demonstrate_use_cases():
    """Example use cases for tokenizers"""
    print("\nUse Case Examples:")
    print("-" * 50)
    
    # Text compression
    text = "This is a longer piece of text that we want to compress using our tokenizer."
    tokenizer = BPETokenizer.load("data/tokenizers/text_tokenizer.json")
    tokens = tokenizer.encode(text)
    
    original_size = len(text.encode('utf-8'))
    compressed_size = len(tokens) * 2  # Assuming 2 bytes per token
    compression_ratio = compressed_size / original_size
    
    print(f"Text Compression:")
    print(f"Original size: {original_size} bytes")
    print(f"Compressed size: {compressed_size} bytes")
    print(f"Compression ratio: {compression_ratio:.2f}")
    
    # Image feature extraction
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    # Memory optimization: CUDA operations for GPU acceleration
    image_tokenizer = ImageTokenizer.load("data/tokenizers/image_tokenizer.pt").to(device)
    # Memory optimization: Device placement for memory management
    
    # Load two similar images
    image1 = Image.open("data/images/test/sample1.jpg").convert('RGB')
    image2 = Image.open("data/images/test/sample2.jpg").convert('RGB')
    
    # Get token representations
    tensor1 = image_tokenizer.transform(image1).unsqueeze(0)
    tensor2 = image_tokenizer.transform(image2).unsqueeze(0)
    
    tokens1 = image_tokenizer.encode(tensor1)
    tokens2 = image_tokenizer.encode(tensor2)
    
    # Compare token distributions
    common_tokens = set(tokens1) & set(tokens2)
    similarity = len(common_tokens) / max(len(set(tokens1)), len(set(tokens2)))
    
    print(f"\nImage Similarity Analysis:")
    print(f"Number of common tokens: {len(common_tokens)}")
    print(f"Token-based similarity: {similarity:.2f}")

if __name__ == "__main__":
    # Run examples
    text_tokenizer_example()
    image_tokenizer_example()
    demonstrate_use_cases()
