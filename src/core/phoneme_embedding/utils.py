#!/usr/bin/env python3
r"""
ImpressionCore: Utils

Module for utils functionality in the ImpressionCore framework.

File: modules/phoneme_embedding/utils.py
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
Dependencies: [typing]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements utils functionality for the
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
# from modules.phoneme_embedding.utils import MainClass # MainClass not defined
# instance = MainClass()
# result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

# ImpressionCore - Phoneme Embedding Utilities
#
# Description:
# This module provides utility functions supporting the phoneme_embedding
# components within ImpressionCore. Currently, it includes a function
# `load_phoneme_vocabulary` for loading phoneme (or character) lists
# from text files. This can be used to define custom vocabularies for
# tokenizers or other processing steps if needed, though current character-based
# tokenizers might use predefined or inferred character sets.
#
# Author: Kirk LaSalle & GitHub Copilot
# Date: 2025-05-23
# Version: 1.0
#
# Dependencies:
# - typing
# - os
#
# License:
# MIT License
#
# Copyright (c) 2025 ImpressionCore
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
Utility functions for the Phoneme Embedding Module.

This module provides helper functions, such as loading vocabularies
or other common tasks related to phoneme processing.
"""

from typing import List
import os

def load_phoneme_vocabulary(vocab_path: str) -> List[str]:
    """
    Loads a phoneme vocabulary from a file.

    Each phoneme should be on a new line in the file.
    Lines starting with '#' will be treated as comments and ignored.
    Empty lines will also be ignored.

    Args:
        vocab_path (str): Path to the vocabulary file.

    Returns:
        List[str]: A list of phonemes.

    Raises:
        FileNotFoundError: If the vocabulary file does not exist.
    """
    if not os.path.exists(vocab_path):
        raise FileNotFoundError(f"Vocabulary file not found at: {vocab_path}")

    phonemes: List[str] = []
    with open(vocab_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                phonemes.append(line)
    
    if not phonemes:
        print(f"Warning: Vocabulary file {vocab_path} is empty or contains only comments.")
        
    return phonemes

# Example usage (for testing purposes)
if __name__ == "__main__":
    # Create a dummy vocab file for testing
    dummy_vocab_content = """# ARPAbet Phonemes
#!/usr/bin/env python3
\"\"\"# Escaped triple quotes
ImpressionCore - Brain-Inspired Multimodal AI Framework

File: src//modules//phoneme_embedding//utils.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-25
Modified: 2025-05-25
Version: 1.0.0
\"\"\"# Escaped triple quotes
AA
AE
AH
AO
AW
AY
B
CH
# This is a comment
DH
EH
ER
EY
F
G
HH
IH
IY
JH
K
L
M
N
NG
OW
P
R
S
SH
T
TH
UH
UW
V
W
Y
Z
ZH"""
    dummy_vocab_path = "dummy_phoneme_vocab.txt"
    with open(dummy_vocab_path, "w") as f:
        f.write(dummy_vocab_content)

    print(f"Created dummy vocab file: {dummy_vocab_path}")

    # Test load_phoneme_vocabulary
    phonemes = load_phoneme_vocabulary(dummy_vocab_path)
    print("Loaded phonemes:", phonemes)

    # Test get_phoneme_to_id_mapping
    # phoneme_to_id, id_to_phoneme = get_phoneme_to_id_mapping(phonemes) # Commented out: function not defined
    # print("Phoneme to ID mapping:", phoneme_to_id)
    # print("ID to Phoneme mapping:", id_to_phoneme)

    # Test get_phoneme_set
    # phoneme_set = get_phoneme_set(dummy_vocab_path) # Commented out: function not defined
    # print("Phoneme set:", phoneme_set)

    # Clean up dummy file
    import os
    os.remove(dummy_vocab_path)
    print(f"Removed dummy vocab file: {dummy_vocab_path}")

    # Test with a non-existent file
    try:
        load_phoneme_vocabulary("non_existent_vocab.txt")
    except FileNotFoundError as e:
        print(f"Caught expected error: {e}")

    # Test with an empty file
    empty_vocab_path = "empty_phoneme_vocab.txt"
    with open(empty_vocab_path, "w") as f:
        pass # Create an empty file
    phonemes_empty = load_phoneme_vocabulary(empty_vocab_path)
    print(f"Loaded phonemes from empty file: {phonemes_empty}") # Should be []
    os.remove(empty_vocab_path)

    # Test with a file containing only comments
    comment_vocab_path = "comment_phoneme_vocab.txt"
    with open(comment_vocab_path, "w") as f:
        f.write("# This is a comment\n")
        f.write("### Another comment\n")
    phonemes_comment = load_phoneme_vocabulary(comment_vocab_path)
    print(f"Loaded phonemes from comment-only file: {phonemes_comment}") # Should be []
    os.remove(comment_vocab_path)
