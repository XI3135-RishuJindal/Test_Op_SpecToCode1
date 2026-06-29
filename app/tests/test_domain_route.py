"""Tests for the Route domain entity."""
from __future__ import annotations

import pytest

from src.domain.route import Route


@pytest.fixture()
def sample_route() -> Route:
    return Route(
        route_id="r-001",
        name="Users Service",
        path_prefix="/api/v1/users",
        upstream_url="http://users-service:8080",
        strip_prefix=True,
        methods=frozenset({"GET", "POST"}),
    )


class TestRouteMatching:
    def test_matches_exact_prefix(self, sample_route: Route) -> None:
        assert sample_route.matches("/api/v1/users", "GET") is True

    def test_matches_sub_path(self, sample_route: Route) -> None:
        assert sample_route.matches("/api/v1/users/123", "GET") is True

    def test_does_not_match_different_prefix(self, sample_route: Route) -> None:
        assert sample_route.matches("/api/v1/orders", "GET") is False

    def test_does_not_match_disallowed_method(self, sample_route: Route) -> None:
        assert sample_route.matches("/api/v1/users", "DELETE") is False

    def test_matches_all_methods_when_empty(self) -> None:
        route = Route(
            route_id="r-002",
            name="Open Route",
            path_prefix="/open",
            upstream_url="http://open:8080",
            methods=frozenset(),
        )
        assert route.matches("/open/anything", "DELETE") is True

    def test_disabled_route_never_matches(self, sample_route: Route) -> None:
        disabled = Route(
            route_id=sample_route.route_id,
            name=sample_route.name,
            path_prefix=sample_route.path_prefix,
            upstream_url=sample_route.upstream_url,
            enabled=False,
        )
        assert disabled.matches("/api/v1/users", "GET") is False


class TestRoutePathRewrite:
    def test_strip_prefix(self, sample_route: Route) -> None:
        assert sample_route.rewrite_path("/api/v1/users/123") == "/123"

    def test_strip_prefix_root(self, sample_route: Route) -> None:
        assert sample_route.rewrite_path("/api/v1/users") == "/"

    def test_no_strip_prefix(self) -> None:
        route = Route(
            route_id="r-003",
            name="No Strip",
            path_prefix="/api",
            upstream_url="http://svc:8080",
            strip_prefix=False,
        )
        assert route.rewrite_path("/api/v1/resource") == "/api/v1/resource"
