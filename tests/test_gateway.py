"""
Tests for the gateway proxy endpoints.

Acceptance criteria:
  - POST /api/v1/auth/register proxies to upstream and returns its response
  - POST /api/v1/auth/verify proxies to upstream and returns its response
  - Rate-limit exceeded → 429
  - Request body too large → 413
  - Upstream unavailable → 502
  - Correlation ID is propagated to upstream
"""
from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient

from app.core.exceptions import RateLimitExceededError, UpstreamUnavailableError
from app.core.models import ProxyResponse


@pytest.mark.asyncio
async def test_register_proxies_upstream_response(
    client: AsyncClient,
    mock_upstream_client: AsyncMock,
) -> None:
    mock_upstream_client.send.return_value = ProxyResponse(
        status_code=201,
        headers={"content-type": "application/json"},
        body=b'{"id": "user-123"}',
    )
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "secret"},
    )
    assert response.status_code == 201
    assert response.json() == {"id": "user-123"}


@pytest.mark.asyncio
async def test_verify_email_proxies_upstream_response(
    client: AsyncClient,
    mock_upstream_client: AsyncMock,
) -> None:
    mock_upstream_client.send.return_value = ProxyResponse(
        status_code=200,
        headers={"content-type": "application/json"},
        body=b'{"verified": true}',
    )
    response = await client.post(
        "/api/v1/auth/verify",
        json={"token": "abc123"},
    )
    assert response.status_code == 200
    assert response.json() == {"verified": True}


@pytest.mark.asyncio
async def test_rate_limit_exceeded_returns_429(
    app,
    mock_rate_limiter: AsyncMock,
) -> None:
    from httpx import ASGITransport, AsyncClient

    mock_rate_limiter.is_allowed.return_value = False
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as c:
        response = await c.post(
            "/api/v1/auth/register",
            json={"email": "x@x.com", "password": "y"},
        )
    assert response.status_code == 429


@pytest.mark.asyncio
async def test_upstream_unavailable_returns_502(
    app,
    mock_upstream_client: AsyncMock,
    mock_rate_limiter: AsyncMock,
) -> None:
    from httpx import ASGITransport, AsyncClient

    mock_upstream_client.send.side_effect = UpstreamUnavailableError("identity-service")
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as c:
        response = await c.post(
            "/api/v1/auth/register",
            json={"email": "x@x.com", "password": "y"},
        )
    assert response.status_code == 502


@pytest.mark.asyncio
async def test_correlation_id_header_forwarded(
    client: AsyncClient,
    mock_upstream_client: AsyncMock,
) -> None:
    cid = "my-correlation-id-999"
    await client.post(
        "/api/v1/auth/register",
        json={"email": "a@b.com", "password": "pw"},
        headers={"X-Correlation-ID": cid},
    )
    call_args = mock_upstream_client.send.call_args
    forwarded_request = call_args[0][0]
    assert forwarded_request.context.correlation_id == cid
