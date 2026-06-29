"""Inbound port interfaces (driving side)."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from src.domain.route import Route
from src.domain.upstream import Upstream


class RouteRegistryPort(ABC):
    """Port for managing routing rules."""

    @abstractmethod
    async def get_route(self, route_id: str) -> Optional[Route]:
        """Retrieve a route by its identifier."""

    @abstractmethod
    async def list_routes(self) -> list[Route]:
        """Return all registered routes."""

    @abstractmethod
    async def register_route(self, route: Route) -> Route:
        """Persist a new route and return it."""

    @abstractmethod
    async def deregister_route(self, route_id: str) -> bool:
        """Remove a route; return ``True`` if it existed."""

    @abstractmethod
    async def resolve_route(self, path: str, method: str) -> Optional[Route]:
        """Find the best matching route for *path* and *method*."""


class UpstreamRegistryPort(ABC):
    """Port for managing upstream services."""

    @abstractmethod
    async def get_upstream(self, upstream_id: str) -> Optional[Upstream]:
        """Retrieve an upstream by its identifier."""

    @abstractmethod
    async def list_upstreams(self) -> list[Upstream]:
        """Return all registered upstreams."""

    @abstractmethod
    async def register_upstream(self, upstream: Upstream) -> Upstream:
        """Persist a new upstream and return it."""

    @abstractmethod
    async def deregister_upstream(self, upstream_id: str) -> bool:
        """Remove an upstream; return ``True`` if it existed."""
