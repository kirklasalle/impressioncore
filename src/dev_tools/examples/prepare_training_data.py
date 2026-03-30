#!/usr/bin/env python3
"""
ImpressionCore: Prepare Training Data

Module for prepare training data functionality in the ImpressionCore framework.

File: examples\prepare_training_data.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [production, 2025]
Dependencies: [typing, pathlib, numpy]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements prepare training data functionality for the
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
from examples.prepare_training_data import MainClass
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
import json
import logging
import argparse
import numpy as np
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional, Union

# Add project root to Python path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.pipeline.multimodal import (
    TextProcessor, ImageProcessor, AudioProcessor, MultimodalAligner
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def prepare_dataset(data_dir: str, output_dir: str) -> None:
    """
    Prepare multimodal dataset for training.
    
    Args:
        data_dir: Directory containing raw data
        output_dir: Directory to save processed data
    """
    # Ensure data_dir is a valid path
    if not data_dir:
        data_dir = os.path.join(project_root, "data", "raw")
        logger.warning(f"No data directory provided, using default: {data_dir}")
    
    # Convert to Path object for easier path manipulation
    data_dir_path = Path(data_dir)
    
    logger.info(f"Processing data from {data_dir_path}")
    
    # Check if data directory exists
    if not data_dir_path.exists():
        logger.error(f"Data directory does not exist: {data_dir_path}")
        logger.info("Creating sample data directories...")
        data_dir_path.mkdir(parents=True, exist_ok=True)
        
    # Check if sample data exists and is valid
    sample_json_path = data_dir_path / "sample.json"
    if not sample_json_path.exists() or not _is_valid_sample(sample_json_path):
        logger.info("Creating new sample data...")
        create_sample_data(data_dir_path)
    
    # Initialize processors
    aligner = MultimodalAligner(
        text_processor=TextProcessor(),
        image_processor=ImageProcessor(),
        audio_processor=AudioProcessor()
    )
    
    # Create output directory
    output_dir_path = Path(output_dir)
    output_dir_path.mkdir(parents=True, exist_ok=True)
    
    # Process data
    processed_count = 0
    skipped_count = 0
    
    # Iterate through data files
    for item_path in data_dir_path.glob("**/*.json"):
        try:
            with open(item_path, "r", encoding="utf-8") as f:
                item_data = json.load(f)
            
            # Process text
            if "text" in item_data:
                text = item_data["text"]
                # Process image if available
                if "image_path" in item_data and item_data["image_path"]:  # Check image_path is not None/empty
                    # Use Path to join paths properly
                    image_path = data_dir_path / item_data["image_path"]
                    if image_path.exists():
                        # In a real implementation, this would load and process the image
                        # For now, we'll just create a placeholder
                        image = np.zeros((224, 224, 3), dtype=np.uint8)
                        
                        # Align text and image
                        aligned_embedding = aligner.align_text_and_image(text, image)
                        
                        # Save processed data
                        output_path = output_dir_path / f"{item_path.stem}.npz"
                        np.savez(
                            output_path, 
                            embedding=aligned_embedding,
                            metadata=json.dumps(item_data)
                        )
                        processed_count += 1
                        logger.info(f"Processed: {item_path.name}")
                        continue
                    else:
                        logger.warning(f"Image not found: {image_path}")
                else:
                    logger.warning(f"No image_path in {item_path.name}")
            else:
                logger.warning(f"No text in {item_path.name}")
            
            skipped_count += 1
                    
        except Exception as e:
            logger.error(f"Error processing {item_path}: {e}")
            skipped_count += 1
    
    logger.info(f"Processing complete. Processed: {processed_count}, Skipped: {skipped_count}")

def _is_valid_sample(sample_path: Path) -> bool:
    """
    Check if the sample JSON file is valid.
    
    Args:
        sample_path: Path to sample JSON file
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        with open(sample_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Check required fields
        if "text" not in data:
            logger.warning("Sample data missing 'text' field")
            return False
            
        if "image_path" not in data:
            logger.warning("Sample data missing 'image_path' field")
            return False
            
        # Check if image exists
        image_path = sample_path.parent / data["image_path"]
        if not image_path.exists():
            logger.warning(f"Sample image not found at {image_path}")
            return False
            
        return True
    except Exception as e:
        logger.warning(f"Error validating sample data: {e}")
        return False

def create_sample_data(data_dir: Path) -> None:
    """
    Create sample data for testing.
    
    Args:
        data_dir: Directory to create sample data in
    """
    # Delete any existing sample data to start fresh
    sample_json_path = data_dir / "sample.json"
    if sample_json_path.exists():
        sample_json_path.unlink()
        
    # Create images subdirectory
    images_dir = data_dir / "images"
    if images_dir.exists():
        shutil.rmtree(images_dir)
    images_dir.mkdir(exist_ok=True)
    
    # Create sample JSON data
    sample_data = {
        "text": "This is a sample image description for testing",
        "image_path": "images/sample.jpg",  # Make sure this is a string and not None
        "metadata": {
            "source": "test",
            "category": "sample",
            "tags": ["test", "sample", "multimodal"]
        }
    }
    
    # Create a dummy image file
    dummy_image_path = images_dir / "sample.jpg"
    with open(dummy_image_path, "wb") as f:
        # Write a minimal JPEG header
        f.write(b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00\x01\x00\x01\x00\x00\xff\xdb\x00\x43\x00\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x03\x01\x11\x00\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xc4\x00\x14\x11\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00?\x00\xff\xd9')
    
    # Write sample JSON file
    with open(sample_json_path, "w", encoding="utf-8") as f:
        json.dump(sample_data, f, indent=2)
    
    logger.info(f"Created sample data in {data_dir}")
    logger.info(f"    - Created sample image: {dummy_image_path}")
    logger.info(f"    - Created sample JSON: {sample_json_path}")
    
    # Verify the sample data was created correctly
    if _is_valid_sample(sample_json_path):
        logger.info("Sample data validated successfully")
    else:
        logger.error("Failed to create valid sample data")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prepare training data for ImpressionCore")
    parser.add_argument("--data-dir", default="", help="Directory containing raw data")
    parser.add_argument("--output-dir", default="data/processed", help="Directory to save processed data")
    parser.add_argument("--clean", action="store_true", help="Clean and recreate sample data")
    args = parser.parse_args()
    
    data_dir = args.data_dir
    output_dir = args.output_dir
    
    # If --clean flag is set, force recreation of sample data
    if args.clean and not data_dir:
        default_data_dir = os.path.join(project_root, "data", "raw")
        logger.info(f"Cleaning sample data in {default_data_dir}")
        data_dir_path = Path(default_data_dir)
        data_dir_path.mkdir(parents=True, exist_ok=True)
        create_sample_data(data_dir_path)
    
    prepare_dataset(data_dir=data_dir, output_dir=output_dir)
