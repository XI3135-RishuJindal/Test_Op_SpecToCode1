"""HTTPX-based outbound HTTP client adapter."""
from __future__ import annotations

from typing import Optional

import httpx

from src.ports.outbound import HttpClientPort


class HttpxClientAdapter(HttpClientPort):
    """Concrete HTTP client using :mod:`httpx` for async request forwarding."""

    def __init__(self, timeout: float = 30.0) -> None:
        self._timeout = timeout

    async def forward(
        self,
        method: str,
        url: str,
        headers: dict[str, str],
        body: Optional[bytes],
        timeout_seconds: float = 30.0,
    ) -> tuple[int, dict[str, str], bytes]:
        """Forward *method* request to *url* and return ``(status, headers, body)``."""
        async with httpx.AsyncClient(timeout=timeout_seconds or self._timeout) as client:
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                content=body,
            )
        resp_headers = dict(response.headers)
        return response.status_code, resp_headers, response.content
