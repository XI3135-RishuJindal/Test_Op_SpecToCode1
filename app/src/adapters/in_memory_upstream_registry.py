"""In-memory upstream registry adapter."""
from __future__ import annotations

from typing import Optional

from src.domain.upstream import Upstream
from src.ports.inbound import UpstreamRegistryPort


class InMemoryUpstreamRegistry(UpstreamRegistryPort):
    """In-memory implementation of :class:`UpstreamRegistryPort`."""

    def __init__(self) -> None:
        self._upstreams: dict[str, Upstream] = {}

    async def get_upstream(self, upstream_id: str) -> Optional[Upstream]:
        return self._upstreams.get(upstream_id)

    async def list_upstreams(self) -> list[Upstream]:
        return list(self._upstreams.values())

    async def register_upstream(self, upstream: Upstream) -> Upstream:
        self._upstreams[upstream.upstream_id] = upstream
        return upstream

    async def deregister_upstream(self, upstream_id: str) -> bool:
        if upstream_id in self._upstreams:
            del self._upstreams[upstream_id]
            return True
        return False
