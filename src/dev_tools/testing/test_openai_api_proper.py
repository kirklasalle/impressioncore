"""
test_openai_api_proper.py

Created: August 21, 2025
Author: GitHub Copilot
Purpose: Test proper OpenAI Embeddings API implementation

This demonstrates the correct way to use OpenAI embeddings API following their documentation.
"""

import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import os
import time
from typing import Any

import numpy as np
import requests

from src.core.utils.rich_logging import log_error, log_info, log_success


class OpenAIEmbeddingsAPI:
    """Proper OpenAI Embeddings API client following official specifications."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = "https://api.openai.com/v1"
        self.embeddings_endpoint = f"{self.base_url}/embeddings"

        if not self.api_key:
            raise ValueError("OpenAI API key required. Set OPENAI_API_KEY environment variable.")

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "ImpressionCore/1.0"
        }

        log_info("✅ Initialized OpenAI API client")
        log_info(f"Endpoint: {self.embeddings_endpoint}")

    def create_embeddings(
        self,
        input_texts: str | list[str],
        model: str = "text-embedding-3-small"
    ) -> dict[str, Any]:
        """Create embeddings using OpenAI API following their exact specification."""

        # Ensure input is a list
        if isinstance(input_texts, str):
            input_texts = [input_texts]

        # Prepare request payload exactly as specified in OpenAI docs
        payload = {
            "model": model,
            "input": input_texts,
            "encoding_format": "float"
        }

        log_info(f"🔄 Creating embeddings for {len(input_texts)} texts using {model}")

        try:
            start_time = time.time()

            # Make the POST request to OpenAI API
            response = requests.post(
                self.embeddings_endpoint,
                headers=self.headers,
                json=payload,
                timeout=60
            )

            # Check for HTTP errors
            response.raise_for_status()
            response_data = response.json()

            elapsed_time = time.time() - start_time

            # Validate response structure
            if "data" not in response_data:
                raise ValueError("Invalid response: missing 'data' field")

            embeddings_count = len(response_data["data"])
            total_tokens = response_data.get("usage", {}).get("total_tokens", 0)

            log_success(f"✅ Created {embeddings_count} embeddings in {elapsed_time:.2f}s")
            log_info(f"📊 Total tokens used: {total_tokens}")

            # Log usage details
            if "usage" in response_data:
                usage = response_data["usage"]
                log_info(f"💰 Usage details: {usage}")

            return response_data

        except requests.exceptions.HTTPError as e:
            log_error(f"❌ HTTP Error: {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    log_error(f"API error details: {error_data}")
                except Exception:
                    log_error(f"API error response: {e.response.text}")
            raise

        except Exception as e:
            log_error(f"❌ Unexpected error: {e}")
            raise

    def extract_embeddings_array(self, response_data: dict[str, Any]) -> np.ndarray:
        """Extract embeddings as numpy array from API response."""
        embeddings_list = []

        for item in response_data["data"]:
            if "embedding" not in item:
                raise ValueError(f"Invalid embedding item: {item}")
            embeddings_list.append(item["embedding"])

        embeddings_array = np.array(embeddings_list, dtype=np.float32)
        log_info(f"📐 Extracted embeddings array shape: {embeddings_array.shape}")

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
            }
        }

        return model_specs.get(model_name, model_specs["text-embedding-3-small"])

    def estimate_cost(self, token_count: int, model_name: str) -> float:
        """Estimate cost for embedding generation."""
        model_info = self.get_model_info(model_name)
        price_per_token = model_info["price_per_1m_tokens"] / 1_000_000
        return token_count * price_per_token


def test_api_basic():
    """Test basic API functionality."""
    log_info("🧪 Testing basic OpenAI Embeddings API functionality...")

    try:
        api = OpenAIEmbeddingsAPI()

        # Test with simple texts
        test_texts = [
            "Hello, world!",
            "This is a test of OpenAI embeddings API.",
            "ImpressionCore is a revolutionary AI framework for consumer hardware."
        ]

        # Test text-embedding-3-small
        log_info("Testing text-embedding-3-small model...")
        response = api.create_embeddings(test_texts, model="text-embedding-3-small")
        embeddings = api.extract_embeddings_array(response)

        log_success("✅ Basic API test successful!")
        log_info(f"Response keys: {list(response.keys())}")
        log_info(f"Embeddings shape: {embeddings.shape}")

        # Calculate cost
        if "usage" in response:
            usage = response["usage"]
            cost = api.estimate_cost(usage.get("total_tokens", 0), "text-embedding-3-small")
            log_info(f"💰 Cost for test: ${cost:.6f}")

        return True, embeddings

    except Exception as e:
        log_error(f"❌ Basic API test failed: {e}")
        return False, None


def test_api_large_model():
    """Test large model API functionality."""
    log_info("🧪 Testing text-embedding-3-large model...")

    try:
        api = OpenAIEmbeddingsAPI()

        # Test with more complex text
        complex_text = """
        ImpressionCore represents a revolutionary approach to artificial intelligence that combines
        brain-inspired architectures with practical constraints for consumer hardware. This framework
        is designed to run efficiently on devices with limited VRAM, such as the NVIDIA GTX 1050 Ti
        with 4GB of memory. The core architecture consists of several key components that work together
        to process multimodal information including text, images, and audio data.
        """

        # Test text-embedding-3-large
        response = api.create_embeddings([complex_text], model="text-embedding-3-large")
        embeddings = api.extract_embeddings_array(response)

        log_success("✅ Large model test successful!")
        log_info(f"Large model embeddings shape: {embeddings.shape}")

        # Calculate cost
        if "usage" in response:
            usage = response["usage"]
            cost = api.estimate_cost(usage.get("total_tokens", 0), "text-embedding-3-large")
            log_info(f"💰 Cost for large model test: ${cost:.6f}")

        return True, embeddings

    except Exception as e:
        log_error(f"❌ Large model test failed: {e}")
        return False, None


def test_api_comprehensive():
    """Run comprehensive API tests."""
    log_info("🚀 Starting comprehensive OpenAI Embeddings API tests...")

    results = {}

    # Test 1: Basic functionality
    log_info("\n" + "="*60)
    log_info("TEST 1: Basic API Functionality")
    log_info("="*60)
    success, embeddings_small = test_api_basic()
    results["basic"] = success

    if success:
        log_info(f"✅ Basic test passed - embeddings shape: {embeddings_small.shape}")

    # Test 2: Large model
    log_info("\n" + "="*60)
    log_info("TEST 2: Large Model Testing")
    log_info("="*60)
    success, embeddings_large = test_api_large_model()
    results["large_model"] = success

    if success:
        log_info(f"✅ Large model test passed - embeddings shape: {embeddings_large.shape}")

    # Summary
    log_info("\n" + "="*60)
    log_info("TEST SUMMARY")
    log_info("="*60)

    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        log_info(f"{test_name}: {status}")

    all_passed = all(results.values())
    if all_passed:
        log_success("🎉 All tests passed! OpenAI API integration is working correctly.")
    else:
        log_error("❌ Some tests failed. Check the logs above for details.")

    return all_passed


if __name__ == "__main__":
    # Run comprehensive tests
    test_api_comprehensive()
