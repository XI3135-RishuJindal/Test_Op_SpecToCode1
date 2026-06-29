"""Tests for the RouteManagementService use-case."""
from __future__ import annotations

import pytest

from src.adapters.in_memory_route_registry import InMemoryRouteRegistry
from src.application.route_management import RouteManagementService


@pytest.fixture()
def service() -> RouteManagementService:
    return RouteManagementService(route_registry=InMemoryRouteRegistry())


@pytest.mark.asyncio
class TestRouteManagementService:
    async def test_add_route_returns_route(self, service: RouteManagementService) -> None:
        route = await service.add_route(
            name="Test Route",
            path_prefix="/test",
            upstream_url="http://test:8080",
        )
        assert route.name == "Test Route"
        assert route.path_prefix == "/test"
        assert route.route_id  # auto-generated UUID

    async def test_add_route_with_methods(self, service: RouteManagementService) -> None:
        route = await service.add_route(
            name="Restricted",
            path_prefix="/restricted",
            upstream_url="http://restricted:8080",
            methods=frozenset({"GET"}),
        )
        assert "GET" in route.methods

    async def test_list_routes_empty(self, service: RouteManagementService) -> None:
        routes = await service.list_routes()
        assert routes == []

    async def test_list_routes_after_add(self, service: RouteManagementService) -> None:
        await service.add_route("R1", "/r1", "http://r1:8080")
        await service.add_route("R2", "/r2", "http://r2:8080")
        routes = await service.list_routes()
        assert len(routes) == 2

    async def test_get_route_by_id(self, service: RouteManagementService) -> None:
        created = await service.add_route("R", "/r", "http://r:8080")
        fetched = await service.get_route(created.route_id)
        assert fetched == created

    async def test_get_nonexistent_route(self, service: RouteManagementService) -> None:
        assert await service.get_route("does-not-exist") is None

    async def test_remove_route(self, service: RouteManagementService) -> None:
        created = await service.add_route("R", "/r", "http://r:8080")
        removed = await service.remove_route(created.route_id)
        assert removed is True
        assert await service.get_route(created.route_id) is None

    async def test_remove_nonexistent_route(self, service: RouteManagementService) -> None:
        assert await service.remove_route("ghost") is False
