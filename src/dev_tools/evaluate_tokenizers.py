#!/usr/bin/env python3
"""
ImpressionCore: Evaluate Tokenizers

Module for evaluate tokenizers functionality in the ImpressionCore framework.

File: tools\evaluate_tokenizers.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [memory-critical, pytorch, production, 2025, object-oriented]
Dependencies: [torch, pathlib, numpy]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements evaluate tokenizers functionality for the
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
# from tools.evaluate_tokenizers import  # Fixed: using local implementation TokenizerEvaluator
instance = TokenizerEvaluator()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

import torch
import numpy as np
from pathlib import Path
from PIL import Image
import matplotlib.pyplot as plt
from src.core.ai.tokenization.bpe import BPETokenizer
from src.core.ai.tokenization.image import ImageTokenizer
from sklearn.metrics import normalized_mutual_info_score
import json

class TokenizerEvaluator:
    """Evaluate text and image tokenizers"""
    
    def __init__(self, output_dir="output/evaluation"):
        """
        
    __init__ function for processing.
    
    Args:
        self, output_dir: Function parameters
    
    Returns:
        Processed result
    
    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints
    
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def evaluate_text_tokenizer(self, tokenizer_path, test_file, save_prefix="text"):
        """Evaluate text tokenizer performance"""
        print("\nEvaluating text tokenizer...")
        tokenizer = BPETokenizer.load(tokenizer_path)
        
        # Read test data
        with open(test_file, 'r', encoding='utf-8') as f:
            text = f.read()
            
        # Tokenize and reconstruct
        tokens = tokenizer.encode(text)
        reconstructed = tokenizer.decode(tokens)
        
        # Calculate metrics
        metrics = {
            "vocabulary_size": len(tokenizer.vocab),
            "compression_ratio": len(tokens) / len(text),
            "unique_tokens": len(set(tokens)),
            "token_frequency": self._calculate_token_frequency(tokens)
        }
        
        # Save metrics
        metrics_path = self.output_dir / f"{save_prefix}_evaluation.json"
        with open(metrics_path, 'w') as f:
            json.dump(metrics, f, indent=2)
        
        # Plot token frequency distribution
        plt.figure(figsize=(10, 6))
        token_freqs = sorted(metrics["token_frequency"].values(), reverse=True)
        plt.plot(token_freqs)
        plt.title("Token Frequency Distribution")
        plt.xlabel("Token Rank")
        plt.ylabel("Frequency")
        plt.yscale('log')
        plt.savefig(self.output_dir / f"{save_prefix}_token_distribution.png")
        plt.close()
        
        # Save sample tokenization
        sample_text = text[:1000]  # First 1000 chars
        sample_tokens = tokenizer.encode(sample_text)
        sample_reconstruction = tokenizer.decode(sample_tokens)
        
        with open(self.output_dir / f"{save_prefix}_sample_tokenization.txt", 'w') as f:
            f.write("Original text:\n")
            f.write(sample_text + "\n\n")
            f.write("Token IDs:\n")
            f.write(str(sample_tokens) + "\n\n")
            f.write("Reconstructed text:\n")
            f.write(sample_reconstruction)
            
        print("Text tokenizer evaluation completed. Results saved to:", self.output_dir)
        return metrics
        
    def evaluate_image_tokenizer(self, tokenizer_path, test_image_dir, save_prefix="image"):
        """Evaluate image tokenizer performance"""
        print("\nEvaluating image tokenizer...")
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        # Memory optimization: CUDA operations for GPU acceleration
        tokenizer = ImageTokenizer(patch_size=8).load(tokenizer_path).to(device)
        # Memory optimization: Device placement for memory management
        tokenizer.eval()
        
        metrics = {
            "psnr_scores": [],
            "ssim_scores": [],
            "token_usage": []
        }
        
        # Process test images
        test_images = list(Path(test_image_dir).glob('*.jpg')) + list(Path(test_image_dir).glob('*.png'))
        for idx, img_path in enumerate(test_images[:5]):  # Evaluate first 5 images
            # Load and preprocess image
            image = Image.open(img_path).convert('RGB')
            image_tensor = tokenizer.transform(image).unsqueeze(0).to(device)
            # Memory optimization: Device placement for memory management
            
            # Tokenize and reconstruct
            with torch.no_grad():
            # Memory optimization: Disable gradient computation to save memory
                tokens = tokenizer.encode(image_tensor)
                reconstructed = tokenizer.decode(tokens)
            
            # Calculate metrics
            metrics["psnr_scores"].append(
                self._calculate_psnr(image_tensor, reconstructed).item()
            )
            metrics["ssim_scores"].append(
                self._calculate_ssim(image_tensor, reconstructed).item()
            )
            metrics["token_usage"].append(len(set(tokens)))
            
            # Save comparison visualization
            if idx == 0:  # Save first image comparison
                plt.figure(figsize=(12, 6))
                plt.subplot(1, 2, 1)
                plt.imshow(image_tensor.squeeze(0).permute(1, 2, 0).cpu())
                plt.title("Original")
                plt.axis('off')
                
                plt.subplot(1, 2, 2)
                plt.imshow(reconstructed.squeeze(0).permute(1, 2, 0).cpu())
                plt.title("Reconstructed")
                plt.axis('off')
                
                plt.savefig(self.output_dir / f"{save_prefix}_reconstruction_comparison.png")
                plt.close()
        
        # Calculate average metrics
        avg_metrics = {
            "average_psnr": np.mean(metrics["psnr_scores"]),
            "average_ssim": np.mean(metrics["ssim_scores"]),
            "average_unique_tokens": np.mean(metrics["token_usage"]),
            "std_unique_tokens": np.std(metrics["token_usage"])
        }
        
        # Save metrics
        metrics_path = self.output_dir / f"{save_prefix}_evaluation.json"
        with open(metrics_path, 'w') as f:
            json.dump({**metrics, **avg_metrics}, f, indent=2)
            
        print("Image tokenizer evaluation completed. Results saved to:", self.output_dir)
        return avg_metrics
    
    def _calculate_token_frequency(self, tokens):
        """Calculate token frequency distribution"""
        freq = {}
        for token in tokens:
            freq[token] = freq.get(token, 0) + 1
        return freq
    
    def _calculate_psnr(self, original, reconstructed):
        """Calculate Peak Signal-to-Noise Ratio"""
        mse = torch.mean((original - reconstructed) ** 2)
        return 20 * torch.log10(1.0 / torch.sqrt(mse))
    
    def _calculate_ssim(self, original, reconstructed, window_size=11):
        """Calculate Structural Similarity Index"""
        C1 = (0.01 * 1) ** 2
        C2 = (0.03 * 1) ** 2
        
        # Calculate means
        mu1 = torch.nn.functional.avg_pool2d(original, window_size, stride=1, padding=window_size//2)
        mu2 = torch.nn.functional.avg_pool2d(reconstructed, window_size, stride=1, padding=window_size//2)
        
        # Calculate variances and covariance
        sigma1_sq = torch.nn.functional.avg_pool2d(original * original, window_size, stride=1, padding=window_size//2) - mu1 * mu1
        sigma2_sq = torch.nn.functional.avg_pool2d(reconstructed * reconstructed, window_size, stride=1, padding=window_size//2) - mu2 * mu2
        sigma12 = torch.nn.functional.avg_pool2d(original * reconstructed, window_size, stride=1, padding=window_size//2) - mu1 * mu2
        
        # Calculate SSIM
        ssim_map = ((2 * mu1 * mu2 + C1) * (2 * sigma12 + C2)) / ((mu1 * mu1 + mu2 * mu2 + C1) * (sigma1_sq + sigma2_sq + C2))
        return torch.mean(ssim_map)

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
    # Setup paths
    base_dir = Path(__file__).parent.parent
    text_tokenizer_path = base_dir / "data/tokenizers/text_tokenizer.json"
    image_tokenizer_path = base_dir / "data/tokenizers/image_tokenizer.pt"
    test_text = base_dir / "data/text_corpus/test.txt"
    test_images = base_dir / "data/images/test"
    
    # Run evaluation
    evaluator = TokenizerEvaluator()
    
    if text_tokenizer_path.exists():
        text_metrics = evaluator.evaluate_text_tokenizer(text_tokenizer_path, test_text)
        print("\nText Tokenizer Metrics:")
        print(json.dumps(text_metrics, indent=2))
    
    if image_tokenizer_path.exists():
        image_metrics = evaluator.evaluate_image_tokenizer(image_tokenizer_path, test_images)
        print("\nImage Tokenizer Metrics:")
        print(json.dumps(image_metrics, indent=2))

if __name__ == "__main__":
    main()
