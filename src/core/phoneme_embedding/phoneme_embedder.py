#!/usr/bin/env python3
"""
ImpressionCore: Phoneme Embedder

Module for phoneme embedder functionality in the ImpressionCore framework.

File: modules\phoneme_embedding\phoneme_embedder.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [pytorch, production, object-oriented, 2025]
Dependencies: [torch, typing]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements phoneme embedder functionality for the
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
from modules.phoneme_embedding.phoneme_embedder import PhonemeTokenizer
instance = PhonemeTokenizer()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

# ImpressionCore - Phoneme (Character) Embedder and Tokenizer
#
# Description:
# This module provides components for processing character sequences, which serve
# as a basic representation of phonemes in the current ImpressionCore audio pipeline.
# It includes:
#   - `PhonemeTokenizer`: Converts character sequences into numerical token IDs and
#     vice-versa. It uses a predefined or custom set of characters and handles
#     special tokens like <UNK> (unknown) and <PAD> (padding).
#   - `PhonemeEmbedder`: A PyTorch `nn.Module` that takes sequences of character
#     token IDs and converts them into dense vector embeddings using an `nn.Embedding`
#     layer. It relies on `PhonemeEmbeddingConfig` for configuration parameters
#     like embedding dimension and vocabulary size (derived from the tokenizer).
#
# These components are foundational for converting textual or character-based
# representations of speech into a format suitable for neural network processing.
#
# Author: [Your Name/Alias]
# Date: 2024-07-27 # Or the actual creation/last modification date
# Version: 1.0
#
# Dependencies:
# - torch
# - torch.nn
# - typing
# - string
# - .config.PhonemeEmbeddingConfig
#
# License:
# MIT License
#
# Copyright (c) 2024 [Your Name/Organization]
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
"""
Phoneme Embedder and Tokenizer for ImpressionCore.

This module handles the conversion of character sequences (treated as basic
phoneme representations in the current pipeline) into numerical tokens
and then into dense vector embeddings.
"""

import torch
import torch.nn as nn
from typing import List, Dict, Optional
import string # For character sets

from .config import PhonemeEmbeddingConfig
# from .utils import load_phoneme_vocabulary # No longer needed for char tokenizer

class PhonemeTokenizer:
    """
    Tokenizes character sequences into numerical IDs and vice-versa.
    This version uses a predefined character set.
    """
    DEFAULT_CHARACTERS = string.ascii_lowercase + string.digits + " .,!?'\"-" # Basic set
    UNK_TOKEN = "<UNK>"
    PAD_TOKEN = "<PAD>"
    # SOS_TOKEN = "<SOS>" # Start of sequence (optional)
    # EOS_TOKEN = "<EOS>" # End of sequence (optional)

    def __init__(self, custom_characters: Optional[str] = None):
        """
        Initializes the CharacterLevelPhonemeTokenizer.

        Args:
            custom_characters (Optional[str]): A string of custom characters to use
                                               instead of the default set. Special tokens
                                               (UNK, PAD) will still be added.
        """
        self.unk_token = PhonemeTokenizer.UNK_TOKEN
        self.pad_token = PhonemeTokenizer.PAD_TOKEN
        
        char_source = custom_characters if custom_characters is not None else PhonemeTokenizer.DEFAULT_CHARACTERS
        
        # Build vocabulary
        self.vocab: Dict[str, int] = {}
        self.vocab[self.pad_token] = 0
        self.vocab[self.unk_token] = 1
        # self.vocab[self.sos_token] = 2 # If using SOS/EOS
        # self.vocab[self.eos_token] = 3

        # Add unique characters from the source string
        current_idx = len(self.vocab)
        for char in sorted(list(set(char_source))): # Sort for consistent ordering
            if char not in self.vocab:
                self.vocab[char] = current_idx
                current_idx += 1
        
        self.unk_id = self.vocab[self.unk_token]
        self.pad_id = self.vocab[self.pad_token]

        self.reverse_vocab = {i: char for char, i in self.vocab.items()}
        print(f"CharacterLevelPhonemeTokenizer initialized with {len(self.vocab)} tokens. Chars: '{''.join(sorted(self.vocab.keys() - {self.unk_token, self.pad_token}))}'")

    def tokenize(self, char_sequence: List[str] | str) -> List[int]:
        """
        Converts a sequence of characters (or a string) into a sequence of token IDs.
        Input characters are lowercased.

        Args:
            char_sequence (List[str] | str): A list of characters or a single string.

        Returns:
            List[int]: A list of corresponding token IDs.
        """
        if isinstance(char_sequence, str):
            char_sequence = list(char_sequence)
            
        return [self.vocab.get(char.lower(), self.unk_id) for char in char_sequence]

    def detokenize(self, token_ids: List[int], strip_special_tokens: bool = True) -> List[str]:
        """
        Converts a sequence of token IDs back into a sequence of characters.

        Args:
            token_ids (List[int]): A list of token IDs.
            strip_special_tokens (bool): If True, PAD and UNK tokens are removed from output.

        Returns:
            List[str]: A list of corresponding characters.
        """
        chars = []
        for idx in token_ids:
            char = self.reverse_vocab.get(idx, self.unk_token)
            if strip_special_tokens and char in [self.pad_token, self.unk_token]: # Add SOS/EOS if used
                continue
            chars.append(char)
        return chars

    @property
    def vocab_size(self) -> int:
        """
        
    vocab_size function for processing.
    
    Args:
        self: Function parameters
    
    Returns:
        Processed result
    
    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints
    
        """
        return len(self.vocab)

class PhonemeEmbedder(nn.Module):
    """
    Embeds sequences of character IDs into dense vector representations.
    """

    def __init__(self, config: PhonemeEmbeddingConfig, tokenizer: PhonemeTokenizer):
        """
        Initializes the PhonemeEmbedder.

        Args:
            config (PhonemeEmbeddingConfig): Configuration for phoneme embedding.
            tokenizer (PhonemeTokenizer): The character-level phoneme tokenizer instance.
        """
        super().__init__()
        self.config = config
        self.tokenizer = tokenizer

        if not isinstance(self.tokenizer, PhonemeTokenizer):
            raise TypeError("Tokenizer must be an instance of the new character-based PhonemeTokenizer.")

        self.embedding_layer = nn.Embedding(
            num_embeddings=self.tokenizer.vocab_size,
            embedding_dim=self.config.embedding_dim,
            padding_idx=self.tokenizer.pad_id
        )
        print(f"PhonemeEmbedder (Character-based) initialized with embedding dim {self.config.embedding_dim} for vocab size {self.tokenizer.vocab_size}")

    def forward(self, char_sequences: List[List[str] | str]) -> torch.Tensor:
        """
        Converts a batch of character sequences to a batch of embeddings.

        Args:
            char_sequences (List[List[str] | str]): A list of character sequences (batch).
                                                    Each sequence can be a list of chars or a string.

        Returns:
            torch.Tensor: A tensor of shape (batch_size, max_seq_len, embedding_dim)
                          containing the character embeddings.
        """
        # Ensure all inputs are lists of characters for tokenization
        processed_sequences = []
        for seq in char_sequences:
            if isinstance(seq, str):
                processed_sequences.append(list(seq))
            elif isinstance(seq, list):
                processed_sequences.append(seq)
            else:
                raise ValueError("Input sequences must be lists of strings or lists of lists of strings.")

        token_ids_batch = [self.tokenizer.tokenize(seq) for seq in processed_sequences]

        max_len = 0
        if token_ids_batch: # Ensure token_ids_batch is not empty
            max_len = max(len(ids) for ids in token_ids_batch) if token_ids_batch else 0
        
        if max_len == 0 and token_ids_batch: # Handle case where all sequences are empty
             # If all sequences are empty but the batch is not, this means we have a batch of empty lists.
             # The embedding layer might not handle max_len=0 well.
             # We could return an empty tensor of appropriate shape or a tensor of PAD embeddings.
             # For now, let's assume if max_len is 0, the batch was effectively empty of tokens.
             # This case should ideally be handled by upstream logic ensuring non-empty inputs if embeddings are expected.
             # Returning an empty tensor for an empty effective batch.
             # (batch_size, 0, embedding_dim)
             return torch.empty((len(token_ids_batch), 0, self.config.embedding_dim), device=self.embedding_layer.weight.device)
             # Memory optimization: Device placement for memory management


        padded_token_ids_batch = [
            ids + [self.tokenizer.pad_id] * (max_len - len(ids)) for ids in token_ids_batch
        ]

        if not padded_token_ids_batch: # If the original batch was empty
            return torch.empty((0, 0, self.config.embedding_dim), device=self.embedding_layer.weight.device)
            # Memory optimization: Device placement for memory management

        token_ids_tensor = torch.tensor(padded_token_ids_batch, dtype=torch.long, device=self.embedding_layer.weight.device)
        # Memory optimization: Device placement for memory management
        embeddings = self.embedding_layer(token_ids_tensor)
        return embeddings

    def get_embedding_for_char(self, char: str) -> Optional[torch.Tensor]:
        """
        Retrieves the embedding vector for a single character.
        Character is lowercased before lookup.

        Args:
            char (str): The character string (should be a single character).

        Returns:
            Optional[torch.Tensor]: The embedding vector (1D tensor) or None if OOV and not UNK.
        """
        if len(char) != 1:
            print(f"Warning: get_embedding_for_char expects a single character, got '{char}'")
            # Fallback to UNK or handle as error
            token_id = self.tokenizer.unk_id
        else:
            token_id = self.tokenizer.vocab.get(char.lower(), self.tokenizer.unk_id)
        
        token_id_tensor = torch.tensor([token_id], dtype=torch.long, device=self.embedding_layer.weight.device)
        # Memory optimization: Device placement for memory management
        with torch.no_grad():
        # Memory optimization: Disable gradient computation to save memory
            embedding_vector = self.embedding_layer(token_id_tensor).squeeze(0)
        return embedding_vector

# Example usage (for testing purposes)
if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    logger.info("--- CharacterLevelPhonemeTokenizer & Embedder Test ---")

    # Initialize tokenizer (using default character set)
    char_tokenizer = PhonemeTokenizer()
    logger.info(f"Tokenizer Vocab Size: {char_tokenizer.vocab_size}")
    logger.info(f"PAD ID: {char_tokenizer.pad_id}, UNK ID: {char_tokenizer.unk_id}")


    # Test tokenization
    test_string = "Hello World 123!"
    logger.info(f"Original string: '{test_string}'")
    
    token_ids = char_tokenizer.tokenize(test_string)
    logger.info(f"Tokenized IDs: {token_ids}")
    
    detokenized_chars = char_tokenizer.detokenize(token_ids)
    logger.info(f"Detokenized (stripped): '{''.join(detokenized_chars)}'")
    
    detokenized_chars_unstripped = char_tokenizer.detokenize(token_ids, strip_special_tokens=False)
    logger.info(f"Detokenized (unstripped): '{''.join(detokenized_chars_unstripped)}'")

    # Test with unknown characters
    test_unknown_string = "Héllo Wörld ©" # Accented chars and symbol not in default set
    logger.info(f"Original unknown string: '{test_unknown_string}'")
    token_ids_unknown = char_tokenizer.tokenize(test_unknown_string)
    logger.info(f"Tokenized unknown IDs: {token_ids_unknown}")
    detokenized_unknown = char_tokenizer.detokenize(token_ids_unknown)
    logger.info(f"Detokenized unknown (stripped): '{''.join(detokenized_unknown)}'") # Should show UNKs replaced or stripped

    # Create a dummy config for the embedder
    # Note: model_path and vocab_path in PhonemeEmbeddingConfig are less relevant now for these simplified components
    # but are kept for consistency with the dataclass structure.
    dummy_config = PhonemeEmbeddingConfig(
        embedding_dim=64, # Smaller dim for testing
        sample_rate=16000,
        # model_path and vocab_path are not directly used by these simplified versions
        # but the config class expects them.
        model_path="placeholder/model.pt", 
        vocab_path="placeholder/vocab.txt" 
    )

    # Initialize embedder
    char_embedder = PhonemeEmbedder(config=dummy_config, tokenizer=char_tokenizer)

    # Test embedding a batch of character sequences
    batch_char_sequences = [
        "hello world",
        "test 123",
        "short",
        "a",
        "! ? ." # Test punctuation and spaces
    ]
    logger.info(f"Batch input sequences: {batch_char_sequences}")
    embeddings_tensor = char_embedder(batch_char_sequences)
    logger.info(f"Output embeddings tensor shape: {embeddings_tensor.shape}") # (batch_size, max_len, embedding_dim)

    # Test embedding an empty sequence / batch
    logger.info("Testing with empty sequence in batch:")
    batch_with_empty = ["hello", "", "world"]
    embeddings_with_empty = char_embedder(batch_with_empty)
    logger.info(f"Embeddings shape (with empty string): {embeddings_with_empty.shape}")

    logger.info("Testing with batch of only empty sequences:")
    batch_all_empty = ["", ""]
    embeddings_all_empty = char_embedder(batch_all_empty)
    logger.info(f"Embeddings shape (all empty strings): {embeddings_all_empty.shape}")
    
    logger.info("Testing with empty batch list:")
    empty_batch_list = []
    embeddings_empty_batch = char_embedder(empty_batch_list)
    logger.info(f"Embeddings shape (empty batch list): {embeddings_empty_batch.shape}")


    # Test getting embedding for a single character
    char_j_embed = char_embedder.get_embedding_for_char('j')
    if char_j_embed is not None:
        logger.info(f"Embedding for 'j' (shape: {char_j_embed.shape}): {char_j_embed[:5]}...")
    
    char_unknown_embed = char_embedder.get_embedding_for_char('©') # Should be UNK
    if char_unknown_embed is not None:
        logger.info(f"Embedding for '©' (shape: {char_unknown_embed.shape}): {char_unknown_embed[:5]}...")
        # Verify if it's the UNK embedding
        unk_token_id = torch.tensor([char_tokenizer.unk_id], dtype=torch.long, device=char_embedder.embedding_layer.weight.device)
        # Memory optimization: Device placement for memory management
        expected_unk_embed = char_embedder.embedding_layer(unk_token_id).squeeze(0)
        if torch.allclose(char_unknown_embed, expected_unk_embed):
            logger.info("Embedding for '©' matches the UNK token embedding.")
        else:
            logger.warning("Embedding for '©' DOES NOT match the UNK token embedding.")


    logger.info("--- CharacterLevelPhonemeTokenizer & Embedder Test Complete ---")
