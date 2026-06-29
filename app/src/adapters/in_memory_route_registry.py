"""In-memory route registry adapter (suitable for testing and single-node deployments)."""
from __future__ import annotations

from typing import Optional

from src.domain.route import Route
from src.ports.inbound import RouteRegistryPort


class InMemoryRouteRegistry(RouteRegistryPort):
    """Thread-safe (asyncio) in-memory implementation of :class:`RouteRegistryPort`.

    Routes are stored in insertion order; the first matching route wins
    during resolution (most-specific-first ordering is the caller's
    responsibility).
    """

    def __init__(self) -> None:
        self._routes: dict[str, Route] = {}

    async def get_route(self, route_id: str) -> Optional[Route]:
        return self._routes.get(route_id)

    async def list_routes(self) -> list[Route]:
        return list(self._routes.values())

    async def register_route(self, route: Route) -> Route:
        self._routes[route.route_id] = route
        return route

    async def deregister_route(self, route_id: str) -> bool:
        if route_id in self._routes:
            del self._routes[route_id]
            return True
        return False

    async def resolve_route(self, path: str, method: str) -> Optional[Route]:
        """Return the longest-prefix-matching enabled route."""
        best: Optional[Route] = None
        best_len = -1
        for route in self._routes.values():
            if route.matches(path, method):
                prefix_len = len(route.path_prefix)
                if prefix_len > best_len:
                    best = route
                    best_len = prefix_len
        return best
