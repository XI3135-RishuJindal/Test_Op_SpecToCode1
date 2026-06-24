"""
Outbound adapter — HTTP client for upstream services.

Uses httpx for async HTTP with connection pooling and timeout management.
Implements UpstreamClientPort.
"""
from __future__ import annotations

import httpx

from app.core.exceptions import UpstreamUnavailableError
from app.core.models import ProxyRequest, ProxyResponse
from app.core.ports import UpstreamClientPort
from app.infrastructure.logging import get_logger

logger = get_logger(__name__)

_DEFAULT_TIMEOUT = httpx.Timeout(connect=5.0, read=30.0, write=10.0, pool=5.0)


class HttpUpstreamClient(UpstreamClientPort):
    """Forwards requests to upstream services via HTTP."""

    def __init__(self, base_url: str, timeout: httpx.Timeout = _DEFAULT_TIMEOUT) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self._base_url,
                timeout=self._timeout,
                follow_redirects=True,
            )
        return self._client

    async def send(self, request: ProxyRequest) -> ProxyResponse:
        client = await self._get_client()

        # Propagate correlation ID to upstream
        headers = dict(request.headers)
        headers["X-Correlation-ID"] = request.context.correlation_id
        if request.context.idempotency_key:
            headers["X-Idempotency-Key"] = request.context.idempotency_key

        # Strip hop-by-hop headers
        for hop in ("host", "connection", "transfer-encoding", "te", "trailer", "upgrade"):
            headers.pop(hop, None)

        try:
            resp = await client.request(
                method=request.method,
                url=request.path,
                headers=headers,
                content=request.body,
            )
        except httpx.ConnectError as exc:
            logger.error("upstream_connect_error", extra={"url": self._base_url, "error": str(exc)})
            raise UpstreamUnavailableError(self._base_url) from exc
        except httpx.TimeoutException as exc:
            logger.error("upstream_timeout", extra={"url": self._base_url, "error": str(exc)})
            raise UpstreamUnavailableError(self._base_url) from exc

        return ProxyResponse(
            status_code=resp.status_code,
            headers=dict(resp.headers),
            body=resp.content,
        )

    async def aclose(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()
