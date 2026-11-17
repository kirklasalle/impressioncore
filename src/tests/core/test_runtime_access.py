"""Authentication must cover HTTP, media, WebSockets and CORS failure responses."""

import pytest
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient

from src.interfaces.runtime_access import RuntimeAccessMiddleware


def make_client(key: str | None = "test-runtime-only") -> TestClient:
    app = FastAPI()

    @app.get("/v1/status")
    @app.get("/captures/test.jpg")
    @app.get("/static/captures/test.jpg")
    @app.get("/health/live")
    def status():
        return {"status": "OK"}

    @app.websocket("/v1/telemetry/stream")
    async def stream(ws: WebSocket):
        await ws.accept()
        await ws.send_json({"status": "OK"})
        await ws.close()

    app.add_middleware(RuntimeAccessMiddleware, key_provider=lambda: key)
    app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], allow_methods=["*"], allow_headers=["*"])
    return TestClient(app)


@pytest.mark.parametrize("path", ["/v1/status", "/captures/test.jpg", "/static/captures/test.jpg"])
def test_http_requires_valid_server_credential(path):
    with make_client() as client:
        response = client.get(path, headers={"Origin": "http://localhost:5173"})
        assert response.status_code == 401
        assert response.headers["access-control-allow-origin"] == "http://localhost:5173"
        assert client.get(path, headers={"X-API-Key": "wrong"}).status_code == 401
        assert client.get(path, headers={"X-API-Key": "test-runtime-only"}).status_code == 200


def test_unconfigured_key_is_explicit_unavailable_not_type_error():
    with make_client(None) as client:
        assert client.get("/v1/status", headers={"X-API-Key": "wrong"}).status_code == 503
        assert client.get("/health/live").status_code == 200


def test_preflight_is_not_authorization():
    with make_client() as client:
        assert client.options("/v1/status", headers={
            "Origin": "http://localhost:5173", "Access-Control-Request-Method": "GET",
        }).status_code == 200
        assert client.get("/v1/status").status_code == 401


def test_websocket_requires_credential_and_valid_gateway_handshake():
    from starlette.websockets import WebSocketDisconnect

    with make_client() as client:
        with pytest.raises(WebSocketDisconnect) as error:
            with client.websocket_connect("/v1/telemetry/stream"):
                pass
        assert error.value.code == 4401
        with client.websocket_connect("/v1/telemetry/stream", headers={"X-API-Key": "test-runtime-only"}) as ws:
            assert ws.receive_json() == {"status": "OK"}
