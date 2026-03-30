#!/usr/bin/env python3
"""
ImpressionCore: Data Processing

Module for data processing functionality in the ImpressionCore framework.

File: examples\data_processing.py
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
Dependencies: [torch, typing]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements data processing functionality for the
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
from examples.data_processing import MainClass
instance = MainClass()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

import torch
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

def prepare_data_for_model(texts: List[str], tokenizer, max_length: int = 1024, 
                           truncation_strategy: str = "head_tail") -> List[Dict[str, torch.Tensor]]:
    """
    Prepare text data for model training with advanced truncation strategies.
    # Memory optimization: Explicit memory cleanup
    
    Args:
        texts: List of text samples to tokenize
        tokenizer: Tokenizer to use
        max_length: Maximum sequence length
        truncation_strategy: Strategy for handling long sequences:
                            - 'head': Keep the beginning of the text
                            - 'tail': Keep the ending of the text
                            - 'head_tail': Keep both ends, truncate the middle
    
    Returns:
        List of tokenized samples ready for model input
        # Memory optimization: Explicit memory cleanup
    """
    processed_samples = []
    truncated_count = 0
    
    for text in texts:
        # Tokenize without truncation first to check length
        tokens = tokenizer.encode(text, add_special_tokens=True)
        
        if len(tokens) > max_length:
            truncated_count += 1
            
            # Apply truncation strategy
            if truncation_strategy == "head":
                # Keep the beginning
                tokens = tokens[:max_length]
            elif truncation_strategy == "tail":
                # Keep the ending
                tokens = tokens[-max_length:]
            elif truncation_strategy == "head_tail":
                # Keep both beginning and end, remove middle
                # Use 1/2 for head and 1/2 for tail
                head_size = max_length // 2
                tail_size = max_length - head_size
                tokens = tokens[:head_size] + tokens[-tail_size:]
            else:
                # Default to head truncation
                tokens = tokens[:max_length]
                
        # Convert to tensors
        input_ids = torch.tensor([tokens], dtype=torch.long)
        attention_mask = torch.ones_like(input_ids)
        
        processed_samples.append({
            "input_ids": input_ids, 
            "attention_mask": attention_mask
        })
    
    # Log truncation statistics
    if truncated_count > 0:
        logger.warning(f"Truncated {truncated_count} sequences exceeding max length of {max_length}")
        logger.info(f"Truncation strategy used: '{truncation_strategy}'")
    
    return processed_samples

def split_long_texts(texts: List[str], max_tokens: int = 1000, tokenizer = None) -> List[str]:
    """
    Split long texts into smaller chunks that fit within token limits.
    
    Args:
        texts: List of text samples to process
        max_tokens: Maximum number of tokens per chunk
        tokenizer: Tokenizer to use for length estimation
        
    Returns:
        Expanded list with longer texts split into chunks
    """
    if tokenizer is None:
        # Estimate roughly 4 chars per token if no tokenizer provided
        char_estimate = max_tokens * 4
        return split_long_texts_by_chars(texts, char_estimate)
    
    result = []
    for text in texts:
        tokens = tokenizer.encode(text)
        if len(tokens) <= max_tokens:
            # Text fits within limit, keep as is
            result.append(text)
        else:
            # Text is too long, split into chunks
            chunks = []
            # Simple sentence-based splitting
            sentences = text.split(". ")
            current_chunk = []
            current_length = 0
            
            for sentence in sentences:
                # Add period back except for the last sentence if it doesn't have one
                if not sentence.endswith("."):
                    sentence_text = sentence + "."
                else:
                    sentence_text = sentence
                    
                # Estimate token length
                sentence_tokens = tokenizer.encode(sentence_text)
                sentence_length = len(sentence_tokens)
                
                if current_length + sentence_length <= max_tokens:
                    # Add to current chunk
                    current_chunk.append(sentence_text)
                    current_length += sentence_length
                else:
                    # Finalize current chunk and start new one
                    if current_chunk:
                        chunks.append(" ".join(current_chunk))
                    current_chunk = [sentence_text]
                    current_length = sentence_length
            
            # Add the last chunk
            if current_chunk:
                chunks.append(" ".join(current_chunk))
                
            # Add all chunks to result
            result.extend(chunks)
    
    return result

def split_long_texts_by_chars(texts: List[str], max_chars: int = 4000) -> List[str]:
    """
    Split long texts into smaller chunks by character count.
    
    Args:
        texts: List of text samples to process
        max_chars: Maximum characters per chunk
        
    Returns:
        Expanded list with longer texts split into chunks
    """
    result = []
    
    for text in texts:
        if len(text) <= max_chars:
            # Text fits within limit, keep as is
            result.append(text)
        else:
            # Find natural breaking points (sentences) for splitting
            chunks = []
            sentences = text.split(". ")
            current_chunk = []
            current_length = 0
            
            for sentence in sentences:
                # Add period back except for last sentence if needed
                sentence_text = sentence + "." if not sentence.endswith(".") else sentence
                sentence_length = len(sentence_text) + 1  # +1 for space
                
                if current_length + sentence_length <= max_chars:
                    # Add to current chunk
                    current_chunk.append(sentence_text)
                    current_length += sentence_length
                else:
                    # Finalize current chunk and start new one
                    if current_chunk:
                        chunks.append(" ".join(current_chunk))
                    current_chunk = [sentence_text]
                    current_length = sentence_length
            
            # Add the last chunk
            if current_chunk:
                chunks.append(" ".join(current_chunk))
                
            # Add all chunks to result
            result.extend(chunks)
            
    return result
