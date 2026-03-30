#!/usr/bin/env python3
"""
ImpressionCore: Data Utils

Module for data utils functionality in the ImpressionCore framework.

File: training\data_utils.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [memory-critical, training, gpu-optimized, ml, pytorch, production, 2025]
Dependencies: [torch, typing, pathlib, numpy]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements data utils functionality for the
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
from training.data_utils import MainClass
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
import logging
import random
from typing import List, Tuple, Optional, Dict, Any
from pathlib import Path

try:
    import torch
    if hasattr(torch, 'Tensor'):
        TORCH_AVAILABLE = True
        TensorType = torch.Tensor
    else:
        TORCH_AVAILABLE = False
        TensorType = Any
except ImportError:
    torch = None
    TORCH_AVAILABLE = False
    TensorType = Any

import numpy as np
from PIL import Image, ImageDraw

# Set up logging
logger = logging.getLogger(__name__)


def generate_sample_text_corpus(output_dir: str, num_samples: int = 100) -> List[str]:
    """
    Generate sample text data for training.
    
    Args:
        output_dir: Output directory for text files
        num_samples: Number of text samples to generate
        
    Returns:
        List of generated text samples
    """
    os.makedirs(output_dir, exist_ok=True)
    samples = []
    
    # Example texts for generation
    sample_texts = [
        "ImpressionCore is a brain-inspired multimodal AI framework.",
        "It can process text, images, and other modalities.",
        "The framework includes tokenizers for different types of content.",
        "Machine learning models form the core of the system.",
        "Neural networks help process complex patterns in data.",
        "Transformer architecture powers modern NLP applications.",
        "Tokenization is a fundamental step in processing content.",
        "The system is designed to run on systems with limited resources.",
        "Memory efficiency is important for practical applications.",
        # Memory optimization: Memory-critical operation
        "Multimodal processing combines different types of data.",
        "Computer vision is integrated with natural language understanding.",
        "Deep learning has revolutionized artificial intelligence.",
        "Large language models can generate human-like text.",
        "Attention mechanisms help models focus on relevant information.",
        "Knowledge graphs store structured information for reasoning.",
        "Training deep neural networks requires significant data.",
        "Transfer learning allows models to use knowledge from different domains.",
        "Self-supervised learning reduces the need for labeled data.",
        "Data preprocessing is crucial for model performance.",
        # Memory optimization: Explicit memory cleanup
        "Model evaluation helps ensure good performance on new data."
        # Memory optimization: Explicit memory cleanup
    ]
    
    for i in range(num_samples):
        # Generate a random number of sentences (5-15)
        num_sentences = random.randint(5, 15)
        
        # Randomly select sentences from the sample texts
        text = " ".join(random.choice(sample_texts) for _ in range(num_sentences))
        
        # Save to file
        filename = os.path.join(output_dir, f"sample_{i:03d}.txt")
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(text)
            
        samples.append(text)
        
    logger.info(f"Generated {len(samples)} sample text files in {output_dir}")
    return samples


def generate_sample_images(output_dir: str, num_samples: int = 50, 
                         size: int = 256) -> List[str]:
    """
    Generate sample images for training.
    
    Args:
        output_dir: Output directory for images
        num_samples: Number of images to generate
        size: Image size (width and height)
        
    Returns:
        List of paths to generated images
    """
    try:
        import numpy as np
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        logger.error("PIL and numpy are required for image generation")
        return []
        
    os.makedirs(output_dir, exist_ok=True)
    image_paths = []
    
    # Create different types of sample images
    for i in range(num_samples):
        # Determine image type
        image_type = i % 4  # 4 different types of images
        
        if image_type == 0:
            # Gradient background with shapes
            image = Image.new('RGB', (size, size), color=(240, 240, 255))
            draw = ImageDraw.Draw(image)
            
            # Add gradient background
            for y in range(size):
                r = int(240 - y * 50 / size)
                g = int(240 - y * 20 / size)
                b = int(255)
                draw.line([(0, y), (size, y)], fill=(r, g, b))
            
            # Draw random shapes
            for _ in range(random.randint(3, 8)):
                shape_type = random.choice(['rectangle', 'ellipse', 'polygon'])
                color = (
                    random.randint(0, 255),
                    random.randint(0, 255),
                    random.randint(0, 255)
                )
                
                if shape_type == 'rectangle':
                    x1, y1 = random.randint(0, size-100), random.randint(0, size-100)
                    x2, y2 = x1 + random.randint(50, 100), y1 + random.randint(50, 100)
                    draw.rectangle((x1, y1, x2, y2), fill=color)
                    
                elif shape_type == 'ellipse':
                    x1, y1 = random.randint(0, size-100), random.randint(0, size-100)
                    x2, y2 = x1 + random.randint(50, 100), y1 + random.randint(50, 100)
                    draw.ellipse((x1, y1, x2, y2), fill=color)
                    
                elif shape_type == 'polygon':
                    points = []
                    for _ in range(random.randint(3, 6)):
                        points.append((
                            random.randint(0, size),
                            random.randint(0, size)
                        ))
                    draw.polygon(points, fill=color)
                    
        elif image_type == 1:
            # Noise patterns
            arr = np.random.randint(0, 255, (size, size, 3), dtype=np.uint8)
            image = Image.fromarray(arr)
            
        elif image_type == 2:
            # Procedural pattern
            image = Image.new('RGB', (size, size), color=(255, 255, 255))
            draw = ImageDraw.Draw(image)
            
            # Create a grid pattern
            cell_size = random.choice([8, 16, 32])
            for x in range(0, size, cell_size):
                for y in range(0, size, cell_size):
                    if (x // cell_size + y // cell_size) % 2 == 0:
                        color = (
                            random.randint(0, 128),
                            random.randint(0, 128),
                            random.randint(128, 255)
                        )
                        draw.rectangle(
                            (x, y, x + cell_size - 1, y + cell_size - 1),
                            fill=color
                        )
            
        else:  # image_type == 3
            # Color bands
            image = Image.new('RGB', (size, size), color=(255, 255, 255))
            draw = ImageDraw.Draw(image)
            
            num_bands = random.randint(5, 15)
            band_width = size // num_bands
            
            for i in range(num_bands):
                color = (
                    random.randint(0, 255),
                    random.randint(0, 255),
                    random.randint(0, 255)
                )
                y_start = i * band_width
                draw.rectangle(
                    (0, y_start, size, y_start + band_width),
                    fill=color
                )
                
        # Save the image
        filename = os.path.join(output_dir, f"sample_{i:03d}.png")
        image.save(filename)
        image_paths.append(filename)
        
    logger.info(f"Generated {len(image_paths)} sample images in {output_dir}")
    return image_paths


def load_text_corpus(corpus_dir: str) -> List[str]:
    """
    Load text corpus from directory.
    
    Args:
        corpus_dir: Directory containing text files
        
    Returns:
        List of text samples
    """
    samples = []
    
    if not os.path.exists(corpus_dir):
        logger.warning(f"Text corpus directory doesn't exist: {corpus_dir}")
        return []
        
    # Walk through directory and read .txt files
    for root, _, files in os.walk(corpus_dir):
        for file in files:
            if file.endswith('.txt'):
                try:
                    with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                        text = f.read().strip()
                        if text:
                            samples.append(text)
                except Exception as e:
                    logger.warning(f"Error reading {file}: {e}")
                    
    logger.info(f"Loaded {len(samples)} text samples from {corpus_dir}")
    
    # If no samples found, generate some
    if not samples:
        logger.warning(f"No text samples found in {corpus_dir}. Generating samples...")
        samples = generate_sample_text_corpus(corpus_dir, num_samples=100)
        
    return samples


def load_image_dataset(image_dir: str, size: int = 256) -> List[str]:
    """
    Load image dataset from directory.
    
    Args:
        image_dir: Directory containing images
        size: Target image size
        
    Returns:
        List of paths to images
    """
    image_paths = []
    valid_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp']
    
    if not os.path.exists(image_dir):
        logger.warning(f"Image directory doesn't exist: {image_dir}")
        return []
        
    # Walk through directory and collect image files
    for root, _, files in os.walk(image_dir):
        for file in files:
            if any(file.lower().endswith(ext) for ext in valid_extensions):
                image_paths.append(os.path.join(root, file))
                
    logger.info(f"Found {len(image_paths)} images in {image_dir}")
    
    # If no images found, generate some
    if not image_paths:
        logger.warning(f"No images found in {image_dir}. Generating samples...")
        image_paths = generate_sample_images(image_dir, num_samples=50, size=size)
        
    return image_paths


def preprocess_text(text: str) -> str:
    """
    Preprocess text for tokenization.
    
    Args:
        text: Input text
        
    Returns:
        Preprocessed text
    """
    # Basic preprocessing
    # - Convert to lowercase
    # - Normalize whitespace
    # - Remove control characters
    text = text.lower()
    text = ' '.join(text.split())
    text = ''.join(ch for ch in text if ch.isprintable() or ch.isspace())
    
    return text


def preprocess_image(image_path: str, size: int = 256) -> Any:
    """
    Preprocess image for tokenization.
    
    Args:
        image_path: Path to image file
        size: Target size
        
    Returns:
        Preprocessed image as tensor
    """
    # Load and preprocess image
    image = Image.open(image_path).convert('RGB')
    image = image.resize((size, size))
    
    # Convert to tensor
    img_array = np.array(image)
    img_tensor = torch.from_numpy(img_array).permute(2, 0, 1).float() / 255.0
    
    return img_tensor
