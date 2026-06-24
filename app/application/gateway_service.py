"""
Application service — gateway / proxy use case.

Implements GatewayPort (inbound port).
Orchestrates rate limiting, request-size enforcement, upstream forwarding,
and correlation-ID propagation.
"""
from __future__ import annotations

from app.core.exceptions import RateLimitExceededError, RequestTooLargeError
from app.core.models import ProxyRequest, ProxyResponse
from app.core.ports import GatewayPort, RateLimiterPort, UpstreamClientPort
from app.infrastructure.config import Settings
from app.infrastructure.logging import get_logger

logger = get_logger(__name__)


class GatewayService(GatewayPort):
    """Proxy requests to upstream services with rate limiting and size checks."""

    def __init__(
        self,
        upstream_client: UpstreamClientPort,
        rate_limiter: RateLimiterPort,
        settings: Settings,
    ) -> None:
        self._upstream = upstream_client
        self._rate_limiter = rate_limiter
        self._settings = settings

    async def forward(self, request: ProxyRequest) -> ProxyResponse:
        # 1. Request-size guard
        if request.body and len(request.body) > self._settings.max_request_body_bytes:
            raise RequestTooLargeError(self._settings.max_request_body_bytes)

        # 2. Rate-limit check (keyed by client IP extracted from headers)
        client_ip = (
            request.headers.get("x-forwarded-for", "").split(",")[0].strip()
            or request.headers.get("x-real-ip", "unknown")
        )
        allowed = await self._rate_limiter.is_allowed(
            key=client_ip,
            limit=self._settings.rate_limit_requests,
            window_seconds=self._settings.rate_limit_window_seconds,
        )
        if not allowed:
            raise RateLimitExceededError()

        # 3. Forward to upstream
        logger.debug(
            "forwarding_request",
            extra={
                "method": request.method,
                "path": request.path,
                "correlation_id": request.context.correlation_id,
            },
        )
        return await self._upstream.send(request)
