"""Route management use-case."""
from __future__ import annotations

import uuid
from typing import Optional

from src.domain.route import Route
from src.ports.inbound import RouteRegistryPort


class RouteManagementService:
    """CRUD operations for gateway routing rules.

    Wraps the :class:`~src.ports.inbound.RouteRegistryPort` with
    business-level validation and ID generation.
    """

    def __init__(self, route_registry: RouteRegistryPort) -> None:
        self._registry = route_registry

    async def add_route(
        self,
        name: str,
        path_prefix: str,
        upstream_url: str,
        strip_prefix: bool = True,
        methods: Optional[frozenset[str]] = None,
        tags: Optional[tuple[str, ...]] = None,
    ) -> Route:
        """Create and register a new route.

        Args:
            name: Human-readable route name.
            path_prefix: URL prefix to match.
            upstream_url: Target upstream base URL.
            strip_prefix: Strip the prefix before forwarding.
            methods: Allowed HTTP methods (empty = all).
            tags: Optional metadata tags.

        Returns:
            The persisted :class:`~src.domain.route.Route`.
        """
        route = Route(
            route_id=str(uuid.uuid4()),
            name=name,
            path_prefix=path_prefix,
            upstream_url=upstream_url,
            strip_prefix=strip_prefix,
            methods=methods or frozenset(),
            tags=tags or (),
        )
        return await self._registry.register_route(route)

    async def remove_route(self, route_id: str) -> bool:
        """Remove a route by ID.

        Returns:
            ``True`` if the route existed and was removed.
        """
        return await self._registry.deregister_route(route_id)

    async def list_routes(self) -> list[Route]:
        """Return all registered routes."""
        return await self._registry.list_routes()

    async def get_route(self, route_id: str) -> Optional[Route]:
        """Return a single route or ``None`` if not found."""
        return await self._registry.get_route(route_id)
