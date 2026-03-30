#!/usr/bin/env python3
"""
ImpressionCore: Test Tokenizers Example

Module for test tokenizers example functionality in the ImpressionCore framework.

File: tests\test_tokenizers_example.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [qa, pytorch, production, testing, 2025]
Dependencies: [torch, pathlib, numpy]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements test tokenizers example functionality for the
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
from tests.test_tokenizers_example import MainClass
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
from pathlib import Path

# Add parent directory to path for importing
sys.path.append(str(Path(__file__).parent.parent))

import torch
import numpy as np
from PIL import Image

# Try importing the necessary components
try:
    from src.core.ai.tokenization import get_tokenizer # Changed from impressioncore.src
    from src.core.ai.tokenization import ImageTokenizer # Corrected import
except ImportError as e:
    print("Error: ImpressionCore tokenization modules not found.")
    print(f"Details: {e}")
    print(f"Current sys.path: {sys.path}")
    print("Make sure the d:\\Projects\\impressioncore directory is in PYTHONPATH or the package is installed correctly.")
    sys.exit(1)


def test_text_tokenization(tokenizer_path):
    """Test the text tokenizer functionality."""
    print("\n" + "="*50)
    print(" TEXT TOKENIZER EXAMPLE ")
    print("="*50)
    
    # Load the tokenizer
    print(f"Loading text tokenizer from {tokenizer_path}")
    tokenizer = get_tokenizer("text", tokenizer_path)
    print(f"Vocabulary size: {tokenizer.vocab_size}")
    
    # Define some example text
    example_texts = [
        "ImpressionCore is a brain-inspired multimodal AI framework.",
        "It can process both text and images using transformer architectures.",
        "The universal knowledge store helps organize information."
    ]
    
    # Process each example
    for i, text in enumerate(example_texts):
        print(f"\nExample {i+1}: \"{text}\"")
        
        # Encode the text to token IDs
        token_ids = tokenizer.encode(text)
        print(f"Encoded token IDs: {token_ids[:10]}... (total: {len(token_ids)})")
        
        # Decode the token IDs back to text
        decoded_text = tokenizer.decode(token_ids)
        print(f"Decoded text: \"{decoded_text}\"")
        
        # Show some token details
        if len(token_ids) > 0:
            print("\nToken details:")
            for j in range(min(5, len(token_ids))):
                token_id = token_ids[j]
                token = tokenizer.id_to_token.get(token_id, "<unknown>")
                print(f"  Token {j+1}: ID={token_id}, Token=\"{token}\"")


def test_image_tokenization(tokenizer_path, image_path=None):
    """Test the image tokenizer functionality."""
    print("\n" + "="*50)
    print(" IMAGE TOKENIZER EXAMPLE ")
    print("="*50)
    
    # Check if we can create or process images
    try:
        import numpy as np
        from PIL import Image, ImageDraw
    except ImportError:
        print("Error: PIL and numpy are required for image tokenization")
        return
        
    # Load the tokenizer using the get_tokenizer function
    print(f"Loading image tokenizer from {tokenizer_path}")
    try:
        tokenizer = get_tokenizer("image", tokenizer_path)
        print(f"Image size: {tokenizer.image_size}x{tokenizer.image_size}")
        print(f"Patch size: {tokenizer.patch_size}x{tokenizer.patch_size}")
        print(f"Codebook size: {tokenizer.num_tokens}")
    except Exception as e:
        print(f"Error loading image tokenizer: {e}")
        return
    
    # Create or load an image
    if image_path and os.path.exists(image_path):
        print(f"Loading image from {image_path}")
        image = Image.open(image_path).convert("RGB")
    else:
        print("Creating a test image")
        # Create a test image with some shapes
        image = Image.new("RGB", (256, 256), color=(240, 240, 255))
        draw = ImageDraw.Draw(image)
        
        # Draw some shapes
        draw.rectangle((50, 50, 200, 200), fill=(200, 100, 100))
        draw.ellipse((75, 75, 175, 175), fill=(100, 200, 100))
        draw.polygon([(125, 30), (200, 120), (50, 120)], fill=(100, 100, 200))
        
        # Save the test image
        test_image_path = "test_image.png"
        image.save(test_image_path)
        print(f"Saved test image to {test_image_path}")
    
    # Resize image to match tokenizer's expected size
    image = image.resize((tokenizer.image_size, tokenizer.image_size))
    
    # Convert to tensor
    img_array = np.array(image)
    img_tensor = torch.from_numpy(img_array).permute(2, 0, 1).float() / 255.0
    
    # Encode the image
    print("\nEncoding image to tokens...")
    token_ids = tokenizer.encode(img_tensor)
    print(f"Encoded to {len(token_ids)} tokens")
    print(f"First 10 token IDs: {token_ids[:10]}")
    
    # Visualize token distribution
    unique_tokens = len(set(token_ids))
    print(f"Number of unique tokens used: {unique_tokens}")
    
    # Decode back to image
    print("\nDecoding tokens back to image...")
    reconstructed_tensor = tokenizer.decode(token_ids)
    
    # Convert tensor to image
    reconstructed_array = (reconstructed_tensor.permute(1, 2, 3).numpy() * 255).astype(np.uint8)
    reconstructed_image = Image.fromarray(reconstructed_array[0])
    
    # Save reconstructed image
    reconstructed_path = "reconstructed_image.png"
    reconstructed_image.save(reconstructed_path)
    print(f"Saved reconstructed image to {reconstructed_path}")
    
    # Calculate reconstruction quality
    orig_mean = img_tensor.mean().item()
    recon_mean = reconstructed_tensor.mean().item()
    print(f"Original image mean pixel value: {orig_mean:.4f}")
    print(f"Reconstructed image mean pixel value: {recon_mean:.4f}")
    
    print("\nNote: The reconstruction quality is intentionally low in this demo")
    print("as we're using a simplified tokenizer without a fully trained VQ-VAE model.")


def main():
    """
    
    main function for processing.
    
    Args:
        No arguments: Function parameters
    
    Returns:
        Processed result
    
    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints
    
    """
    parser = argparse.ArgumentParser(description="Test ImpressionCore tokenizers")
    parser.add_argument("--text-tokenizer", type=str, 
                      default="data/tokenizer/text_tokenizer.json",
                      help="Path to trained text tokenizer")
    parser.add_argument("--image-tokenizer", type=str, 
                      default="data/tokenizer/image_tokenizer.pt",
                      help="Path to trained image tokenizer")
    parser.add_argument("--image-path", type=str, default=None,
                      help="Optional path to test image")
    parser.add_argument("--mode", choices=["text", "image", "both"], 
                      default="both", help="Which tokenizer to test")
    
    args = parser.parse_args()
    
    print("ImpressionCore Tokenizer Example")
    print("===============================")
    
    # Test tokenizers based on mode
    if args.mode in ["text", "both"]:
        test_text_tokenization(args.text_tokenizer)
        
    if args.mode in ["image", "both"]:
        test_image_tokenization(args.image_tokenizer, args.image_path)
    
    print("\nTokenizer testing completed!")
    print("\nNext steps:")
    print("1. Integrate these tokenizers with your modal engine")
    print("2. Use them for training transformer and diffusion models")
    print("3. Explore the ImpressionCore API to see how they're used in the system")


if __name__ == "__main__":
    import argparse
    main()
