"""
Unit tests for the GatewayService application service.
"""
from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from app.application.gateway_service import GatewayService
from app.core.exceptions import RateLimitExceededError, RequestTooLargeError
from app.core.models import CorrelationContext, ProxyRequest, ProxyResponse
from app.infrastructure.config import Settings


@pytest.fixture()
def settings() -> Settings:
    return Settings(
        rate_limit_requests=10,
        rate_limit_window_seconds=60,
        max_request_body_bytes=100,
    )


@pytest.fixture()
def allow_rate_limiter() -> AsyncMock:
    m = AsyncMock()
    m.is_allowed = AsyncMock(return_value=True)
    return m


@pytest.fixture()
def deny_rate_limiter() -> AsyncMock:
    m = AsyncMock()
    m.is_allowed = AsyncMock(return_value=False)
    return m


@pytest.fixture()
def upstream_client() -> AsyncMock:
    m = AsyncMock()
    m.send = AsyncMock(
        return_value=ProxyResponse(
            status_code=200,
            headers={"content-type": "application/json"},
            body=b'{"ok": true}',
        )
    )
    return m


def _make_request(body: bytes | None = None) -> ProxyRequest:
    return ProxyRequest(
        method="POST",
        path="/auth/register",
        headers={"x-forwarded-for": "1.2.3.4"},
        body=body,
        context=CorrelationContext(),
    )


@pytest.mark.asyncio
async def test_forward_calls_upstream(
    settings: Settings,
    allow_rate_limiter: AsyncMock,
    upstream_client: AsyncMock,
) -> None:
    svc = GatewayService(upstream_client, allow_rate_limiter, settings)
    result = await svc.forward(_make_request())
    assert result.status_code == 200
    upstream_client.send.assert_awaited_once()


@pytest.mark.asyncio
async def test_forward_raises_rate_limit_when_denied(
    settings: Settings,
    deny_rate_limiter: AsyncMock,
    upstream_client: AsyncMock,
) -> None:
    svc = GatewayService(upstream_client, deny_rate_limiter, settings)
    with pytest.raises(RateLimitExceededError):
        await svc.forward(_make_request())
    upstream_client.send.assert_not_awaited()


@pytest.mark.asyncio
async def test_forward_raises_request_too_large(
    settings: Settings,
    allow_rate_limiter: AsyncMock,
    upstream_client: AsyncMock,
) -> None:
    svc = GatewayService(upstream_client, allow_rate_limiter, settings)
    oversized_body = b"x" * (settings.max_request_body_bytes + 1)
    with pytest.raises(RequestTooLargeError):
        await svc.forward(_make_request(body=oversized_body))
    upstream_client.send.assert_not_awaited()
