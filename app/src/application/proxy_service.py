"""Gateway proxy use-case — route resolution and request forwarding."""
from __future__ import annotations

import time
import uuid
from typing import Optional

from src.domain.traffic import RequestMetric
from src.ports.inbound import RouteRegistryPort
from src.ports.outbound import HttpClientPort, MetricsPort, SecurityPort


class ProxyService:
    """Orchestrates route resolution, security checks, and request forwarding.

    This is the central use-case of the API Gateway.  It:

    1. Resolves the best matching :class:`~src.domain.route.Route` for the
       incoming request.
    2. Optionally validates the caller's credentials via
       :class:`~src.ports.outbound.SecurityPort`.
    3. Forwards the request to the upstream service.
    4. Records a :class:`~src.domain.traffic.RequestMetric` for observability.
    """

    def __init__(
        self,
        route_registry: RouteRegistryPort,
        http_client: HttpClientPort,
        metrics: MetricsPort,
        security: Optional[SecurityPort] = None,
    ) -> None:
        self._routes = route_registry
        self._http = http_client
        self._metrics = metrics
        self._security = security

    async def handle(
        self,
        method: str,
        path: str,
        headers: dict[str, str],
        body: Optional[bytes] = None,
    ) -> tuple[int, dict[str, str], bytes]:
        """Handle an incoming request and return ``(status, headers, body)``.

        Raises:
            ValueError: If no route matches the request.
            PermissionError: If the caller fails authentication.
        """
        start = time.monotonic()
        request_id = str(uuid.uuid4())

        route = await self._routes.resolve_route(path, method)
        if route is None:
            raise ValueError(f"No route found for {method} {path}")

        # ── Optional security enforcement ────────────────────────────────────
        if self._security is not None:
            api_key_header = headers.get("x-api-key") or headers.get("X-API-Key")
            auth_header = headers.get("authorization") or headers.get("Authorization")

            if api_key_header:
                key = await self._security.validate_api_key(api_key_header)
                if key is None or not key.enabled or key.is_expired():
                    raise PermissionError("Invalid or expired API key")
            elif auth_header and auth_header.lower().startswith("bearer "):
                token = auth_header.split(" ", 1)[1]
                claims = await self._security.validate_jwt(token)
                if claims is None or claims.is_expired():
                    raise PermissionError("Invalid or expired JWT token")

        # ── Build upstream URL ────────────────────────────────────────────────
        rewritten_path = route.rewrite_path(path)
        upstream_url = f"{route.upstream_url.rstrip('/')}{rewritten_path}"

        # ── Forward request ───────────────────────────────────────────────────
        forwarded_headers = {k: v for k, v in headers.items()}
        forwarded_headers["X-Request-ID"] = request_id
        forwarded_headers["X-Forwarded-By"] = "api-gateway-service"

        status, resp_headers, resp_body = await self._http.forward(
            method=method,
            url=upstream_url,
            headers=forwarded_headers,
            body=body,
        )

        # ── Record metrics ────────────────────────────────────────────────────
        latency_ms = (time.monotonic() - start) * 1000
        await self._metrics.record(
            RequestMetric(
                request_id=request_id,
                route_id=route.route_id,
                upstream_id=route.upstream_url,
                method=method,
                path=path,
                status_code=status,
                latency_ms=latency_ms,
            )
        )

        return status, resp_headers, resp_body

    # Alias used by the HTTP adapter
    async def proxy(
        self,
        method: str,
        path: str,
        headers: dict[str, str],
        body: Optional[bytes] = None,
    ) -> Optional[tuple[int, dict[str, str], bytes]]:
        """Public alias for :meth:`handle` that returns ``None`` on routing failure."""
        try:
            return await self.handle(method=method, path=path, headers=headers, body=body)
        except ValueError:
            return None
