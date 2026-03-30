#!/usr/bin/env python3
"""
ImpressionCore: Tokenizer Usage Example

Module for tokenizer usage example functionality in the ImpressionCore framework.

File: examples\tokenizer_usage_example.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [pytorch, production, 2025]
Dependencies: [torch, pathlib, numpy]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements tokenizer usage example functionality for the
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
from examples.tokenizer_usage_example import MainClass
instance = MainClass()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

import os
import sys
import argparse
from pathlib import Path
import logging

# Add parent directory to path for importing
sys.path.append(str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Check if tokenization components are available
try:
    from src.core.ai.tokenization import get_default_tokenizer
    from src.core.ai.tokenization.tokenizer import BPETokenizer, tokenize_text
    text_tokenizer_available = True
except ImportError:
    logger.warning("Text tokenizer not available. Skipping text tokenization examples.")
    text_tokenizer_available = False

try:
    from src.core.ai.tokenization.image_tokenizer import ImageTokenizer
    import torch
    import numpy as np
    from PIL import Image
    image_tokenizer_available = True
except ImportError:
    logger.warning("Image tokenizer not available. Skipping image tokenization examples.")
    image_tokenizer_available = False

try:
    from src.core.ai.tokenization.integration import (
        TokenizationProcessor, tokenize_for_modality, detokenize_for_modality
    )
    integration_available = True
except ImportError:
    logger.warning("Tokenization integration not available. Skipping integration examples.")
    integration_available = False


def example_basic_text_tokenization():
    """Demonstrate basic text tokenization."""
    if not text_tokenizer_available:
        logger.info("Text tokenizer not available. Skipping example.")
        return
    
    print("\n=== Basic Text Tokenization ===\n")
    
    # Get the default tokenizer
    tokenizer = get_default_tokenizer()
    
    # Example text
    text = "Hello world! This is a simple example of tokenization in ImpressionCore."
    print(f"Original text: \"{text}\"\n")
    
    # Tokenize
    token_ids = tokenizer.encode(text)
    print(f"Encoded token IDs: {token_ids[:10]}... (total: {len(token_ids)} tokens)\n")
    
    # Decode
    decoded_text = tokenizer.decode(token_ids)
    print(f"Decoded text: \"{decoded_text}\"\n")
    
    # Show special tokens
    print("Special tokens:")
    for name, token_id in tokenizer.special_tokens.items():
        print(f"  {name}: {token_id}")
    print()


def example_custom_text_tokenization():
    """Demonstrate custom text tokenization settings."""
    if not text_tokenizer_available:
        logger.info("Text tokenizer not available. Skipping example.")
        return
    
    print("\n=== Custom Text Tokenization ===\n")
    
    # Create a custom tokenizer
    custom_tokenizer = BPETokenizer(vocab_size=10000)
    
    # Example text
    text = "Custom tokenization with a smaller vocabulary size."
    print(f"Original text: \"{text}\"\n")
    
    # Tokenize with custom settings
    token_ids = custom_tokenizer.encode(text, add_special_tokens=False)
    print(f"Encoded without special tokens: {token_ids}\n")
    
    # Tokenize with special tokens
    token_ids_with_special = custom_tokenizer.encode(text, add_special_tokens=True)
    print(f"Encoded with special tokens: {token_ids_with_special}\n")
    
    # Decode with and without special tokens
    decoded_with_special = custom_tokenizer.decode(token_ids_with_special, skip_special_tokens=False)
    decoded_without_special = custom_tokenizer.decode(token_ids_with_special, skip_special_tokens=True)
    
    print(f"Decoded (keeping special tokens): \"{decoded_with_special}\"")
    print(f"Decoded (skipping special tokens): \"{decoded_without_special}\"\n")


def example_image_tokenization(image_path=None):
    """Demonstrate image tokenization."""
    if not image_tokenizer_available:
        logger.info("Image tokenizer not available. Skipping example.")
        return
    
    print("\n=== Image Tokenization ===\n")
    
    # Use default image or provided image
    if image_path is None or not os.path.exists(image_path):
        # Create a simple test image
        print("No valid image path provided. Creating a test image.\n")
        image = Image.new("RGB", (256, 256), color=(100, 150, 200))
        
        # Add some shapes to make it more interesting
        from PIL import ImageDraw
        draw = ImageDraw.Draw(image)
        draw.rectangle((50, 50, 200, 200), fill=(200, 100, 100))
        draw.ellipse((70, 70, 180, 180), fill=(100, 200, 100))
    else:
        # Load the image
        print(f"Loading image from {image_path}\n")
        image = Image.open(image_path).convert("RGB")
        
        # Resize if too large
        if max(image.size) > 512:
            image.thumbnail((512, 512))
            print(f"Resized image to {image.size}\n")
    
    # Display image dimensions
    print(f"Image dimensions: {image.size[0]}x{image.size[1]}\n")
    
    # Save the image for reference
    test_image_path = "test_image.png"
    image.save(test_image_path)
    print(f"Saved image to {test_image_path} for reference\n")
    
    # Convert to tensor
    img_array = np.array(image)
    img_tensor = torch.from_numpy(img_array).permute(2, 0, 1).float() / 255.0
    
    # Create image tokenizer
    print("Creating image tokenizer...")
    tokenizer = ImageTokenizer(
        image_size=256,  # Resize to this dimension
        patch_size=16,   # Size of each patch
        num_tokens=8192, # Size of codebook vocabulary
        channels=3       # RGB
    )
    
    # Tokenize the image
    print("Tokenizing image...")
    token_ids = tokenizer.encode(img_tensor)
    print(f"Image encoded to {len(token_ids)} tokens")
    print(f"First few tokens: {token_ids[:10]}...\n")
    
    # Reconstruct the image
    print("Reconstructing image from tokens...")
    reconstructed_array = tokenizer.decode(token_ids)
    
    # Convert back to PIL Image
    reconstructed_img = Image.fromarray(
        (np.transpose(reconstructed_array, (1, 2, 0)) * 255).astype(np.uint8)
    )
    
    # Save the reconstructed image
    recon_path = "reconstructed_image.png"
    reconstructed_img.save(recon_path)
    print(f"Saved reconstructed image to {recon_path}\n")
    print("Note: The reconstructed image quality depends on the tokenizer's codebook size and training.\n")


def example_integration():
    """Demonstrate integration with Modal Engine."""
    if not integration_available:
        logger.info("Integration components not available. Skipping example.")
        return
    
    print("\n=== Tokenization Integration ===\n")
    
    # Create processor
    processor = TokenizationProcessor()
    
    # Example with text
    text = "This example shows how to integrate tokenization with the Modal Engine."
    print(f"Original text: \"{text}\"\n")
    
    # Tokenize with modality system
    tokens = tokenize_for_modality(text, "text")
    print(f"Tokenized with modality system: {tokens[:5]}... (total: {len(tokens)} tokens)\n")
    
    # Detokenize
    decoded = detokenize_for_modality(tokens, "text")
    print(f"Detokenized: \"{decoded}\"\n")
    
    # Show how to get vocabulary size
    text_vocab_size = processor.get_vocab_size("text")
    image_vocab_size = processor.get_vocab_size("image")
    
    print(f"Text vocabulary size: {text_vocab_size}")
    print(f"Image vocabulary size: {image_vocab_size}\n")


def main():
    """Main entry point for the example script."""
    parser = argparse.ArgumentParser(description="Demonstrate tokenization usage")
    parser.add_argument("--image", type=str, default=None, 
                       help="Path to an image file for image tokenization example")
    args = parser.parse_args()
    
    print("\nImpressionCore Tokenization Usage Examples")
    print("========================================\n")
    
    # Run examples
    example_basic_text_tokenization()
    example_custom_text_tokenization()
    example_image_tokenization(args.image)
    example_integration()
    
    print("\nExamples completed!\n")


if __name__ == "__main__":
    main()
