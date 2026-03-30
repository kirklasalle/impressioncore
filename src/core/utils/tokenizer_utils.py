#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #cuda #documentation #inference #memory_management #python #source_code #src/core/utils/tokenizer_utils.py #tokenization #transformer
**Category:** Core Implementation
**Status:** Active
"""









# Tokenizer Utils

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:01
# Author:** ImpressionCore Team
# Tags:** #cuda #documentation #inference #memory_management #python #source_code #src\\core\\utils\\tokenizer_utils.py #tokenization #transformer
# Category:** Core Implementation
# Status:** Active


from transformers import AutoModelForCausalLM

# Default generative model: small, efficient, open-source (can be changed via config)
DEFAULT_GENERATIVE_MODEL = "distilgpt2"

def load_generative_model_and_tokenizer(model_name: str = DEFAULT_GENERATIVE_MODEL):
    """
    Loads a HuggingFace generative model and tokenizer for text generation.

    Args:
        model_name (str): Name of the HuggingFace model to load.

    Returns:
        tokenizer: The loaded tokenizer object.
        model: The loaded generative model (in eval mode).
    """
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    model.eval()
    return tokenizer, model

def generate_text(prompt: str, tokenizer, model, device: str | None = None, max_length: int = 64) -> str:
    """
    Generates text from a prompt using a generative model.

    Args:
        prompt (str): Input prompt for generation.
        tokenizer: HuggingFace tokenizer.
        model: HuggingFace generative model.
        device (str, optional): Device to run inference on (e.g., 'cpu', 'cuda').
        max_length (int): Maximum length of generated text.

    Returns:
        str: Generated text response.
    """
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
    model = model.to(device)
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    with torch.no_grad():
        outputs = model.generate(**inputs, max_length=max_length, do_sample=True, top_p=0.95, top_k=50, temperature=0.8, pad_token_id=tokenizer.eos_token_id)
    generated = tokenizer.decode(outputs[0], skip_special_tokens=True)
    # Remove the prompt from the output for a clean reply
    if generated.startswith(prompt):
        generated = generated[len(prompt):].strip()
    return generated
"""
tokenizer_utils.py

Utility functions for initializing and using HuggingFace tokenizers and embedding models in ImpressionCore.

- Modular, memory-efficient, and compliant with ImpressionCore standards.
- Designed for GTX 1050 Ti (4GB VRAM) and low-resource environments.
- All functions are functional (not class-based) and include docstrings per ImpressionCore documentation requirements.

Author: ImpressionCore Copilot
Last updated: 2025-06-23
"""


import torch
from transformers import AutoModel, AutoTokenizer

# Default model: small, efficient, open-source (can be changed via config)
DEFAULT_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

def load_tokenizer_and_model(model_name: str = DEFAULT_MODEL_NAME):
    """
    Loads a HuggingFace tokenizer and model for text embedding.

    Args:
        model_name (str): Name of the HuggingFace model to load.

    Returns:
        tokenizer: The loaded tokenizer object.
        model: The loaded embedding model (in eval mode).
    """
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)
    model.eval()
    return tokenizer, model

def embed_text(text: str, tokenizer, model, device: str | None = None) -> torch.Tensor:
    """
    Converts input text to an embedding vector using the provided tokenizer and model.

    Args:
        text (str): Input text to embed.
        tokenizer: HuggingFace tokenizer.
        model: HuggingFace model.
        device (str, optional): Device to run inference on (e.g., 'cpu', 'cuda').

    Returns:
        torch.Tensor: Embedding vector for the input text.
    """
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
    model = model.to(device)
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=256)
    inputs = {k: v.to(device) for k, v in inputs.items()}
    with torch.no_grad():
        outputs = model(**inputs)
        # Use the [CLS] token embedding as the sentence embedding
        embedding = outputs.last_hidden_state[:, 0, :].squeeze(0)
    return embedding.cpu()

def batch_embed_texts(texts: list[str], tokenizer, model, device: str | None = None) -> torch.Tensor:
    """
    Batch embeds a list of texts for efficient inference.

    Args:
        texts (List[str]): List of input texts.
        tokenizer: HuggingFace tokenizer.
        model: HuggingFace model.
        device (str, optional): Device to run inference on.

    Returns:
        torch.Tensor: Batch of embedding vectors (shape: [batch_size, embedding_dim]).
    """
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
    model = model.to(device)
    inputs = tokenizer(texts, return_tensors="pt", padding=True, truncation=True, max_length=256)
    inputs = {k: v.to(device) for k, v in inputs.items()}
    with torch.no_grad():
        outputs = model(**inputs)
        embeddings = outputs.last_hidden_state[:, 0, :]
    return embeddings.cpu()
