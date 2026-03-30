"""
test_openai_embeddings.py

Created: August 20, 2025
Author: GitHub Copilot
Purpose: Unit tests for OpenAI embedding utilities.
"""


import os
import sys

import pytest

# Ensure project root is in sys.path for imports
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
from src.core.utils.openai_embeddings import generate_openai_embeddings

if not os.getenv("OPENAI_API_KEY"):
    # Attempt to infer raw key from root or src .env
    possible_paths = [
        os.path.abspath(os.path.join(PROJECT_ROOT, '.env')),
        os.path.abspath(os.path.join(PROJECT_ROOT, 'src', '.env')),
    ]
    inferred = None
    for p in possible_paths:
        if os.path.isfile(p):
            with open(p, encoding='utf-8') as f:
                for line in f:
                    t = line.strip()
                    if not t or t.startswith('#'):
                        continue
                    if t.startswith('OPENAI_API_KEY='):
                        inferred = t.split('=',1)[1].strip()
                        break
                    if t.startswith('sk-') and len(t) > 40:
                        inferred = t
                        break
            if inferred:
                break
    if inferred:
        os.environ['OPENAI_API_KEY'] = inferred
    else:
        pytest.skip("OPENAI_API_KEY not set or inferable; skipping embedding test.", allow_module_level=True)

def test_generate_openai_embeddings():
    """
    Test OpenAI embedding generation for a simple input.
    Args:
        None
    Returns:
        None. Asserts correctness of embedding output.
    """
    texts = ["Test sentence for embedding."]
    embeddings = generate_openai_embeddings(texts)
    assert embeddings is not None, "Embeddings should not be None"
    assert embeddings.shape[0] == 1, "Should return one embedding"
    assert embeddings.shape[1] > 0, "Embedding dimension should be > 0"
