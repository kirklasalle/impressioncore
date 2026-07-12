"""Integration coverage for the B3 production launcher FastAPI layer."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from deployment import launch_production as launch_module


class StubInference:
    """Minimal inference stub that records generate calls."""

    def __init__(self) -> None:
        self.calls = []

    def generate(self, **kwargs):  # type: ignore[override]
        self.calls.append(kwargs)
        return {
            "response": "Integration success.",
            "strategy": "natural_only",
            "timing": {"total_ms": 42},
        }


class ErrorInference:
    """Inference stub that simulates a runtime failure."""

    def generate(self, **kwargs):  # type: ignore[override]
        raise RuntimeError("synthetic failure")


@pytest.mark.skip(reason="Placeholder test: ImpressionCoreB3Launcher is not implemented; deployment is managed via b3_production_deployment.py")
@pytest.mark.integration
def test_inference_endpoint_round_trip():
    """POST /inference returns metadata from the underlying inference call."""
    inference = StubInference()
    app = launch_module.create_api_application(inference)
    client = TestClient(app)

    payload = {
        "prompt": "Explain concentrated intelligence.",
        "use_rag": True,
        "category": "multimodal",
        "max_length": 256,
        "use_retry": False,
        "use_smart_hybrid": True,
    }

    response = client.post("/inference", json=payload)
    body = response.json()

    assert response.status_code == 200
    assert body["response"] == "Integration success."
    assert body["metadata"]["strategy"] == "natural_only"
    assert inference.calls[0]["user_input"] == payload["prompt"]
    assert inference.calls[0]["use_rag"] is True


@pytest.mark.skip(reason="Placeholder test: ImpressionCoreB3Launcher is not implemented; deployment is managed via b3_production_deployment.py")
@pytest.mark.integration
def test_inference_endpoint_error_path():
    """Generator errors surface as HTTP 500 responses for observability."""
    app = launch_module.create_api_application(ErrorInference())
    client = TestClient(app)

    payload = {
        "prompt": "Trigger an error",
        "use_rag": False,
        "category": "multimodal",
        "max_length": 64,
        "use_retry": False,
        "use_smart_hybrid": False,
    }

    response = client.post("/inference", json=payload)
    body = response.json()

    assert response.status_code == 500
    assert "Inference error" in body["detail"]


@pytest.mark.skip(reason="Placeholder test: ImpressionCoreB3Launcher is not implemented; deployment is managed via b3_production_deployment.py")
@pytest.mark.integration
def test_validation_mode_skips_runtime(monkeypatch):
    """Validation-only mode runs preflight and avoids building the API."""
    flags = {"preflight": False}

    def stub_preflight() -> None:
        flags["preflight"] = True

    def fail_initialize(self, config):  # pragma: no cover - defensive
        raise AssertionError("initialize_inference should not run in validation-only mode")

    def fail_build(self):  # pragma: no cover - defensive
        raise AssertionError("build_api should not run in validation-only mode")

    monkeypatch.setattr(launch_module, "run_preflight_checks", stub_preflight)
    monkeypatch.setattr(launch_module, "PREFLIGHT_AVAILABLE", True)
    monkeypatch.setattr(launch_module.ImpressionCoreB3Launcher, "initialize_inference", fail_initialize)
    monkeypatch.setattr(launch_module.ImpressionCoreB3Launcher, "build_api", fail_build)

    config = launch_module.LaunchConfig(
        mode="validation-only",
        host="127.0.0.1",
        port=8000,
        workers=1,
        model_path=None,
        f_data_root=Path("F:/data"),
        skip_preflight=False,
    )

    launcher = launch_module.ImpressionCoreB3Launcher()
    assert launcher.launch_production(config) is True
    assert flags["preflight"] is True
