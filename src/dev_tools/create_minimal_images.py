#!/usr/bin/env python3
"""
Create minimal synthetic images for ImpressionCore training.
"""
import numpy as np
from PIL import Image
import os

def create_minimal_images():
    """Create minimal synthetic images for testing."""
    output_dir = "src/data/minimal_datasets/images"
    os.makedirs(output_dir, exist_ok=True)
    
    # Create 5 simple synthetic images
    for i in range(1, 6):
        # Create a simple pattern image (64x64 RGB)
        img_array = np.zeros((64, 64, 3), dtype=np.uint8)
        
        # Different patterns for each image
        if i == 1:
            # Gradient
            for x in range(64):
                img_array[:, x, 0] = x * 4  # Red gradient
        elif i == 2:
            # Checkerboard
            for x in range(64):
                for y in range(64):
                    if (x // 8 + y // 8) % 2:
                        img_array[y, x] = [255, 255, 255]
        elif i == 3:
            # Circle
            center = 32
            for x in range(64):
                for y in range(64):
                    dist = ((x - center) ** 2 + (y - center) ** 2) ** 0.5
                    if dist < 20:
                        img_array[y, x] = [0, 255, 0]  # Green circle
        elif i == 4:
            # Stripes
            for y in range(64):
                if (y // 4) % 2:
                    img_array[y, :] = [0, 0, 255]  # Blue stripes
        else:
            # Random noise
            img_array = np.random.randint(0, 256, (64, 64, 3), dtype=np.uint8)
        
        # Save image
        img = Image.fromarray(img_array)
        img.save(f"{output_dir}/sample_{i:03d}.jpg")
        print(f"Created {output_dir}/sample_{i:03d}.jpg")

if __name__ == "__main__":
    create_minimal_images()
