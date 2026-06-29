"""Shared pytest fixtures."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from src.adapters.in_memory_metrics import InMemoryMetricsAdapter
from src.adapters.in_memory_route_registry import InMemoryRouteRegistry
from src.adapters.in_memory_security import InMemorySecurityAdapter
from src.adapters.in_memory_upstream_registry import InMemoryUpstreamRegistry
from src.adapters.httpx_client import HttpxClientAdapter
from src.application.health_service import HealthService
from src.application.proxy_service import ProxyService
from src.application.route_management import RouteManagementService
from src.config import get_settings
from src.main import create_app


@pytest.fixture()
def metrics() -> InMemoryMetricsAdapter:
    return InMemoryMetricsAdapter()


@pytest.fixture()
def route_registry() -> InMemoryRouteRegistry:
    return InMemoryRouteRegistry()


@pytest.fixture()
def upstream_registry() -> InMemoryUpstreamRegistry:
    return InMemoryUpstreamRegistry()


@pytest.fixture()
def security_adapter() -> InMemorySecurityAdapter:
    settings = get_settings()
    return InMemorySecurityAdapter(
        jwt_secret=settings.jwt_secret,
        jwt_algorithm=settings.jwt_algorithm,
    )


@pytest.fixture()
def health_service(metrics: InMemoryMetricsAdapter) -> HealthService:
    return HealthService(metrics=metrics)


@pytest.fixture()
def route_management_service(route_registry: InMemoryRouteRegistry) -> RouteManagementService:
    return RouteManagementService(route_registry=route_registry)


@pytest.fixture()
def client() -> TestClient:
    """Return a synchronous TestClient backed by a fresh app instance."""
    app = create_app()
    return TestClient(app, raise_server_exceptions=True)
