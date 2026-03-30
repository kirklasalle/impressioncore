"""
openai_embeddings_api.py

Created: August 21, 2025
Author: GitHub Copilot
Purpose: Proper OpenAI Embeddings API implementation following platform.openai.com specifications

This implements the correct API patterns:
POST https://api.openai.com/v1/embeddings

Following OpenAI documentation patterns for:
- Proper API authentication
- Request/response handling
- Error management
- Model specifications
"""

import os
import time
from dataclasses import dataclass
from typing import Any

import numpy as np
import requests

from .rich_logging import log_error, log_info, log_success, log_warning


@dataclass
class EmbeddingConfig:
    """Configuration for OpenAI embeddings API calls."""
    model: str = "text-embedding-3-small"  # or "text-embedding-3-large"
    encoding_format: str = "float"  # or "base64"
    dimensions: int | None = None  # Optional for ada-002 compatibility
    user: str | None = None  # Optional user identifier


class OpenAIEmbeddingsAPI:
    """Proper OpenAI Embeddings API client following official specifications."""

    def __init__(self, api_key: str | None = None, base_url: str = "https://api.openai.com/v1"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = base_url
        self.embeddings_endpoint = f"{base_url}/embeddings"

        if not self.api_key:
            raise ValueError("OpenAI API key required. Set OPENAI_API_KEY environment variable.")

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "ImpressionCore/1.0"
        }

        log_info(f"Initialized OpenAI API client with endpoint: {self.embeddings_endpoint}")

    def create_embeddings(
        self,
        input_texts: str | list[str],
        config: EmbeddingConfig | None = None
    ) -> dict[str, Any]:
        """
        Create embeddings using OpenAI API.

        Args:
            input_texts: Text or list of texts to embed
            config: Embedding configuration

        Returns:
            Full API response with embeddings data
        """
        config = config or EmbeddingConfig()

        # Ensure input is a list
        if isinstance(input_texts, str):
            input_texts = [input_texts]

        # Prepare request payload following OpenAI API spec
        payload = {
            "model": config.model,
            "input": input_texts,
            "encoding_format": config.encoding_format
        }

        # Add optional parameters
        if config.dimensions:
            payload["dimensions"] = config.dimensions
        if config.user:
            payload["user"] = config.user

        log_info(f"Creating embeddings for {len(input_texts)} texts using {config.model}")
        log_info(f"Request payload keys: {list(payload.keys())}")

        try:
            start_time = time.time()
            response = requests.post(
                self.embeddings_endpoint,
                headers=self.headers,
                json=payload,
                timeout=60
            )

            response.raise_for_status()
            response_data = response.json()

            elapsed_time = time.time() - start_time

            # Validate response structure
            if "data" not in response_data:
                raise ValueError("Invalid response: missing 'data' field")

            if "usage" not in response_data:
                log_warning("Response missing usage information")

            embeddings_count = len(response_data["data"])
            total_tokens = response_data.get("usage", {}).get("total_tokens", 0)

            log_success(f"✅ Created {embeddings_count} embeddings in {elapsed_time:.2f}s")
            log_info(f"Total tokens used: {total_tokens}")

            if "usage" in response_data:
                usage = response_data["usage"]
                log_info(f"Usage details: {usage}")

            return response_data

        except requests.exceptions.RequestException as e:
            log_error(f"API request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    log_error(f"API error details: {error_data}")
                except (ValueError, KeyError):
                    log_error(f"API error response: {e.response.text}")
            raise

        except Exception as e:
            log_error(f"Unexpected error during embedding creation: {e}")
            raise

    def extract_embeddings_array(self, response_data: dict[str, Any]) -> np.ndarray:
        """Extract embeddings as numpy array from API response."""
        embeddings_list = []

        for item in response_data["data"]:
            if "embedding" not in item:
                raise ValueError(f"Invalid embedding item: {item}")
            embeddings_list.append(item["embedding"])

        embeddings_array = np.array(embeddings_list, dtype=np.float32)
        log_info(f"Extracted embeddings array shape: {embeddings_array.shape}")

        return embeddings_array

    def get_model_info(self, model_name: str) -> dict[str, Any]:
        """Get information about embedding model capabilities."""
        model_specs = {
            "text-embedding-3-small": {
                "dimensions": 1536,
                "max_tokens": 8191,
                "price_per_1m_tokens": 0.02,
                "description": "High performance, cost-effective embedding model"
            },
            "text-embedding-3-large": {
                "dimensions": 3072,
                "max_tokens": 8191,
                "price_per_1m_tokens": 0.13,
                "description": "Most capable embedding model with highest accuracy"
            },
            "text-embedding-ada-002": {
                "dimensions": 1536,
                "max_tokens": 8191,
                "price_per_1m_tokens": 0.10,
                "description": "Legacy embedding model (deprecated)"
            }
        }

        return model_specs.get(model_name, {
            "dimensions": 1536,
            "max_tokens": 8191,
            "price_per_1m_tokens": 0.02,
            "description": "Unknown model"
        })

    def estimate_cost(self, token_count: int, model_name: str) -> float:
        """Estimate cost for embedding generation."""
        model_info = self.get_model_info(model_name)
        price_per_token = model_info["price_per_1m_tokens"] / 1_000_000
        return token_count * price_per_token

    def create_embeddings_batched(
        self,
        input_texts: list[str],
        config: EmbeddingConfig | None = None,
        batch_size: int = 100,
        delay_between_batches: float = 1.0
    ) -> np.ndarray:
        """
        Create embeddings in batches to handle large inputs efficiently.

        Args:
            input_texts: List of texts to embed
            config: Embedding configuration
            batch_size: Number of texts per API call
            delay_between_batches: Delay in seconds between batches

        Returns:
            Combined embeddings array
        """
        config = config or EmbeddingConfig()

        log_info(f"Processing {len(input_texts)} texts in batches of {batch_size}")

        all_embeddings = []
        total_tokens = 0

        for i in range(0, len(input_texts), batch_size):
            batch = input_texts[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (len(input_texts) + batch_size - 1) // batch_size

            log_info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} texts)")

            try:
                response = self.create_embeddings(batch, config)
                batch_embeddings = self.extract_embeddings_array(response)
                all_embeddings.append(batch_embeddings)

                # Track usage
                if "usage" in response:
                    total_tokens += response["usage"].get("total_tokens", 0)

                # Delay between batches to respect rate limits
                if i + batch_size < len(input_texts) and delay_between_batches > 0:
                    time.sleep(delay_between_batches)

            except Exception as e:
                log_error(f"Failed to process batch {batch_num}: {e}")
                raise

        # Combine all embeddings
        combined_embeddings = np.vstack(all_embeddings)

        estimated_cost = self.estimate_cost(total_tokens, config.model)

        log_success("✅ Completed batched embedding generation")
        log_info(f"Final shape: {combined_embeddings.shape}")
        log_info(f"Total tokens: {total_tokens}")
        log_info(f"Estimated cost: ${estimated_cost:.4f}")

        return combined_embeddings


def test_openai_api_connection():
    """Test OpenAI API connection and basic functionality."""
    try:
        api = OpenAIEmbeddingsAPI()

        # Test with a simple text
        test_texts = [
            "Hello, world!",
            "This is a test of OpenAI embeddings API.",
            "ImpressionCore is a revolutionary AI framework."
        ]

        log_info("Testing OpenAI API connection...")

        # Test small model
        config_small = EmbeddingConfig(model="text-embedding-3-small")
        response = api.create_embeddings(test_texts, config_small)
        embeddings = api.extract_embeddings_array(response)

        log_success("✅ API test successful!")
        log_info(f"Response structure: {list(response.keys())}")
        log_info(f"Embeddings shape: {embeddings.shape}")

        if "usage" in response:
            usage = response["usage"]
            cost = api.estimate_cost(usage.get("total_tokens", 0), config_small.model)
            log_info(f"Cost for test: ${cost:.6f}")

        return True

    except Exception as e:
        log_error(f"API test failed: {e}")
        return False


if __name__ == "__main__":
    # Run API connection test
    test_openai_api_connection()
