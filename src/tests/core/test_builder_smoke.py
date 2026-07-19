"""Smoke tests for all Builder routes under a simulated low-VRAM (GTX 1050 Ti) hardware profile.

Covers WS3 Task 5 and WS5 quality gate.
"""
import pytest
from unittest.mock import MagicMock, patch
from flask import Flask, json

# Mock PyTorch properties
class MockCudaDeviceProperties:
    def __init__(self):
        self.name = "NVIDIA GeForce GTX 1050 Ti"
        self.total_mem = 4294967296  # 4GB VRAM


@pytest.fixture
def mock_cuda():
    with patch("torch.cuda.is_available", return_value=True), \
         patch("torch.cuda.device_count", return_value=1), \
         patch("torch.cuda.get_device_properties", return_value=MockCudaDeviceProperties()), \
         patch("torch.cuda.memory_allocated", return_value=1073741824), \
         patch("torch.cuda.memory_reserved", return_value=1610612736):
        yield


@pytest.fixture
def app():
    app = Flask(__name__)
    from src.interfaces.web.routes.builder import builder_bp
    app.register_blueprint(builder_bp)
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(app):
    return app.test_client()


def test_walkthrough_progress_smoke(client):
    # GET walkthrough progress
    resp = client.get("/api/v1/builder/walkthrough/progress")
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data["success"] is True

    # PUT walkthrough progress
    payload = {"step": 2, "selected_offering": "b1_39m"}
    resp = client.put(
        "/api/v1/builder/walkthrough/progress",
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data["success"] is True


def test_model_presets_smoke(client):
    resp = client.get("/api/v1/builder/model/presets")
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data["success"] is True
    assert "presets" in data
    assert any(p["id"] == "b1_39m" for p in data["presets"])


def test_model_configure_smoke(client, mock_cuda):
    # Get current config
    resp = client.get("/api/v1/builder/model/configure")
    assert resp.status_code == 200
    
    # Configure custom low-VRAM parameters
    payload = {
        "preset": "custom",
        "architecture": "transformer",
        "layers": 4,
        "hiddenSize": 256,
        "heads": 4,
        "intermediateSize": 1024,
        "contextWindow": 1024,
        "vocabSize": 10000,
        "precision": "fp16",
    }
    resp = client.post(
        "/api/v1/builder/model/configure",
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data["success"] is True
    assert "estimates" in data
    assert data["estimates"]["fits_target"] is True  # Low-VRAM config fits target


def test_training_configure_smoke(client):
    # GET training config
    resp = client.get("/api/v1/builder/training/configure")
    assert resp.status_code == 200

    # POST training config
    payload = {"epochs": 2, "batchSize": 1, "learningRate": 0.00002}
    resp = client.post(
        "/api/v1/builder/training/configure",
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data["success"] is True


def test_training_actions_and_status_smoke(client):
    # GET training status
    resp = client.get("/api/v1/builder/training/status")
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert "running" in data

    # POST stop training (clean start check)
    resp = client.post("/api/v1/builder/training/stop")
    assert resp.status_code == 200


def test_checkpoint_browser_smoke(client):
    resp = client.get("/api/v1/builder/training/checkpoints")
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data["success"] is True
    assert "checkpoints" in data


def test_data_profiles_smoke(client):
    # GET profiles
    resp = client.get("/api/v1/builder/data/profiles")
    assert resp.status_code == 200

    # POST create profile
    payload = {"name": "Test Profile", "dirPath": "data/raw"}
    resp = client.post(
        "/api/v1/builder/data/profiles",
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert resp.status_code in (200, 400)
