#!/usr/bin/env python3
"""
Unit tests for GPU OOM error handling and memory clear endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from fastapi import HTTPException

# Ensure src is in path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.interfaces.triad_api import app
from src.interfaces import api_state
from agent0core.config import default_config as agent_config

# Set a test API key for the environment
agent_config.api_key = "test_api_key"

@pytest.fixture
def client():
    return TestClient(app)

def test_multimodal_process_oom_handling(client):
    """Test that process endpoint handles OOM errors and returns 503 with suggestions."""
    mock_triad = MagicMock()
    # Simulate a CUDA out of memory error
    mock_triad.generate.side_effect = RuntimeError("CUDA out of memory: VRAM allocation limit reached.")
    
    with patch.object(api_state, 'triad_instance', mock_triad):
        payload = {
            "prompt": "Test prompting to trigger OOM",
            "voice_enabled": False
        }
        headers = {"X-API-Key": agent_config.api_key}
        response = client.post("/v1/process", json=payload, headers=headers)
        
        assert response.status_code == 503
        data = response.json()
        assert "detail" in data
        detail = data["detail"]
        assert detail["error"] == "GPU_OOM"
        assert "GPU memory exhausted" in detail["message"]
        assert "fallback_suggestions" in detail
        assert len(detail["fallback_suggestions"]) > 0

def test_system_memory_clear_endpoint(client):
    """Test that the system memory clear endpoint successfully invokes the clear utility."""
    with patch("src.core.utils.gpu_utils.clear_gpu_memory") as mock_clear:
        headers = {"X-API-Key": agent_config.api_key}
        response = client.post("/v1/system/memory/clear", headers=headers)
        assert response.status_code == 200
        assert response.json() == {"status": "SUCCESS", "message": "GPU memory cleared."}
        mock_clear.assert_called_once()
