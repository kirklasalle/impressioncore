from types import SimpleNamespace
import threading

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.interfaces import api_state
from src.interfaces.routes import system, vision
from src.interfaces.runtime_access import RuntimeAccessMiddleware
from src.orchestrator import audio_engine, kinect_connector


class FakeCamera:
    def isOpened(self):
        return True


class FakeVision:
    def __init__(self, *, has_caps=True):
        self.caps = {}
        self._frames = {"old": object()}
        self.visual_buffer = [object()]
        self.last_known_detections = {"old": object()}
        self.latest_skeleton = object()
        self.open_calls = 0
        self.close_calls = 0
        self.open_thread = None
        self.close_thread = None
        self.buffer_calls = 0
        self.has_caps = has_caps
        self._is_running = False

    def open(self):
        self.open_calls += 1
        self.open_thread = threading.current_thread().name
        self._is_running = True
        if self.has_caps:
            self.caps["camera"] = FakeCamera()
        return True

    def close(self):
        self.close_calls += 1
        self.close_thread = threading.current_thread().name
        self._is_running = False
        self.caps.clear()

    def start_buffer_loop(self):
        self.buffer_calls += 1


@pytest.fixture
def api_client(monkeypatch):
    vision._capture_status = {
        "status": "stopped",
        "active": False,
        "detail": "Capture has not been started.",
    }
    vision._capture_vision = None
    app = FastAPI()
    app.include_router(system.router)
    app.include_router(vision.router)
    app.add_middleware(RuntimeAccessMiddleware, key_provider=lambda: "test-runtime-key")
    with TestClient(app) as client:
        yield client
    api_state.triad_instance = None
    api_state.runtime_startup = {"phase": "NOT_STARTED", "error": None}


def _authorized(client, method, path, **kwargs):
    headers = kwargs.pop("headers", {})
    headers["x-api-key"] = "test-runtime-key"
    return getattr(client, method)(path, headers=headers, **kwargs)


def test_capture_status_get_does_not_open_hardware(api_client):
    fake_vision = FakeVision()
    api_state.triad_instance = SimpleNamespace(vision=fake_vision)

    assert api_client.get("/v1/vision/capture").status_code == 401
    response = _authorized(api_client, "get", "/v1/vision/capture")

    assert response.json()["status"] == "stopped"
    assert fake_vision.open_calls == 0


def test_capture_post_starts_then_stops_and_clears_cached_frames(api_client):
    fake_vision = FakeVision()
    api_state.triad_instance = SimpleNamespace(vision=fake_vision)

    started = _authorized(
        api_client, "post", "/v1/vision/capture", json={"enabled": True}
    )
    assert started.status_code == 200
    assert started.json()["status"] == "active"
    assert fake_vision.open_calls == 1
    assert fake_vision.open_thread.startswith("asyncio")
    assert api_state.triad_instance.vision_active is True

    status = _authorized(api_client, "get", "/v1/vision/capture")
    assert status.json()["active"] is True

    stopped = _authorized(
        api_client, "post", "/v1/vision/capture", json={"enabled": False}
    )
    assert stopped.status_code == 200
    assert stopped.json()["status"] == "stopped"
    assert fake_vision.close_calls == 1
    assert fake_vision.close_thread.startswith("asyncio")
    assert api_state.triad_instance.vision_active is False
    assert fake_vision._frames == {}
    assert fake_vision.visual_buffer == []
    assert fake_vision.last_known_detections == {}
    assert fake_vision.latest_skeleton is None


def test_capture_start_reports_missing_capabilities_and_releases(api_client):
    fake_vision = FakeVision(has_caps=False)
    api_state.triad_instance = SimpleNamespace(vision=fake_vision)

    response = _authorized(
        api_client, "post", "/v1/vision/capture", json={"enabled": True}
    )

    assert response.json()["status"] == "error"
    assert "no camera capabilities" in response.json()["detail"]
    assert fake_vision.close_calls == 1
    assert fake_vision._frames == {}


def test_system_and_model_status_expose_startup_failure(api_client):
    api_state.triad_instance = None
    api_state.runtime_startup = {"phase": "FAILED", "error": "model init failed"}

    response = _authorized(api_client, "get", "/v1/system/status")
    assert response.status_code == 503
    assert response.json()["status"] == "FAILED"
    assert response.json()["loading_phase"] == "FAILED"
    assert response.json()["initialization_error"] == "model init failed"

    model_response = _authorized(api_client, "get", "/v1/model/status")
    assert model_response.status_code == 503
    assert model_response.json()["detail"] == {
        "message": "Triad not initialized",
        "phase": "FAILED",
        "error": "model init failed",
    }


def test_kinect_stream_health_distinguishes_requested_initialized_and_fresh():
    connector = kinect_connector.KinectConnector()
    connector.is_open = True
    connector.sensor = object()
    connector.sensor_count = 1
    connector._set_stream_initialized("color", True, 0)
    connector._record_stream_frame("color", SimpleNamespace(dwFrameNumber=23))
    connector._set_stream_initialized(
        "ir", False, detail="RGB is open; Kinect v1 color and IR share a sensor path."
    )

    health = connector.get_stream_health()

    assert health["physical_sensor_count"] == 1
    assert health["logical_stream_count"] == 4
    assert health["streams"]["color"]["requested"] is True
    assert health["streams"]["color"]["initialized"] is True
    assert health["streams"]["color"]["fresh"] is True
    assert health["streams"]["color"]["frame_count"] == 1
    assert health["streams"]["color"]["last_frame_number"] == 23
    assert health["streams"]["ir"]["requested"] is True
    assert health["streams"]["ir"]["initialized"] is False
    assert health["streams"]["ir"]["fresh"] is False
    assert health["streams"]["ir"]["status"] == "UNAVAILABLE"


@pytest.mark.parametrize("capture_key", ["98", 98, "legacy-sdk-capture"])
def test_stream_status_api_keeps_legacy_enabled_streams_shape(api_client, capture_key):
    class FakeKinect:
        enabled_streams = {
            "color": True,
            "depth": True,
            "ir": True,
            "skeleton": True,
            "face": False,
        }

        def get_stream_health(self):
            return {
                "status": "DEGRADED",
                "capture_active": True,
                "physical_sensor_count": 1,
                "physical_sensor_identity": "kinect-v1:0",
                "logical_stream_count": 4,
                "streams": {
                    "color": {
                        "requested": True,
                        "initialized": True,
                        "fresh": False,
                        "status": "WAITING_FOR_FRAME",
                    }
                },
            }

    fake_kinect = FakeKinect()
    fake_vision = FakeVision()
    fake_vision.caps = {capture_key: fake_kinect}
    api_state.triad_instance = SimpleNamespace(vision=fake_vision)

    legacy = _authorized(api_client, "get", "/v1/vision/kinect/streams")
    assert legacy.json() == fake_kinect.enabled_streams

    health = _authorized(api_client, "get", "/v1/vision/kinect/stream-health")
    assert health.json()["health"]["physical_sensor_count"] == 1
    assert health.json()["health"]["logical_stream_count"] == 4
    assert health.json()["health"]["streams"]["color"]["fresh"] is False
    assert fake_vision.open_calls == 0


def test_missing_kinect_returns_explicit_404_without_opening_capture(api_client):
    fake_vision = FakeVision()
    api_state.triad_instance = SimpleNamespace(vision=fake_vision)
    response = _authorized(api_client, "get", "/v1/vision/kinect/streams")
    assert response.status_code == 404
    assert response.json() == {"detail": "Kinect not connected"}
    assert fake_vision.open_calls == 0


def test_stopped_capture_health_is_normal_after_close_empties_caps(api_client):
    fake_vision = FakeVision()
    api_state.triad_instance = SimpleNamespace(vision=fake_vision)
    started = _authorized(
        api_client, "post", "/v1/vision/capture", json={"enabled": True}
    )
    assert started.json()["active"] is True
    stopped = _authorized(
        api_client, "post", "/v1/vision/capture", json={"enabled": False}
    )
    assert stopped.json()["active"] is False
    assert fake_vision.caps == {}

    response = _authorized(api_client, "get", "/v1/vision/kinect/stream-health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "OK"
    assert payload["capture"]["status"] == "stopped"
    assert payload["capture"]["active"] is False
    assert payload["health"]["status"] == "STOPPED"
    assert payload["health"]["capture_active"] is False
    assert payload["health"]["physical_sensor_count"] is None
    assert payload["health"]["logical_stream_count"] == 4
    for stream in payload["health"]["streams"].values():
        assert stream["fresh"] is False
        assert stream["initialized"] is False
        assert stream["last_frame_age_ms"] is None
    assert fake_vision.open_calls == 1
    assert fake_vision.close_calls == 1
    assert _authorized(
        api_client, "get", "/v1/vision/kinect/streams"
    ).status_code == 404


def test_unstarted_capture_health_does_not_probe_sensor(api_client):
    fake_vision = FakeVision()
    api_state.triad_instance = SimpleNamespace(vision=fake_vision)
    response = _authorized(api_client, "get", "/v1/vision/kinect/stream-health")
    assert response.status_code == 200
    assert response.json()["health"]["physical_sensor_count"] is None
    assert response.json()["health"]["capture_active"] is False
    assert fake_vision.open_calls == 0
    assert fake_vision.close_calls == 0


def test_kinect_lookup_without_vision_has_no_lifecycle_side_effects():
    assert vision._find_kinect(None) is None



@pytest.mark.parametrize(
    ("result", "expected"),
    [(0, True), (1, True), (0x80070005, False), (-2147024891, False), (None, True)],
)
def test_hresult_success_check(result, expected):
    assert kinect_connector._hresult_succeeded(result) is expected


def test_acquired_sdk_frames_are_released_even_without_a_texture():
    class FakeSensor:
        def __init__(self):
            self.acquired = 0
            self.released = 0

        def NuiImageStreamGetNextFrame(self, handle, timeout, frame):
            self.acquired += 1
            return None  # comtypes success return

        def NuiImageStreamReleaseFrame(self, handle, frame):
            self.released += 1
            return None

    connector = kinect_connector.KinectConnector()
    connector.sensor = FakeSensor()
    handle = kinect_connector.wintypes.HANDLE(1)
    for _ in range(10):
        assert connector._get_frame_from_stream(
            handle, kinect_connector.NUI_IMAGE_TYPE_COLOR, "color"
        ) == (None, None)
    assert connector.sensor.acquired == connector.sensor.released == 10


@pytest.mark.parametrize(
    "name",
    [
        "Microphone Array (Kinect USB Au",
        "Microphone (Kinect USB Audio)",
        "Kinect USB Audio",
    ],
)
def test_kinect_mme_truncated_name_maps_to_canonical_identity(name):
    assert audio_engine.audio_device_identity(name) == "audio:kinect usb audio"


def test_four_channel_kinect_is_not_a_playstation_eye(monkeypatch):
    class FakeSoundDevice:
        @staticmethod
        def query_devices():
            return [
                {
                    "name": "Microphone (Kinect USB Audio)",
                    "max_input_channels": 4,
                    "default_samplerate": 16000,
                    "hostapi": 0,
                },
                {
                    "name": "Microphone (USB Camera)",
                    "max_input_channels": 4,
                    "default_samplerate": 16000,
                    "hostapi": 0,
                },
                {
                    "name": "Microphone (PlayStation Eye)",
                    "max_input_channels": 4,
                    "default_samplerate": 16000,
                    "hostapi": 0,
                },
            ]

        @staticmethod
        def query_hostapis():
            return [{"name": "WASAPI"}]

    monkeypatch.setattr(audio_engine, "sd", FakeSoundDevice)
    engine = audio_engine.AudioEngine()

    kinect = next(device for device in engine.devices if "Kinect" in device["name"])
    usb_camera = next(device for device in engine.devices if "USB Camera" in device["name"])
    ps_eye = next(device for device in engine.devices if "PlayStation" in device["name"])

    assert kinect["is_kinect"] is True
    assert kinect["is_eye"] is False
    assert usb_camera["is_eye"] is False
    assert ps_eye["is_eye"] is True


def test_audio_endpoints_deduplicate_by_normalized_device_name():
    endpoints = [
        {
            "index": 2,
            "name": "Microphone (Kinect USB Audio)",
            "channels": 4,
            "provider": "WASAPI",
            "is_kinect": True,
            "is_eye": False,
        },
        {
            "index": 8,
            "name": "Kinect USB Audio",
            "channels": 4,
            "provider": "DirectSound",
            "is_kinect": True,
            "is_eye": False,
        },
    ]

    grouped = audio_engine.summarize_audio_devices(endpoints)

    assert len(grouped) == 1
    assert grouped[0]["channels"] == 4
    assert grouped[0]["providers"] == ["WASAPI", "DirectSound"]
    assert grouped[0]["endpoint_indices"] == [2, 8]
    assert grouped[0]["is_kinect"] is True
    assert grouped[0]["is_eye"] is False
