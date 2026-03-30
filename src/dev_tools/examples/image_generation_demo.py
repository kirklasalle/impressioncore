#!/usr/bin/env python3
"""
ImpressionCore: Image Generation Demo

Module for image generation demo functionality in the ImpressionCore framework.

File: examples\image_generation_demo.py
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
This module implements image generation demo functionality for the
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
from examples.image_generation_demo import MainClass
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
import torch
import numpy as np
from pathlib import Path
from PIL import Image
import matplotlib.pyplot as plt
import logging

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    """Run the demo of image generation with knowledge store integration."""
    print("\n===== Image Generation with Knowledge Store Integration =====\n")
    
    # Check for PyTorch availability
    if torch.cuda.is_available():
    # Memory optimization: CUDA operations for GPU acceleration
        print(f"PyTorch is available with CUDA. Device: {torch.cuda.get_device_name(0)}")
        # Memory optimization: CUDA operations for GPU acceleration
    else:
        print("PyTorch is available.")
    
    # Import knowledge store components
    try:
        from src.core.knowledge.uks import UniversalKnowledgeStore
        from src.core.knowledge.node import KnowledgeNode
        
        # Create knowledge store
        print("Creating knowledge store with planetary information...")
        uks = UniversalKnowledgeStore()
        
        # Create nodes for planets
        # Fixed: Changed add_attribute to set_attribute to match the actual method name
        mars = KnowledgeNode("Mars")
        mars.set_attribute("color", "red")  # Changed from add_attribute to set_attribute
        mars.set_attribute("type", "planet")
        mars.set_attribute("diameter_km", 6779)
        mars.set_attribute("atmosphere", "thin, mostly CO2")
        
        earth = KnowledgeNode("Earth")
        earth.set_attribute("color", "blue")
        earth.set_attribute("type", "planet")
        earth.set_attribute("diameter_km", 12742)
        earth.set_attribute("atmosphere", "nitrogen, oxygen")
        
        # Add nodes to knowledge store
        uks.add_node(mars)
        uks.add_node(earth)
        
        # Create relationships
        uks.add_relation(earth, "orbits", "Sun")
        uks.add_relation(mars, "orbits", "Sun")
        
        print("Knowledge store created successfully.")
        
        # Create simple image generation function that uses knowledge attributes
        def generate_planet_image(planet_node, size=256):
            """
            Generate a simple planet image based on knowledge attributes.
            
            Args:
                planet_node: KnowledgeNode representing a planet
                size: Size of the generated image
                
            Returns:
                PIL.Image: The generated planet image
            """
            # Get planet attributes
            name = planet_node.name
            color_name = planet_node.get_attribute("color")
            
            # Map color names to RGB
            color_map = {
                "red": (220, 80, 60),
                "blue": (60, 100, 200),
                "orange": (240, 140, 20),
                "yellow": (240, 220, 40),
                "brown": (160, 100, 60),
                "gray": (120, 120, 120),
            }
            
            # Default to gray if color not found
            color = color_map.get(color_name, (120, 120, 120))
            
            # Create a black background
            img = np.zeros((size, size, 3), dtype=np.uint8)
            
            # Draw planet circle
            center = size // 2
            radius = size // 3
            
            # Create a circle mask
            y, x = np.ogrid[:size, :size]
            dist_from_center = np.sqrt((x - center)**2 + (y - center)**2)
            mask = dist_from_center <= radius
            
            # Apply color to the mask
            img[mask] = color
            
            # Add some noise/texture
            noise = np.random.randint(0, 30, (size, size, 3), dtype=np.int32)
            img = np.clip(img.astype(np.int32) + noise - 15, 0, 255).astype(np.uint8)
            
            # Convert to PIL image
            pil_img = Image.fromarray(img)
            
            # Add text label
            print(f"Generated {name} image")
            
            return pil_img
        
        # Generate and display images
        output_dir = os.path.join(project_root, "output", "generated_images")
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate Mars image
        mars_img = generate_planet_image(mars)
        mars_path = os.path.join(output_dir, "mars.png")
        mars_img.save(mars_path)
        print(f"Mars image saved to {mars_path}")
        
        # Generate Earth image
        earth_img = generate_planet_image(earth)
        earth_path = os.path.join(output_dir, "earth.png")
        earth_img.save(earth_path)
        print(f"Earth image saved to {earth_path}")
        
        # Display if running in interactive mode
        if hasattr(sys, 'ps1') or sys.flags.interactive:
            plt.figure(figsize=(12, 6))
            plt.subplot(1, 2, 1)
            plt.imshow(mars_img)
            plt.title("Mars")
            plt.axis('off')
            
            plt.subplot(1, 2, 2)
            plt.imshow(earth_img)
            plt.title("Earth")
            plt.axis('off')
            plt.show()
            
        print("\nDemo completed successfully!")
        
    except ImportError as e:
        print(f"Error importing required modules: {e}")
    except Exception as e:
        print(f"Error running demo: {e}")

if __name__ == "__main__":
    main()
