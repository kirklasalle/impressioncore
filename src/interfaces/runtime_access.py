"""Authentication for runtime HTTP, media and WebSocket transports."""

import hmac
import logging
from collections.abc import Callable

from starlette.datastructures import Headers
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

logger = logging.getLogger(__name__)
PUBLIC_PATHS = frozenset({
    "/", "/docs", "/docs/oauth2-redirect", "/openapi.json", "/favicon.ico",
    "/health/live", "/health/ready", "/system_monitor.html",
})


class RuntimeAccessMiddleware:
    """Keep the service key server-side and require it on all runtime transports."""

    def __init__(self, app: ASGIApp, key_provider: Callable[[], str | None]) -> None:
        self.app = app
        self.key_provider = key_provider

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in {"http", "websocket"}:
            await self.app(scope, receive, send)
            return
        path = scope["path"]
        if scope["type"] == "http" and (
            path in PUBLIC_PATHS or scope.get("method") == "OPTIONS"
        ):
            await self.app(scope, receive, send)
            return
        expected = self.key_provider()
        supplied = Headers(scope=scope).get("x-api-key", "")
        if expected and hmac.compare_digest(supplied.encode(), expected.encode()):
            await self.app(scope, receive, send)
            return
        if scope["type"] == "websocket":
            await send({"type": "websocket.close", "code": 4401})
            return
        status = 401 if expected else 503
        detail = (
            "Invalid or missing runtime credentials"
            if expected else "Runtime authentication is not configured; use the local stack launcher"
        )
        await JSONResponse({"detail": detail}, status_code=status)(scope, receive, send)
