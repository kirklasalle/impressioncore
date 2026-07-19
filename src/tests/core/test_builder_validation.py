"""Tests for Builder configuration validation.

Covers WS3 Task 4 and WS5 quality gate.
"""
import pytest
from unittest.mock import MagicMock, patch
from flask import Flask, json

from src.interfaces.web.routes.builder import builder_bp


@pytest.fixture
def app():
    app = Flask(__name__)
    app.register_blueprint(builder_bp)
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(app):
    return app.test_client()


def test_builder_model_configure_get(client):
    resp = client.get("/api/v1/builder/model/configure")
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data["success"] is True
    assert "config" in data


def test_builder_model_configure_valid_preset(client):
    # Attempt configuring preset b1_39m with no modifications
    payload = {"preset": "b1_39m"}
    resp = client.post(
        "/api/v1/builder/model/configure",
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data["success"] is True
    assert data["config"]["preset"] == "b1_39m"


def test_builder_model_configure_invalid_preset_override(client):
    # Attempt configuring b1_39m but override hiddenSize (which is 768 in preset)
    payload = {"preset": "b1_39m", "hiddenSize": 1024}
    resp = client.post(
        "/api/v1/builder/model/configure",
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert resp.status_code == 400
    data = json.loads(resp.data)
    assert data["success"] is False
    assert any("Cannot override preset" in err for err in data["errors"])


def test_builder_model_configure_custom_valid(client):
    # Valid custom configuration
    payload = {
        "preset": "custom",
        "architecture": "transformer",
        "layers": 12,
        "hiddenSize": 512,
        "heads": 8,
        "intermediateSize": 2048,
        "contextWindow": 2048,
        "vocabSize": 50257,
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


def test_builder_model_configure_custom_invalid_bounds(client):
    # Invalid custom configurations (hiddenSize too small or non-divisible by heads)
    payload = {
        "preset": "custom",
        "layers": 12,
        "hiddenSize": 512,
        "heads": 7,  # 512 is not divisible by 7
    }
    resp = client.post(
        "/api/v1/builder/model/configure",
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert resp.status_code == 400
    data = json.loads(resp.data)
    assert data["success"] is False
    assert any("divisible by heads" in err for err in data["errors"])
