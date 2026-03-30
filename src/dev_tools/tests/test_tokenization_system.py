#!/usr/bin/env python3
"""
ImpressionCore: Test Tokenization System

Module for test tokenization system functionality in the ImpressionCore framework.

File: tests\test_tokenization_system.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [memory-critical, qa, pytorch, production, testing, 2025, object-oriented]
Dependencies: [torch, pathlib, numpy]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements test tokenization system functionality for the
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
from tests.test_tokenization_system import TokenizationSystemTest
instance = TokenizationSystemTest()
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
import unittest
from pathlib import Path

# Add parent directory to path for importing
sys.path.append(str(Path(__file__).parent.parent))

import torch
import numpy as np
from PIL import Image

try:
    from core.tokenization import get_tokenizer
    from core.modal_engine import ModalEngine, ModalityType
    from core.tokenization.integration import TokenizationProcessor
    from core.api import ImpressionCoreAPI
    
    TOKENIZATION_AVAILABLE = True
except ImportError:
    TOKENIZATION_AVAILABLE = False


@unittest.skipIf(not TOKENIZATION_AVAILABLE, "Tokenization components not available")
class TokenizationSystemTest(unittest.TestCase):
    """Integration tests for the tokenization system."""
    
    def setUp(self):
        """Set up test environment."""
        self.text_tokenizer_path = "data/tokenizer/text_tokenizer.json"
        self.image_tokenizer_path = "data/tokenizer/image_tokenizer.pt"
        
        # Skip tests if tokenizers don't exist
        if not os.path.exists(self.text_tokenizer_path) or not os.path.exists(self.image_tokenizer_path):
            self.skipTest("Tokenizer files not found.")
        
        # Load tokenizers
        self.text_tokenizer = get_tokenizer("text", self.text_tokenizer_path)
        self.image_tokenizer = get_tokenizer("image", self.image_tokenizer_path)
        
        # Test content
        self.test_text = "ImpressionCore tokenization system integration test"
        
        # Create a small test image
        self.image_size = 64  # Use small image for tests
        self.test_image = torch.rand(3, self.image_size, self.image_size)
    
    def test_direct_tokenization(self):
        """Test direct use of tokenizers."""
        # Text tokenization
        text_tokens = self.text_tokenizer.encode(self.test_text)
        self.assertIsInstance(text_tokens, list)
        self.assertTrue(len(text_tokens) > 0)
        
        # Text detokenization
        decoded_text = self.text_tokenizer.decode(text_tokens)
        self.assertEqual(decoded_text, self.test_text)
        
        # Image tokenization
        image_tokens = self.image_tokenizer.encode(self.test_image)
        self.assertIsInstance(image_tokens, list)
        self.assertTrue(len(image_tokens) > 0)
        
        # Image detokenization
        decoded_image = self.image_tokenizer.decode(image_tokens)
        self.assertIsInstance(decoded_image, torch.Tensor)
        
    def test_modal_engine_integration(self):
        """Test tokenizers integrated with Modal Engine."""
        engine = ModalEngine()
        
        # Register tokenizers
        engine.register_tokenizer(ModalityType.TEXT, self.text_tokenizer)
        engine.register_tokenizer(ModalityType.IMAGE, self.image_tokenizer)
        
        # Text through engine
        text_tokens = engine.tokenize(self.test_text, ModalityType.TEXT)
        self.assertIsInstance(text_tokens, list)
        decoded_text = engine.detokenize(text_tokens, ModalityType.TEXT)
        self.assertEqual(decoded_text, self.test_text)
        
        # Image through engine
        image_tokens = engine.tokenize(self.test_image, ModalityType.IMAGE)
        self.assertIsInstance(image_tokens, list)
        decoded_image = engine.detokenize(image_tokens, ModalityType.IMAGE)
        self.assertIsInstance(decoded_image, torch.Tensor)
    
    def test_tokenization_processor(self):
        """Test the TokenizationProcessor."""
        processor = TokenizationProcessor()
        
        # Load tokenizers
        processor.load_tokenizer("text", self.text_tokenizer_path)
        processor.load_tokenizer("image", self.image_tokenizer_path)
        
        # Text tokenization
        text_tokens = processor.tokenize(self.test_text, "text")
        self.assertIsInstance(text_tokens, list)
        decoded_text = processor.detokenize(text_tokens, "text")
        self.assertEqual(decoded_text, self.test_text)
        
        # Image tokenization
        image_tokens = processor.tokenize(self.test_image, "image")
        self.assertIsInstance(image_tokens, list)
        decoded_image = processor.detokenize(image_tokens, "image")
        self.assertIsInstance(decoded_image, torch.Tensor)
    
    def test_api(self):
        """Test the high-level API."""
        # Standard API
        api = ImpressionCoreAPI(use_lite_engine=False)
        text_tokens = api.tokenize(self.test_text, "text")
        decoded_text = api.detokenize(text_tokens, "text")
        self.assertEqual(decoded_text, self.test_text)
        
        # Lite API
        lite_api = ImpressionCoreAPI(use_lite_engine=True, memory_efficient=True)
        # Memory optimization: Memory-critical operation
        text_tokens = lite_api.tokenize(self.test_text, "text")
        decoded_text = lite_api.detokenize(text_tokens, "text")
        self.assertEqual(decoded_text, self.test_text)
        

if __name__ == "__main__":
    unittest.main()

import pytest
from src.pipelines.tokenization import MultimodalTokenizer

@pytest.mark.test
def test_text_tokenization():
    """
    Test text tokenization functionality.
    """
    tokenizer = MultimodalTokenizer(text_tokenizer_name="gpt2")
    text = "This is a test."
    tokens = tokenizer.tokenize_text(text)
    
    # Assertions
    assert "input_ids" in tokens, "Tokenized output missing 'input_ids'"
    assert "attention_mask" in tokens, "Tokenized output missing 'attention_mask'"
    assert len(tokens["input_ids"][0]) == tokenizer.max_text_length, "Tokenized output length mismatch"

@pytest.mark.test
def test_image_tokenization():
    """
    Test image tokenization functionality.
    """
    tokenizer = MultimodalTokenizer(image_patch_size=16, max_image_resolution=256)
    from PIL import Image
    image = Image.new("RGB", (256, 256), color="white")
    tokens = tokenizer.tokenize_image(image)
    
    # Assertions
    assert "patch_tokens" in tokens, "Tokenized output missing 'patch_tokens'"
    assert "attention_mask" in tokens, "Tokenized output missing 'attention_mask'"
    assert tokens["patch_tokens"].shape[1] == (256 // 16) ** 2, "Patch token count mismatch"
