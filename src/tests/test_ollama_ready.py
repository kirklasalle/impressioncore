"""Quick test of Ollama connectivity and llama3.2:3b availability."""
import pytest
import requests


def test_ollama_api_reachable():
    """Check that the Ollama API is running and responding."""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
    except Exception as exc:
        pytest.skip(f"Ollama API unreachable: {exc}")
    assert response.status_code == 200
    models = response.json()
    assert "models" in models


def test_ollama_llama32_generation():
    """Generate a short response with llama3.2:3b."""
    try:
        requests.get("http://localhost:11434/api/tags", timeout=5)
    except Exception as exc:
        pytest.skip(f"Ollama API unreachable: {exc}")

    payload = {
        "model": "llama3.2:3b",
        "prompt": "Hello! Can you introduce yourself briefly?",
        "stream": False,
    }
    response = requests.post(
        "http://localhost:11434/api/generate", json=payload, timeout=30
    )
    assert response.status_code == 200
    result = response.json()
    assert "response" in result
