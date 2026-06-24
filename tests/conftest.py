"""
Shared pytest fixtures for the API Gateway / BFF Service test suite.
"""
from __future__ import annotations

from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.core.models import HealthStatus, ProxyResponse
from app.infrastructure.config import Settings


# ── Settings override ─────────────────────────────────────────────────────────

@pytest.fixture()
def test_settings() -> Settings:
    """Return a Settings instance with safe test defaults."""
    return Settings(
        app_name="api-gateway-test",
        app_version="0.0.0-test",
        environment="development",
        identity_service_url="http://identity-service-mock:8001",
        redis_url="redis://localhost:6379/15",
        rate_limit_requests=1000,
        rate_limit_window_seconds=60,
        max_request_body_bytes=1_048_576,
        otel_exporter_otlp_endpoint="",
    )


# ── Mock adapters ─────────────────────────────────────────────────────────────

@pytest.fixture()
def mock_rate_limiter() -> AsyncMock:
    """Rate limiter that always allows requests."""
    limiter = AsyncMock()
    limiter.is_allowed = AsyncMock(return_value=True)
    return limiter


@pytest.fixture()
def mock_upstream_client() -> AsyncMock:
    """Upstream HTTP client that returns a canned 200 response."""
    client = AsyncMock()
    client.send = AsyncMock(
        return_value=ProxyResponse(
            status_code=200,
            headers={"content-type": "application/json"},
            body=b'{"ok": true}',
        )
    )
    client.aclose = AsyncMock()
    return client


# ── Application fixture ───────────────────────────────────────────────────────

@pytest.fixture()
def app(test_settings: Settings, mock_rate_limiter: AsyncMock, mock_upstream_client: AsyncMock) -> FastAPI:
    """Return a FastAPI test application with mocked dependencies."""
    from app.main import create_app
    from app.infrastructure.config import get_settings
    from app.infrastructure.dependencies import (
        get_gateway_service,
        get_health_service,
        get_rate_limiter,
        get_upstream_client,
    )
    from app.application.gateway_service import GatewayService
    from app.application.health_service import HealthService

    application = create_app()

    # Override settings
    application.dependency_overrides[get_settings] = lambda: test_settings

    # Override adapters
    application.dependency_overrides[get_rate_limiter] = lambda: mock_rate_limiter
    application.dependency_overrides[get_upstream_client] = lambda: mock_upstream_client

    # Override services
    application.dependency_overrides[get_health_service] = lambda: HealthService(test_settings)
    application.dependency_overrides[get_gateway_service] = lambda: GatewayService(
        upstream_client=mock_upstream_client,
        rate_limiter=mock_rate_limiter,
        settings=test_settings,
    )

    return application


@pytest_asyncio.fixture()
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Async HTTP test client wired to the test application."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as ac:
        yield ac
