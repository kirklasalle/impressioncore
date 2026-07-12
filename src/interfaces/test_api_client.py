import sys
import os
from unittest.mock import MagicMock

# ── Mock heavy neural dependencies and hardware interfaces ───────────────
mock_triad = MagicMock()
mock_triad.vision = MagicMock()
mock_triad.audio = MagicMock()
mock_triad.avatar = MagicMock()
mock_triad.generate.return_value = {
    "response": "Synthesized Mock Response",
    "internal_monitors": {"left_hemisphere": "left", "right_hemisphere": "right"},
    "nexus_logs": [],
    "snapshot_url": "/captures/mock.jpg",
    "snapshot_urls": ["/captures/mock.jpg"],
    "generated_image_url": None,
    "affective_state": "NEUTRAL"
}

class MockUnifiedBrainTriad:
    def __new__(cls, *args, **kwargs):
        return mock_triad

sys.modules['src.orchestrator.unified_triad'] = MagicMock()
sys.modules['src.orchestrator.unified_triad'].UnifiedBrainTriad = MockUnifiedBrainTriad

sys.modules['src.intelligence.stt_service'] = MagicMock()
sys.modules['src.intelligence.tts_service'] = MagicMock()
sys.modules['src.orchestrator.kinect_fusion_adapter'] = MagicMock()
sys.modules['src.interfaces.telemetry_manager'] = MagicMock()
sys.modules['src.orchestrator.runtime_mode_controller'] = MagicMock()
sys.modules['src.orchestrator.vector_connector'] = MagicMock()

# Mock sounddevice for audio routing unit tests
sys.modules['sounddevice'] = MagicMock()
sys.modules['sounddevice'].query_devices.return_value = [
    {"name": "Mock Microphone 1", "hostapi": 0, "max_input_channels": 2},
    {"name": "Mock Microphone 2", "hostapi": 0, "max_input_channels": 4}
]

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from fastapi.testclient import TestClient
from src.interfaces.triad_api import app
from src.interfaces import api_state

client = TestClient(app)

def test_routes():
    # Force state indicators for testing
    api_state.triad_instance = mock_triad
    api_state.stt_service = MagicMock()
    api_state.tts_service = MagicMock()
    api_state.telemetry_manager = MagicMock()
    api_state.runtime_mode_controller = MagicMock()
    api_state.kinect_fusion_adapter = MagicMock()

    print("Testing root endpoint...")
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ONLINE"
    print("Root OK:", data)

    print("Testing system status...")
    response = client.get("/v1/system/status")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    print("System Status OK:", data)

    print("Testing vision trace...")
    response = client.get("/v1/vision/trace")
    assert response.status_code == 401
    print("Vision Trace Auth Check OK (Returned 401)")

    # Send correct API Key
    from agent0core.config import default_config as agent_config
    if not agent_config.api_key:
        agent_config.api_key = "test-api-key"
    headers = {"X-API-Key": agent_config.api_key}

    print("Testing vision trace with API key...")
    response = client.get("/v1/vision/trace", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "1_server_status" in data
    print("Vision Trace OK:", data)

    print("Testing audio devices...")
    response = client.get("/v1/audio/devices", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "OK"
    assert len(data["devices"]) > 0
    print("Audio Devices OK:", data)

    print("Testing RLM status...")
    response = client.get("/v1/rlm/status", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "policy_agent" in data
    assert "training" in data
    print("RLM Status OK:", data)

    print("Testing Agent0 status...")
    response = client.get("/v1/agent0/status", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    print("Agent0 Status OK:", data)

    print("All modular route tests passed successfully!")

if __name__ == "__main__":
    test_routes()
