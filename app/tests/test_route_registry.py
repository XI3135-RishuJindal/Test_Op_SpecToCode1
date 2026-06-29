"""Tests for the in-memory route registry adapter."""
from __future__ import annotations

import pytest

from src.adapters.in_memory_route_registry import InMemoryRouteRegistry
from src.domain.route import Route


@pytest.fixture()
def registry() -> InMemoryRouteRegistry:
    return InMemoryRouteRegistry()


@pytest.fixture()
def route_a() -> Route:
    return Route(
        route_id="r-a",
        name="Route A",
        path_prefix="/a",
        upstream_url="http://a:8080",
    )


@pytest.fixture()
def route_b() -> Route:
    return Route(
        route_id="r-b",
        name="Route B",
        path_prefix="/a/b",
        upstream_url="http://b:8080",
    )


@pytest.mark.asyncio
class TestInMemoryRouteRegistry:
    async def test_register_and_get(self, registry: InMemoryRouteRegistry, route_a: Route) -> None:
        await registry.register_route(route_a)
        result = await registry.get_route("r-a")
        assert result == route_a

    async def test_get_nonexistent_returns_none(self, registry: InMemoryRouteRegistry) -> None:
        assert await registry.get_route("nonexistent") is None

    async def test_list_routes(self, registry: InMemoryRouteRegistry, route_a: Route, route_b: Route) -> None:
        await registry.register_route(route_a)
        await registry.register_route(route_b)
        routes = await registry.list_routes()
        assert len(routes) == 2

    async def test_deregister_existing(self, registry: InMemoryRouteRegistry, route_a: Route) -> None:
        await registry.register_route(route_a)
        removed = await registry.deregister_route("r-a")
        assert removed is True
        assert await registry.get_route("r-a") is None

    async def test_deregister_nonexistent(self, registry: InMemoryRouteRegistry) -> None:
        assert await registry.deregister_route("ghost") is False

    async def test_resolve_longest_prefix_wins(
        self,
        registry: InMemoryRouteRegistry,
        route_a: Route,
        route_b: Route,
    ) -> None:
        await registry.register_route(route_a)
        await registry.register_route(route_b)
        resolved = await registry.resolve_route("/a/b/resource", "GET")
        assert resolved is not None
        assert resolved.route_id == "r-b"

    async def test_resolve_no_match_returns_none(self, registry: InMemoryRouteRegistry, route_a: Route) -> None:
        await registry.register_route(route_a)
        assert await registry.resolve_route("/z/unknown", "GET") is None
