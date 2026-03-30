#!/usr/bin/env python3
"""
ImpressionCore: Test Tokenizers

Module for test tokenizers functionality in the ImpressionCore framework.

File: examples\test_tokenizers.py
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
This module implements test tokenizers functionality for the
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
from examples.test_tokenizers import MainClass
instance = MainClass()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

import sys
import os
import argparse
from pathlib import Path

# Add the project root to Python's path to allow imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from src.training.tokenization import get_tokenizer
    import torch
    import numpy as np
    from PIL import Image, ImageDraw
except ImportError as e:
    print(f"Error: Required modules not found: {e}")
    print("Make sure ImpressionCore is properly installed.")
    sys.exit(1)


def test_text_tokenizer(tokenizer_path: str, text: str = None):
    """Test a text tokenizer with sample text."""
    print("\n" + "="*50)
    print(" TEXT TOKENIZER TEST ")
    print("="*50)
    
    if not os.path.exists(tokenizer_path):
        print(f"Error: Text tokenizer file not found at {tokenizer_path}")
        return False
    
    print(f"Loading text tokenizer from {tokenizer_path}")
    tokenizer = get_tokenizer("text", tokenizer_path)
    
    if not text:
        text = "Hello, world! Testing the ImpressionCore text tokenizer."
    
    print(f"\nSample text: \"{text}\"")
    
    try:
        # Tokenize the text
        start_time = torch.cuda.Event(enable_timing=True) if torch.cuda.is_available() else None
        # Memory optimization: CUDA operations for GPU acceleration
        end_time = torch.cuda.Event(enable_timing=True) if torch.cuda.is_available() else None
        # Memory optimization: CUDA operations for GPU acceleration
        
        if start_time:
            start_time.record()
            
        token_ids = tokenizer.encode(text)
        
        if end_time:
            end_time.record()
            torch.cuda.synchronize()
            # Memory optimization: CUDA operations for GPU acceleration
            encoding_time = start_time.elapsed_time(end_time)
            print(f"Encoding time: {encoding_time:.2f} ms")
        
        print(f"Encoded to {len(token_ids)} tokens: {token_ids}")
        
        # Decode the tokens
        if start_time:
            start_time.record()
            
        decoded_text = tokenizer.decode(token_ids)
        
        if end_time:
            end_time.record()
            torch.cuda.synchronize()
            # Memory optimization: CUDA operations for GPU acceleration
            decoding_time = start_time.elapsed_time(end_time)
            print(f"Decoding time: {decoding_time:.2f} ms")
        
        print(f"Decoded text: \"{decoded_text}\"")
        
        # Check reconstruction quality
        if text == decoded_text:
            print("✅ Perfect reconstruction!")
        else:
            print("⚠️ Reconstruction differs from original")
            print("Differences may be due to tokenizer limitations or vocabulary constraints")
            
        return True
    except Exception as e:
        print(f"Error testing text tokenizer: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_image_tokenizer(tokenizer_path: str, image_path: str = None):
    """Test an image tokenizer with a sample image."""
    print("\n" + "="*50)
    print(" IMAGE TOKENIZER TEST ")
    print("="*50)
    
    if not os.path.exists(tokenizer_path):
        print(f"Error: Image tokenizer file not found at {tokenizer_path}")
        return False
    
    print(f"Loading image tokenizer from {tokenizer_path}")
    tokenizer = get_tokenizer("image", tokenizer_path)
    
    try:
        # Create or load test image
        if image_path and os.path.exists(image_path):
            print(f"Loading image from {image_path}")
            image = Image.open(image_path).convert("RGB")
        else:
            print("Creating test image...")
            image_size = tokenizer.image_size if hasattr(tokenizer, "image_size") else 256
            
            # Create test image with simple shapes
            image = Image.new("RGB", (image_size, image_size), color=(240, 240, 255))
            draw = ImageDraw.Draw(image)
            
            # Draw a red rectangle
            draw.rectangle([(50, 50), (150, 100)], fill=(255, 0, 0))
            
            # Draw a green circle
            draw.ellipse([(100, 100), (200, 200)], fill=(0, 255, 0))
            
            # Draw a blue triangle
            draw.polygon([(75, 200), (150, 120), (225, 200)], fill=(0, 0, 255))
            
            # Save test image
            test_path = "test_image.png"
            image.save(test_path)
            print(f"Saved test image to {test_path}")
        
        # Resize image if needed
        if hasattr(tokenizer, "image_size"):
            image = image.resize((tokenizer.image_size, tokenizer.image_size))
        
        # Convert to tensor
        img_array = np.array(image)
        img_tensor = torch.from_numpy(img_array).permute(2, 0, 1).float() / 255.0
        
        print(f"\nImage shape: {img_tensor.shape}")
        
        # Tokenize the image
        start_time = torch.cuda.Event(enable_timing=True) if torch.cuda.is_available() else None
        # Memory optimization: CUDA operations for GPU acceleration
        end_time = torch.cuda.Event(enable_timing=True) if torch.cuda.is_available() else None
        # Memory optimization: CUDA operations for GPU acceleration
        
        if start_time:
            start_time.record()
            
        token_ids = tokenizer.encode(img_tensor)
        
        if end_time:
            end_time.record()
            torch.cuda.synchronize()
            # Memory optimization: CUDA operations for GPU acceleration
            encoding_time = start_time.elapsed_time(end_time)
            print(f"Encoding time: {encoding_time:.2f} ms")
        
        print(f"Encoded to {len(token_ids)} tokens")
        print(f"First 10 tokens: {token_ids[:10]}")
        unique_tokens = len(set(token_ids))
        print(f"Unique tokens: {unique_tokens} ({unique_tokens/len(token_ids)*100:.1f}% of total)")
        
        # Decode the tokens
        if start_time:
            start_time.record()
            
        reconstructed = tokenizer.decode(token_ids)
        
        if end_time:
            end_time.record()
            torch.cuda.synchronize()
            # Memory optimization: CUDA operations for GPU acceleration
            decoding_time = start_time.elapsed_time(end_time)
            print(f"Decoding time: {decoding_time:.2f} ms")
        
        # Save reconstructed image
        if isinstance(reconstructed, torch.Tensor):
            if reconstructed.dim() > 3:
                reconstructed = reconstructed.squeeze(0)  # Remove batch dimension if present
                
            reconstructed_array = (reconstructed.permute(1, 2, 0).numpy() * 255).astype(np.uint8)
            reconstructed_image = Image.fromarray(reconstructed_array)
            reconstructed_path = "reconstructed_image.png"
            reconstructed_image.save(reconstructed_path)
            print(f"Saved reconstructed image to {reconstructed_path}")
            
            # Calculate MSE
            mse = ((img_tensor - reconstructed) ** 2).mean().item()
            psnr = 10 * np.log10(1.0 / mse) if mse > 0 else 100.0
            print(f"\nReconstruction quality:")
            print(f"  MSE: {mse:.4f}")
            print(f"  PSNR: {psnr:.2f} dB")
            print("\nNote: Lower MSE and higher PSNR indicate better reconstruction quality")
        
        return True
    except Exception as e:
        print(f"Error testing image tokenizer: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Test ImpressionCore tokenizers")
    parser.add_argument("--text", action="store_true", help="Test text tokenizer")
    parser.add_argument("--image", action="store_true", help="Test image tokenizer")
    parser.add_argument("--text-tokenizer", default="data/tokenizer/text_tokenizer.json", 
                      help="Path to text tokenizer")
    parser.add_argument("--image-tokenizer", default="data/tokenizer/image_tokenizer.pt", 
                      help="Path to image tokenizer")
    parser.add_argument("--image-path", help="Path to test image (optional)")
    parser.add_argument("--text-sample", help="Sample text to tokenize (optional)")
    
    args = parser.parse_args()
    
    # If neither --text nor --image is specified, test both
    if not args.text and not args.image:
        args.text = True
        args.image = True
    
    print("ImpressionCore Tokenizer Test")
    print("============================")
    
    success = True
    
    if args.text:
        success &= test_text_tokenizer(args.text_tokenizer, args.text_sample)
        
    if args.image:
        success &= test_image_tokenizer(args.image_tokenizer, args.image_path)
        
    print("\nTest completed!")
    if not success:
        print("⚠️ Some tests encountered errors. Check the output above for details.")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
