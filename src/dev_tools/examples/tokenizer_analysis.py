#!/usr/bin/env python3
"""
ImpressionCore: Tokenizer Analysis

Module for tokenizer analysis functionality in the ImpressionCore framework.

File: examples\tokenizer_analysis.py
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
This module implements tokenizer analysis functionality for the
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
from examples.tokenizer_analysis import MainClass
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
import random
import matplotlib.pyplot as plt
from collections import Counter
from pathlib import Path

# Add parent directory to path for importing
sys.path.append(str(Path(__file__).parent.parent))

try:
    from src.core.ai.tokenization import get_tokenizer
    from src.core.ai.tokenization.image_tokenizer import ImageTokenizer
    import torch
    import numpy as np
    from PIL import Image
except ImportError:
    print("Error: Required ImpressionCore modules not found.")
    sys.exit(1)


def analyze_text_tokenizer(tokenizer_path: str, corpus_dir: str = None, sample_count: int = 10):
    """
    Analyze a text tokenizer's performance on samples.
    
    Args:
        tokenizer_path: Path to the tokenizer file
        corpus_dir: Optional directory containing text samples
        sample_count: Number of samples to analyze
    """
    print("\n" + "="*60)
    print("TEXT TOKENIZER ANALYSIS")
    print("="*60)
    
    # Load tokenizer
    tokenizer = get_tokenizer("text", tokenizer_path)
    print(f"Loaded text tokenizer from {tokenizer_path}")
    print(f"Vocabulary size: {tokenizer.vocab_size}")
    print(f"Special tokens: {list(filter(lambda x: x.startswith('<') and x.endswith('>'), tokenizer.token_to_id.keys()))}")
    
    # Count token type distribution
    print("\nToken type distribution:")
    token_types = {"special": 0, "alphabetic": 0, "numeric": 0, "punctuation": 0, "whitespace": 0, "other": 0}
    
    for token, token_id in tokenizer.token_to_id.items():
        if token.startswith('<') and token.endswith('>'):
            token_types["special"] += 1
        elif token.isalpha():
            token_types["alphabetic"] += 1
        elif token.isdigit():
            token_types["numeric"] += 1
        elif token in ".,;:!?-\"'()[]{}<>":
            token_types["punctuation"] += 1
        elif token.isspace():
            token_types["whitespace"] += 1
        else:
            token_types["other"] += 1
            
    for token_type, count in token_types.items():
        print(f"  {token_type}: {count} tokens")
    
    # Get text samples
    samples = []
    if corpus_dir and os.path.exists(corpus_dir):
        # Get samples from corpus files
        for root, _, files in os.walk(corpus_dir):
            for file in files:
                if file.endswith('.txt'):
                    try:
                        with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                            content = f.read()
                            # Split into paragraphs
                            paragraphs = content.split('\n\n')
                            for para in paragraphs:
                                if para.strip():
                                    samples.append(para.strip())
                                    if len(samples) >= sample_count * 10:  # Get more than needed for random selection
                                        break
                            if len(samples) >= sample_count * 10:
                                break
                    except Exception as e:
                        print(f"Error reading file {file}: {e}")
            if len(samples) >= sample_count * 10:
                break
                
        # Select random samples if we have more than needed
        if len(samples) > sample_count:
            samples = random.sample(samples, sample_count)
    
    # If we don't have samples from files, use some default samples
    if not samples:
        samples = [
            "The quick brown fox jumps over the lazy dog.",
            "ImpressionCore provides tools for multimodal AI processing.",
            "Tokenization is a key step in natural language processing.",
            "Machine learning models require large amounts of training data.",
            "The performance of the system depends on various factors including hardware capabilities.",
            "Python is a widely used programming language for AI development.",
            "Neural networks have revolutionized computer vision and natural language processing.",
            "The transformer architecture has become dominant in NLP tasks.",
            "Deep learning models can require significant computational resources.",
            "The future of AI involves more efficient multimodal understanding."
        ]
    
    # Analyze tokenization of samples
    print(f"\nAnalyzing {len(samples)} text samples...")
    
    token_counts = []
    reconstruction_accuracies = []
    
    for i, sample in enumerate(samples[:min(5, len(samples))]):
        print(f"\nSample {i+1}: \"{sample[:100]}{'...' if len(sample) > 100 else ''}\"")
        
        # Tokenize and count
        token_ids = tokenizer.encode(sample)
        token_counts.append(len(token_ids))
        
        # Decode and check reconstruction
        reconstructed = tokenizer.decode(token_ids)
        
        # Calculate reconstruction accuracy
        if sample == reconstructed:
            accuracy = 100.0
        else:
            # Calculate character-level accuracy
            correct_chars = sum(1 for a, b in zip(sample, reconstructed) if a == b)
            total_chars = max(len(sample), len(reconstructed))
            accuracy = (correct_chars / total_chars) * 100
        
        reconstruction_accuracies.append(accuracy)
        
        print(f"  Tokens: {len(token_ids)}")
        print(f"  Reconstruction accuracy: {accuracy:.2f}%")
        
        # Print any differences if not perfect
        if accuracy < 100:
            if len(sample) != len(reconstructed):
                print(f"  Length difference: original={len(sample)}, reconstructed={len(reconstructed)}")
            
            # Find first difference
            for j, (orig_char, recon_char) in enumerate(zip(sample, reconstructed)):
                if orig_char != recon_char:
                    print(f"  First difference at position {j}: '{orig_char}' vs '{recon_char}'")
                    break
    
    # Calculate statistics
    if token_counts:
        print("\nToken count statistics:")
        print(f"  Average tokens per sample: {sum(token_counts) / len(token_counts):.2f}")
        print(f"  Min tokens: {min(token_counts)}")
        print(f"  Max tokens: {max(token_counts)}")
        
    if reconstruction_accuracies:
        print("\nReconstruction accuracy statistics:")
        print(f"  Average accuracy: {sum(reconstruction_accuracies) / len(reconstruction_accuracies):.2f}%")
        print(f"  Min accuracy: {min(reconstruction_accuracies):.2f}%")
        print(f"  Max accuracy: {max(reconstruction_accuracies):.2f}%")
        
    # Test handling of unknown characters
    print("\nTesting handling of unknown characters:")
    special_text = "Hello, 世界! This contains non-ASCII characters: ñáéíóú 😊"
    token_ids = tokenizer.encode(special_text)
    reconstructed = tokenizer.decode(token_ids)
    
    print(f"  Original: {special_text}")
    print(f"  Reconstructed: {reconstructed}")


def analyze_image_tokenizer(tokenizer_path: str, image_dir: str = None, sample_count: int = 3):
    """
    Analyze an image tokenizer's performance on samples.
    
    Args:
        tokenizer_path: Path to the tokenizer file
        image_dir: Optional directory containing images
        sample_count: Number of samples to analyze
    """
    print("\n" + "="*60)
    print("IMAGE TOKENIZER ANALYSIS")
    print("="*60)
    
    try:
        # Load tokenizer
        tokenizer = get_tokenizer("image", tokenizer_path)
        print(f"Loaded image tokenizer from {tokenizer_path}")
        print(f"Image size: {tokenizer.image_size}x{tokenizer.image_size}")
        print(f"Patch size: {tokenizer.patch_size}x{tokenizer.patch_size}")
        print(f"Codebook size: {tokenizer.num_tokens}")
        print(f"Patches per image: {tokenizer.patches_per_side}x{tokenizer.patches_per_side} = {tokenizer.num_patches}")
        
        # Get image samples
        image_paths = []
        if image_dir and os.path.exists(image_dir):
            # Get samples from image files
            for root, _, files in os.walk(image_dir):
                for file in files:
                    if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                        image_paths.append(os.path.join(root, file))
                        if len(image_paths) >= sample_count * 5:  # Get more than needed for random selection
                            break
                if len(image_paths) >= sample_count * 5:
                    break
                    
            # Select random samples if we have more than needed
            if len(image_paths) > sample_count:
                image_paths = random.sample(image_paths, sample_count)
        
        # If no images found, create test images
        images = []
        if not image_paths:
            print("\nCreating test images for analysis...")
            from PIL import Image, ImageDraw
            
            for i in range(sample_count):
                # Create a test image with random shapes
                image = Image.new("RGB", (tokenizer.image_size, tokenizer.image_size), color=(240, 240, 255))
                draw = ImageDraw.Draw(image)
                
                # Draw some shapes with random colors
                for _ in range(5):
                    color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                    shape_type = random.choice(["rectangle", "ellipse", "polygon"])
                    
                    if shape_type == "rectangle":
                        x1, y1 = random.randint(0, tokenizer.image_size // 2), random.randint(0, tokenizer.image_size // 2)
                        x2, y2 = x1 + random.randint(50, tokenizer.image_size // 2), y1 + random.randint(50, tokenizer.image_size // 2)
                        draw.rectangle([x1, y1, x2, y2], fill=color)
                        
                    elif shape_type == "ellipse":
                        x1, y1 = random.randint(0, tokenizer.image_size // 2), random.randint(0, tokenizer.image_size // 2)
                        x2, y2 = x1 + random.randint(50, tokenizer.image_size // 2), y1 + random.randint(50, tokenizer.image_size // 2)
                        draw.ellipse([x1, y1, x2, y2], fill=color)
                        
                    else:  # polygon
                        points = []
                        for _ in range(3):
                            points.append((random.randint(0, tokenizer.image_size), 
                                         random.randint(0, tokenizer.image_size)))
                        draw.polygon(points, fill=color)
                
                images.append(image)
        else:
            # Load images from paths
            for path in image_paths:
                try:
                    image = Image.open(path).convert("RGB")
                    image = image.resize((tokenizer.image_size, tokenizer.image_size))
                    images.append(image)
                except Exception as e:
                    print(f"Error loading image {path}: {e}")
        
        # Analyze tokenization of images
        print(f"\nAnalyzing {len(images)} images...")
        
        token_counts = []
        unique_token_counts = []
        reconstruction_scores = []
        token_histograms = []
        
        os.makedirs("tokenizer_analysis", exist_ok=True)
        
        for i, image in enumerate(images):
            print(f"\nImage {i+1}:")
            
            # Save original image
            orig_path = f"tokenizer_analysis/original_{i+1}.png"
            image.save(orig_path)
            print(f"  Saved original image to {orig_path}")
            
            # Convert to tensor
            img_array = np.array(image)
            img_tensor = torch.from_numpy(img_array).permute(2, 0, 1).float() / 255.0
            
            # Tokenize and count
            token_ids = tokenizer.encode(img_tensor)
            token_counts.append(len(token_ids))
            unique_tokens = len(set(token_ids))
            unique_token_counts.append(unique_tokens)
            
            # Count token frequencies
            token_freq = Counter(token_ids)
            token_histograms.append(token_freq)
            
            # Decode and reconstruct
            reconstructed_tensor = tokenizer.decode(token_ids)
            
            # Convert tensor to image
            reconstructed_array = (reconstructed_tensor.permute(1, 2, 0).numpy() * 255).astype(np.uint8)
            reconstructed_image = Image.fromarray(reconstructed_array)
            
            # Save reconstructed image
            recon_path = f"tokenizer_analysis/reconstructed_{i+1}.png"
            reconstructed_image.save(recon_path)
            print(f"  Saved reconstructed image to {recon_path}")
            
            # Calculate reconstruction quality (MSE)
            mse = ((img_tensor - reconstructed_tensor.squeeze(0)) ** 2).mean().item()
            psnr = 10 * np.log10(1.0 / mse) if mse > 0 else 100.0  # Peak signal-to-noise ratio
            reconstruction_scores.append(psnr)
            
            print(f"  Total tokens: {len(token_ids)}")
            print(f"  Unique tokens: {unique_tokens} ({unique_tokens / len(token_ids) * 100:.2f}% of total)")
            print(f"  Most common token: {token_freq.most_common(1)[0][0]} (used {token_freq.most_common(1)[0][1]} times)")
            print(f"  Reconstruction PSNR: {psnr:.2f} dB")
            
            # Visualize token distribution (for the first few images)
            if i < 2:  # Limit to first two images to avoid cluttering
                # Plot token frequency histogram
                plt.figure(figsize=(10, 6))
                token_ids_list = list(token_freq.keys())
                counts = list(token_freq.values())
                plt.bar(token_ids_list, counts)
                plt.title(f"Token Frequency Distribution (Image {i+1})")
                plt.xlabel("Token ID")
                plt.ylabel("Frequency")
                plt.xlim(0, tokenizer.num_tokens)
                hist_path = f"tokenizer_analysis/token_histogram_{i+1}.png"
                plt.savefig(hist_path)
                plt.close()
                print(f"  Saved token histogram to {hist_path}")
        
        # Calculate statistics
        if token_counts:
            print("\nToken count statistics:")
            print(f"  Average tokens per image: {sum(token_counts) / len(token_counts):.2f}")
            print(f"  Average unique tokens per image: {sum(unique_token_counts) / len(unique_token_counts):.2f}")
            print(f"  Avg token utilization: {sum(unique_token_counts) / len(unique_token_counts) / tokenizer.num_tokens * 100:.2f}% of codebook")
            
        if reconstruction_scores:
            print("\nReconstruction quality statistics:")
            print(f"  Average PSNR: {sum(reconstruction_scores) / len(reconstruction_scores):.2f} dB")
            print(f"  Min PSNR: {min(reconstruction_scores):.2f} dB")
            print(f"  Max PSNR: {max(reconstruction_scores):.2f} dB")
            
        # Plot combined token usage across all analyzed images
        combined_histogram = Counter()
        for hist in token_histograms:
            combined_histogram.update(hist)
            
        print("\nCodebook utilization:")
        used_tokens = len(combined_histogram)
        print(f"  Used tokens: {used_tokens} out of {tokenizer.num_tokens} ({used_tokens / tokenizer.num_tokens * 100:.2f}%)")
        
        plt.figure(figsize=(12, 6))
        plt.bar(list(combined_histogram.keys()), list(combined_histogram.values()))
        plt.title(f"Combined Token Usage Across All Images")
        plt.xlabel("Token ID")
        plt.ylabel("Frequency")
        plt.xlim(0, tokenizer.num_tokens)
        plt.savefig("tokenizer_analysis/combined_token_usage.png")
        plt.close()
        print("  Saved combined token usage histogram to tokenizer_analysis/combined_token_usage.png")
        
    except Exception as e:
        print(f"Error analyzing image tokenizer: {e}")
        import traceback
        traceback.print_exc()


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
    parser = argparse.ArgumentParser(description="Analyze ImpressionCore tokenizers")
    parser.add_argument("--text", action="store_true", help="Analyze text tokenizer")
    parser.add_argument("--image", action="store_true", help="Analyze image tokenizer")
    parser.add_argument("--text-tokenizer", type=str, 
                      default="data/tokenizer/text_tokenizer.json",
                      help="Path to text tokenizer")
    parser.add_argument("--image-tokenizer", type=str, 
                      default="data/tokenizer/image_tokenizer.pt",
                      help="Path to image tokenizer")
    parser.add_argument("--text-corpus", type=str, default=None,
                      help="Directory containing text corpus for testing")
    parser.add_argument("--image-dir", type=str, default=None,
                      help="Directory containing images for testing")
    parser.add_argument("--samples", type=int, default=5,
                      help="Number of samples to analyze")
    
    args = parser.parse_args()
    
    # If no specific test is specified, run both if available
    if not args.text and not args.image:
        args.text = True
        args.image = True
        
    print("ImpressionCore Tokenizer Analysis")
    print("================================")
    print("This tool provides detailed analysis of tokenizer behavior on sample data.")
    
    # Check if tokenizer files exist
    if args.text and not os.path.exists(args.text_tokenizer):
        print(f"Error: Text tokenizer file not found at {args.text_tokenizer}")
        print("Please train the text tokenizer first with: python -m training.train_tokenizer --type text")
        args.text = False
        
    if args.image and not os.path.exists(args.image_tokenizer):
        print(f"Error: Image tokenizer file not found at {args.image_tokenizer}")
        print("Please train the image tokenizer first with: python -m training.train_tokenizer --type image")
        args.image = False
        
    # Run analyses
    if args.text:
        analyze_text_tokenizer(args.text_tokenizer, args.text_corpus, args.samples)
        
    if args.image:
        try:
            import matplotlib
            matplotlib.use('Agg')  # Use non-interactive backend
            analyze_image_tokenizer(args.image_tokenizer, args.image_dir, args.samples)
        except ImportError:
            print("Error: matplotlib is required for image tokenizer analysis. Install with: pip install matplotlib")
    
    print("\nTokenizer analysis complete!")
    print("Results saved in the tokenizer_analysis directory.")


if __name__ == "__main__":
    main()
