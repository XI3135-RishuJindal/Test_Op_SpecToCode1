"""Dependency injection wiring for FastAPI."""
from __future__ import annotations

from functools import lru_cache

from src.adapters.httpx_client import HttpxClientAdapter
from src.adapters.in_memory_metrics import InMemoryMetricsAdapter
from src.adapters.in_memory_route_registry import InMemoryRouteRegistry
from src.adapters.in_memory_security import InMemorySecurityAdapter
from src.adapters.in_memory_upstream_registry import InMemoryUpstreamRegistry
from src.application.health_service import HealthService
from src.application.proxy_service import ProxyService
from src.application.route_management import RouteManagementService
from src.config import Settings, get_settings


# ── Singleton adapters ────────────────────────────────────────────────────────

@lru_cache(maxsize=1)
def _route_registry() -> InMemoryRouteRegistry:
    return InMemoryRouteRegistry()


@lru_cache(maxsize=1)
def _upstream_registry() -> InMemoryUpstreamRegistry:
    return InMemoryUpstreamRegistry()


@lru_cache(maxsize=1)
def _metrics_adapter() -> InMemoryMetricsAdapter:
    return InMemoryMetricsAdapter()


@lru_cache(maxsize=1)
def _http_client() -> HttpxClientAdapter:
    settings: Settings = get_settings()
    return HttpxClientAdapter(timeout=30.0)


@lru_cache(maxsize=1)
def _security_adapter() -> InMemorySecurityAdapter:
    settings: Settings = get_settings()
    return InMemorySecurityAdapter(
        jwt_secret=settings.jwt_secret,
        jwt_algorithm=settings.jwt_algorithm,
    )


# ── FastAPI dependency callables ──────────────────────────────────────────────

def get_health_service() -> HealthService:
    """Provide a :class:`HealthService` instance."""
    return HealthService(metrics=_metrics_adapter())


def get_route_management_service() -> RouteManagementService:
    """Provide a :class:`RouteManagementService` instance."""
    return RouteManagementService(route_registry=_route_registry())


def get_proxy_service() -> ProxyService:
    """Provide a :class:`ProxyService` instance."""
    return ProxyService(
        route_registry=_route_registry(),
        http_client=_http_client(),
        metrics=_metrics_adapter(),
    )
