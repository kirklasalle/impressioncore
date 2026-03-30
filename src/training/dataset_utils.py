#!/usr/bin/env python3
"""
ImpressionCore: Dataset Utils

Module for dataset utils functionality in the ImpressionCore framework.

File: training\dataset_utils.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [training, gpu-optimized, ml, pytorch, production, 2025, object-oriented]
Dependencies: [torch, typing, pathlib, numpy]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements dataset utils functionality for the
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
from training.dataset_utils import DatasetInfo
instance = DatasetInfo()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

import os
import json
import logging
import torch
import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Union, Callable, Iterator
import random
from tqdm import tqdm
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
import hashlib
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class DatasetInfo:
    """Information about a processed dataset"""
    
    name: str
    num_examples: int
    num_tokens: int
    vocab_size: int = 0
    max_length: int = 0
    avg_length: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class DatasetProcessor:
    """Process raw data into training datasets"""
    
    def __init__(
        self,
        output_dir: str,
        tokenizer_path: Optional[str] = None,
        use_huggingface: bool = True
    ):
        """
        Initialize the dataset processor.
        
        Args:
            output_dir: Directory to save processed datasets
            tokenizer_path: Path to tokenizer (if using non-HF tokenizer)
            use_huggingface: Whether to use HuggingFace tokenizers
        """
        self.output_dir = output_dir
        self.tokenizer_path = tokenizer_path
        self.use_huggingface = use_huggingface
        self.tokenizer = None
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Load tokenizer
        self._load_tokenizer()
    
    def _load_tokenizer(self) -> None:
        """Load the appropriate tokenizer"""
        if self.use_huggingface:
            try:
                from transformers import AutoTokenizer
                
                # Use either provided path or default to Llama tokenizer
                if self.tokenizer_path:
                    self.tokenizer = AutoTokenizer.from_pretrained(self.tokenizer_path)
                else:
                    self.tokenizer = AutoTokenizer.from_pretrained("hf-internal-testing/llama-tokenizer")
                    
                logger.info(f"Loaded HuggingFace tokenizer with vocab size {len(self.tokenizer)}")
                
            except ImportError:
                logger.error("Failed to import transformers. Please install via pip install transformers")
                raise
        else:
            # Load custom tokenizer if provided
            if not self.tokenizer_path:
                raise ValueError("tokenizer_path must be provided when use_huggingface=False")
                
            # Implementation would depend on the custom tokenizer format
            logger.info(f"Loading custom tokenizer from {self.tokenizer_path}")
            # self.tokenizer = load_custom_tokenizer(self.tokenizer_path)
    
    def process_text_files(
        self,
        input_files: List[str],
        output_name: str,
        chunk_size: int = 1024,
        max_seq_length: int = 2048,
        shuffle: bool = True,
        num_workers: int = 4
    ) -> DatasetInfo:
        """
        Process text files into a dataset for training.
        
        Args:
            input_files: List of input text file paths
            output_name: Name for the processed dataset
            chunk_size: Size of chunks to process at once
            max_seq_length: Maximum sequence length
            shuffle: Whether to shuffle the data
            num_workers: Number of worker processes for parallel processing
            
        Returns:
            Information about the processed dataset
        """
        # Validate input files
        for file_path in input_files:
            if not os.path.exists(file_path):
                raise ValueError(f"Input file not found: {file_path}")
        
        output_path = os.path.join(self.output_dir, output_name)
        os.makedirs(output_path, exist_ok=True)
        
        # Process files in parallel
        logger.info(f"Processing {len(input_files)} files with {num_workers} workers")
        
        all_tokens = []
        total_tokens = 0
        max_length = 0
        total_length = 0
        
        with ProcessPoolExecutor(max_workers=num_workers) as executor:
            file_futures = []
            
            # Submit file processing tasks
            for file_path in input_files:
                future = executor.submit(
                    self._process_file,
                    file_path,
                    chunk_size,
                    max_seq_length
                )
                file_futures.append(future)
            
            # Collect results
            for future in tqdm(file_futures, desc="Processing files"):
                tokens_list, file_tokens, file_max_len, file_total_len = future.result()
                all_tokens.extend(tokens_list)
                total_tokens += file_tokens
                max_length = max(max_length, file_max_len)
                total_length += file_total_len
        
        # Shuffle if requested
        if shuffle:
            random.shuffle(all_tokens)
        
        # Save as jsonl for easy loading
        jsonl_path = os.path.join(output_path, f"{output_name}.jsonl")
        with open(jsonl_path, 'w') as f:
            for tokens in tqdm(all_tokens, desc="Writing JSONL"):
                f.write(json.dumps({"tokens": tokens.tolist() if isinstance(tokens, np.ndarray) else tokens}) + "\n")
        
        # Save as PyTorch tensor
        pt_path = os.path.join(output_path, f"{output_name}.pt")
        torch.save(all_tokens, pt_path)
        
        # Calculate statistics
        avg_length = total_length / max(1, len(all_tokens))
        vocab_size = len(self.tokenizer) if hasattr(self.tokenizer, '__len__') else 0
        
        # Create and save dataset info
        dataset_info = DatasetInfo(
            name=output_name,
            num_examples=len(all_tokens),
            num_tokens=total_tokens,
            vocab_size=vocab_size,
            max_length=max_length,
            avg_length=avg_length
        )
        
        # Save dataset info
        info_path = os.path.join(output_path, f"{output_name}_info.json")
        with open(info_path, 'w') as f:
            json.dump(dataset_info.__dict__, f, indent=2)
        
        logger.info(f"Processed dataset saved to {output_path}")
        logger.info(f"Dataset stats: {len(all_tokens)} examples, {total_tokens} tokens, avg length {avg_length:.1f}")
        
        
    
    def _process_file(
        self,
        file_path: str,
        chunk_size: int,
        max_seq_length: int
    ) -> Tuple[List[List[int]], int, int, int]:
        """
        Process a single text file.
        
        Args:
            file_path: Path to text file
            chunk_size: Size of chunks to process at once
            max_seq_length: Maximum sequence length
            
        Returns:
            Tuple of (list of token sequences, total tokens, max length, total length)
        """
        tokens_list = []
        total_tokens = 0
        max_length = 0
        total_length = 0
        
        try:
            # Read file in chunks
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read(chunk_size)
                while text:
                    # Tokenize the text chunk
                    tokens = self.tokenizer.encode(text)
                    
                    # Split into sequences of max_seq_length
                    for i in range(0, len(tokens), max_seq_length):
                        seq = tokens[i:i+max_seq_length]
                        tokens_list.append(seq)
                        total_tokens += len(seq)
                        max_length = max(max_length, len(seq))
                        total_length += len(seq)
                    
                    text = f.read(chunk_size)
                    
        except Exception as e:
            logger.error(f"Error processing {file_path}: {str(e)}")
            raise
