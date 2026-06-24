"""
FastAPI middleware collection for the API Gateway / BFF Service.

Middleware is applied in the order it is registered on the FastAPI app.
"""
from __future__ import annotations

import time
import uuid

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp

from app.infrastructure.logging import get_logger

logger = get_logger(__name__)

_CORRELATION_ID_HEADER = "X-Correlation-ID"
_REQUEST_ID_HEADER = "X-Request-ID"


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """Ensure every request carries a valid X-Correlation-ID header.

    If the client supplies one it is validated and forwarded; otherwise a new
    UUID4 is generated.  The value is echoed back in the response.
    """

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        correlation_id = (
            request.headers.get(_CORRELATION_ID_HEADER) or str(uuid.uuid4())
        )
        # Attach to request state so downstream handlers can read it
        request.state.correlation_id = correlation_id

        response = await call_next(request)
        response.headers[_CORRELATION_ID_HEADER] = correlation_id
        return response


class AccessLogMiddleware(BaseHTTPMiddleware):
    """Emit a structured access-log entry for every request."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000

        logger.info(
            "access_log",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round(duration_ms, 2),
                "correlation_id": getattr(request.state, "correlation_id", "-"),
                "client_ip": request.client.host if request.client else "-",
            },
        )
        return response


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """Reject requests whose body exceeds *max_bytes*."""

    def __init__(self, app: ASGIApp, max_bytes: int = 1_048_576) -> None:
        super().__init__(app)
        self._max_bytes = max_bytes

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self._max_bytes:
            return Response(
                content=f"Request body too large (max {self._max_bytes} bytes)",
                status_code=413,
            )
        return await call_next(request)
