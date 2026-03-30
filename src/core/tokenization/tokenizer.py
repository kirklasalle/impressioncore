#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #multimodal #python #source_code #src/data/tokenization/tokenizer.py #tokenization #transformer
**Category:** Data Processing
**Status:** Active
"""









# Tokenizer

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:01
# Author:** ImpressionCore Team
# Tags:** #multimodal #python #source_code #src\\data\\tokenization\\tokenizer.py #tokenization #transformer
# Category:** Data Processing
# Status:** Active

"""
Multimodal tokenizer interface for ImpressionCore-b1.

Handles both text and image tokenization.
"""
import logging
from typing import Any

logger = logging.getLogger(__name__)


def initialize_models():
    """
    Loads and initializes the text and image models required for tokenization.
    This should be called once to avoid reloading large models repeatedly.

    Returns:
        tuple: A tuple containing (text_tokenizer, image_model, image_preprocessor).
    """
    try:
        from torchvision import models
        from torchvision.models import ResNet18_Weights
        from transformers import AutoTokenizer

        logger.info("Initializing text and image models...")
        text_tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')

        # Use the recommended `weights` parameter and get the default weights
        weights = ResNet18_Weights.DEFAULT
        image_model = models.resnet18(weights=weights)
        image_model.eval()

        # Use the transforms associated with the weights
        image_preprocessor = weights.transforms()

        logger.info("Models initialized successfully.")
        return text_tokenizer, image_model, image_preprocessor
    except ImportError as e:
        logger.error("Failed to import necessary libraries for model initialization: %s", e)
        logger.error("Please ensure 'transformers' and 'torchvision' are installed.")
        return None, None, None
    except Exception as e:
        logger.error("An unexpected error occurred during model initialization: %s", e)
        return None, None, None

def tokenize(prompt: dict[str, Any], text_tokenizer: Any, image_model: Any, image_preprocessor: Any) -> dict[str, Any]:
    """
    Tokenize a unified prompt (text, image path) using pre-loaded models.

    Args:
        prompt (Dict[str, Any]): Unified prompt dictionary.
        text_tokenizer (Any): Pre-loaded text tokenizer.
        image_model (Any): Pre-loaded image model.
        image_preprocessor (Any): Pre-loaded image preprocessor.

    Returns:
        Dict[str, Any]: Tokenized representation (text_ids, image_features, etc).
    """
    import torch
    from PIL import Image

    text = prompt.get('text')
    image_path = prompt.get('image_path')
    metadata = prompt.get('metadata', {})

    text_ids = None
    image_features = None

    if text and text_tokenizer:
        try:
            text_ids = text_tokenizer.encode(text, return_tensors='pt')
        except Exception as e:
            logger.warning("Text tokenization failed for entry: %s. Error: %s", metadata.get('source', 'N/A'), e)

    if image_path and image_model and image_preprocessor:
        try:
            with Image.open(image_path).convert("RGB") as img:
                image_tensor = image_preprocessor(img).unsqueeze(0)
                with torch.no_grad():
                    image_features = image_model(image_tensor).squeeze(0)
        except FileNotFoundError:
            logger.warning("Image file not found: %s", image_path)
        except Exception as e:
            logger.warning("Image processing failed for %s. Error: %s", image_path, e)

    return {
        "text_ids": text_ids,
        "image_features": image_features,
        "metadata": metadata
    }
