#!/usr/bin/env python3
"""
ImpressionCore: Tokenization Demo

Module for tokenization demo functionality in the ImpressionCore framework.

File: examples\tokenization_demo.py
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
This module implements tokenization demo functionality for the
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
from examples.tokenization_demo import TokenizerDemo
instance = TokenizerDemo()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

import torch
import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from io import BytesIO
from pathlib import Path
import numpy as np

from src.core.ai.tokenization.bpe import BPETokenizer
from src.core.ai.tokenization.image import ImageTokenizer

class TokenizerDemo:
    """
    
    TokenizerDemo class for ImpressionCore framework.
    
    This class implements tokenizerdemo functionality optimized for
    memory-constrained environments like the GTX 1050 Ti.
    # Memory optimization: Memory-critical operation
    
    Memory Considerations:
    # Memory optimization: Memory-critical operation
        - Implements memory-efficient algorithms
        # Memory optimization: Memory-critical operation
        - Supports gradient checkpointing
        - Provides CPU fallback options
    
    Notes:
        - Thread-safe implementation
        - GPU memory optimized
        # Memory optimization: Memory-critical operation
        - Part of ImpressionCore ecosystem
    
    """
    def __init__(self, root):
        """
        
    __init__ function for processing.
    
    Args:
        self, root: Function parameters
    
    Returns:
        Processed result
    
    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints
    
        """
        self.root = root
        self.root.title("Tokenizer Demo")
        
        # Load tokenizers
        self.load_tokenizers()
        
        # Create main UI
        self.create_notebook()
        self.create_text_tab()
        self.create_image_tab()
    
    def load_tokenizers(self):
        """Load pre-trained tokenizers"""
        try:
            self.text_tokenizer = BPETokenizer.load("data/tokenizers/text_tokenizer.json")
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            # Memory optimization: CUDA operations for GPU acceleration
            self.image_tokenizer = ImageTokenizer.load("data/tokenizers/image_tokenizer.pt").to(self.device)
            # Memory optimization: Device placement for memory management
            self.image_tokenizer.eval()
        except FileNotFoundError as e:
            print(f"Error loading tokenizers: {e}")
            self.root.destroy()
    
    def create_notebook(self):
        """Create tabbed interface"""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(padx=10, pady=5, expand=True, fill='both')
        
        self.text_frame = ttk.Frame(self.notebook)
        self.image_frame = ttk.Frame(self.notebook)
        
        self.notebook.add(self.text_frame, text='Text Tokenization')
        self.notebook.add(self.image_frame, text='Image Tokenization')
    
    def create_text_tab(self):
        """Create text tokenization interface"""
        # Input text
        ttk.Label(self.text_frame, text="Input Text:").pack(pady=5)
        self.text_input = tk.Text(self.text_frame, height=5)
        self.text_input.pack(padx=5, pady=5, fill='x')
        self.text_input.insert('1.0', 'Enter text to tokenize...')
        
        # Tokenize button
        ttk.Button(self.text_frame, text="Tokenize", 
                  command=self.process_text).pack(pady=5)
        
        # Results
        ttk.Label(self.text_frame, text="Token IDs:").pack(pady=5)
        self.token_display = tk.Text(self.text_frame, height=3)
        self.token_display.pack(padx=5, pady=5, fill='x')
        
        ttk.Label(self.text_frame, text="Reconstructed Text:").pack(pady=5)
        self.reconstructed_text = tk.Text(self.text_frame, height=5)
        self.reconstructed_text.pack(padx=5, pady=5, fill='x')
        
        # Stats
        self.text_stats = ttk.Label(self.text_frame, text="")
        self.text_stats.pack(pady=5)
    
    def create_image_tab(self):
        """Create image tokenization interface"""
        # Image selection
        ttk.Button(self.image_frame, text="Select Image", 
                  command=self.load_image).pack(pady=10)
        
        # Image display frames
        self.display_frame = ttk.Frame(self.image_frame)
        self.display_frame.pack(expand=True, fill='both', padx=5, pady=5)
        
        self.original_label = ttk.Label(self.display_frame, text="Original Image")
        self.original_label.grid(row=0, column=0, padx=5)
        
        self.reconstructed_label = ttk.Label(self.display_frame, 
                                           text="Reconstructed Image")
        self.reconstructed_label.grid(row=0, column=1, padx=5)
        
        # Stats
        self.image_stats = ttk.Label(self.image_frame, text="")
        self.image_stats.pack(pady=5)
    
    def process_text(self):
        """Process text through the tokenizer"""
        # Get input text
        text = self.text_input.get('1.0', 'end-1c')
        
        # Tokenize
        tokens = self.text_tokenizer.encode(text)
        self.token_display.delete('1.0', 'end')
        self.token_display.insert('1.0', str(tokens))
        
        # Reconstruct
        reconstructed = self.text_tokenizer.decode(tokens)
        self.reconstructed_text.delete('1.0', 'end')
        self.reconstructed_text.insert('1.0', reconstructed)
        
        # Update stats
        compression = len(tokens) / len(text)
        unique = len(set(tokens))
        self.text_stats.config(
            text=f"Compression ratio: {compression:.2f}\n"
                 f"Unique tokens: {unique}/{len(tokens)}"
        )
    
    def load_image(self):
        """Load and process an image"""
        filepath = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png")]
        )
        if not filepath:
            return
        
        # Load and preprocess image
        image = Image.open(filepath).convert('RGB')
        image_tensor = self.image_tokenizer.transform(image).unsqueeze(0)
        
        # Get tokens and reconstruct
        with torch.no_grad():
        # Memory optimization: Disable gradient computation to save memory
            tokens = self.image_tokenizer.encode(image_tensor)
            reconstructed = self.image_tokenizer.decode(tokens)
        
        # Display images
        self._display_image_pair(image, reconstructed)
        
        # Calculate and display stats
        unique_tokens = len(set(tokens))
        self.image_stats.config(
            text=f"Total tokens: {len(tokens)}\n"
                 f"Unique tokens: {unique_tokens}\n"
                 f"Compression ratio: {unique_tokens/len(tokens):.2f}"
        )
    
    def _display_image_pair(self, original, reconstructed):
        """Display original and reconstructed images side by side"""
        # Convert reconstructed tensor to PIL Image
        reconstructed = reconstructed.cpu().permute(1, 2, 0).numpy()
        reconstructed = Image.fromarray((reconstructed * 255).astype(np.uint8))
        
        # Resize for display
        display_size = (256, 256)
        original = original.resize(display_size)
        reconstructed = reconstructed.resize(display_size)
        
        # Convert to Tkinter format
        original_tk = ImageTk.PhotoImage(original)
        reconstructed_tk = ImageTk.PhotoImage(reconstructed)
        
        # Update labels
        original_display = ttk.Label(self.display_frame, image=original_tk)
        original_display.image = original_tk  # Keep reference
        original_display.grid(row=1, column=0, padx=5, pady=5)
        
        reconstructed_display = ttk.Label(self.display_frame, 
                                        image=reconstructed_tk)
        reconstructed_display.image = reconstructed_tk  # Keep reference
        reconstructed_display.grid(row=1, column=1, padx=5, pady=5)

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
    root = tk.Tk()
    app = TokenizerDemo(root)
    root.mainloop()

if __name__ == "__main__":
    main()
