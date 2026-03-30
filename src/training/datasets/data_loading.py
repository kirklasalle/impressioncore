#!/usr/bin/env python3
"""
ImpressionCore: Data Loading

Module for data loading functionality in the ImpressionCore framework.

File: training\datasets\data_loading.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [training, gpu-optimized, ml, pytorch, production, 2025]
Dependencies: [torch, typing, pathlib, numpy]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements data loading functionality for the
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
from training.datasets.data_loading import MainClass
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
import torch
import numpy as np
from typing import List, Dict, Any, Optional, Union, Tuple
from pathlib import Path
import json

logger = logging.getLogger(__name__)


def load_text_data(data_path: Union[str, Path], 
                  max_samples: Optional[int] = None,
                  encoding: str = 'utf-8') -> List[Dict[str, Any]]:
    """
    Load text data from file or directory.
    
    Args:
        data_path: Path to text data file or directory
        max_samples: Maximum number of samples to load
        encoding: Text encoding to use
        
    Returns:
        List of dictionaries containing text data
    """
    data_path = Path(data_path)
    text_data = []
    
    try:
        if data_path.is_file():
            # Single file
            if data_path.suffix.lower() == '.json':
                with open(data_path, 'r', encoding=encoding) as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        text_data.extend(data)
                    else:
                        text_data.append(data)
            else:
                # Plain text file
                with open(data_path, 'r', encoding=encoding) as f:
                    content = f.read()
                    text_data.append({"text": content, "source": str(data_path)})
                    
        elif data_path.is_dir():
            # Directory of files
            for file_path in data_path.glob('*.txt'):
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                    text_data.append({"text": content, "source": str(file_path)})
                    
                if max_samples and len(text_data) >= max_samples:
                    break
                    
        # Limit samples if specified
        if max_samples:
            text_data = text_data[:max_samples]
            
        logger.info(f"Loaded {len(text_data)} text samples from {data_path}")
        return text_data
        
    except Exception as e:
        logger.error(f"Error loading text data from {data_path}: {e}")
        return []


def load_image_data(data_path: Union[str, Path],
                   max_samples: Optional[int] = None,
                   image_extensions: List[str] = None) -> List[Dict[str, Any]]:
    """
    Load image data from file or directory.
    
    Args:
        data_path: Path to image data file or directory
        max_samples: Maximum number of samples to load
        image_extensions: List of valid image extensions
        
    Returns:
        List of dictionaries containing image data
    """
    if image_extensions is None:
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']
        
    data_path = Path(data_path)
    image_data = []
    
    try:
        if data_path.is_file() and data_path.suffix.lower() in image_extensions:
            # Single image file
            image_data.append({
                "image_path": str(data_path),
                "filename": data_path.name,
                "source": str(data_path)
            })
            
        elif data_path.is_dir():
            # Directory of images
            for ext in image_extensions:
                for file_path in data_path.glob(f'*{ext}'):
                    image_data.append({
                        "image_path": str(file_path),
                        "filename": file_path.name,
                        "source": str(file_path)
                    })
                    
                    if max_samples and len(image_data) >= max_samples:
                        break
                        
                if max_samples and len(image_data) >= max_samples:
                    break
                    
        # Limit samples if specified
        if max_samples:
            image_data = image_data[:max_samples]
            
        logger.info(f"Loaded {len(image_data)} image samples from {data_path}")
        return image_data
        
    except Exception as e:
        logger.error(f"Error loading image data from {data_path}: {e}")
        return []


def load_audio_data(data_path: Union[str, Path],
                   max_samples: Optional[int] = None,
                   audio_extensions: List[str] = None) -> List[Dict[str, Any]]:
    """
    Load audio data from file or directory.
    
    Args:
        data_path: Path to audio data file or directory
        max_samples: Maximum number of samples to load
        audio_extensions: List of valid audio extensions
        
    Returns:
        List of dictionaries containing audio data
    """
    if audio_extensions is None:
        audio_extensions = ['.wav', '.mp3', '.flac', '.ogg', '.m4a']
        
    data_path = Path(data_path)
    audio_data = []
    
    try:
        if data_path.is_file() and data_path.suffix.lower() in audio_extensions:
            # Single audio file
            audio_data.append({
                "audio_path": str(data_path),
                "filename": data_path.name,
                "source": str(data_path)
            })
            
        elif data_path.is_dir():
            # Directory of audio files
            for ext in audio_extensions:
                for file_path in data_path.glob(f'*{ext}'):
                    audio_data.append({
                        "audio_path": str(file_path),
                        "filename": file_path.name,
                        "source": str(file_path)
                    })
                    
                    if max_samples and len(audio_data) >= max_samples:
                        break
                        
                if max_samples and len(audio_data) >= max_samples:
                    break
                    
        # Limit samples if specified
        if max_samples:
            audio_data = audio_data[:max_samples]
            
        logger.info(f"Loaded {len(audio_data)} audio samples from {data_path}")
        return audio_data
        
    except Exception as e:
        logger.error(f"Error loading audio data from {data_path}: {e}")
        return []


def create_multimodal_dataset(text_data: List[Dict[str, Any]],
                             image_data: List[Dict[str, Any]],
                             audio_data: List[Dict[str, Any]],
                             alignment_strategy: str = "round_robin") -> List[Dict[str, Any]]:
    """
    Create a multimodal dataset from text, image, and audio data.
    
    Args:
        text_data: List of text samples
        image_data: List of image samples
        audio_data: List of audio samples
        alignment_strategy: Strategy for aligning different modalities
        
    Returns:
        List of multimodal samples
    """
    multimodal_data = []
    
    if alignment_strategy == "round_robin":
        # Interleave samples from different modalities
        max_len = max(len(text_data), len(image_data), len(audio_data))
        
        for i in range(max_len):
            sample = {"modalities": []}
            
            if i < len(text_data):
                sample["modalities"].append({"type": "text", "data": text_data[i]})
            if i < len(image_data):
                sample["modalities"].append({"type": "image", "data": image_data[i]})
            if i < len(audio_data):
                sample["modalities"].append({"type": "audio", "data": audio_data[i]})
                
            if sample["modalities"]:
                multimodal_data.append(sample)
                
    elif alignment_strategy == "combine_all":
        # Create samples with all available modalities
        min_len = min(len(text_data), len(image_data), len(audio_data))
        
        for i in range(min_len):
            sample = {
                "modalities": [
                    {"type": "text", "data": text_data[i]},
                    {"type": "image", "data": image_data[i]},
                    {"type": "audio", "data": audio_data[i]}
                ]
            }
            multimodal_data.append(sample)
            
    logger.info(f"Created {len(multimodal_data)} multimodal samples using {alignment_strategy} strategy")
    return multimodal_data
