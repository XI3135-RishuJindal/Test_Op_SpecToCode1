"""Route domain entity."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class Route:
    """Represents a single routing rule in the gateway.

    Attributes:
        route_id: Unique identifier for the route.
        name: Human-readable name.
        path_prefix: URL path prefix to match (e.g. ``/api/v1/users``).
        upstream_url: Target upstream service URL.
        strip_prefix: Whether to strip the matched prefix before forwarding.
        methods: HTTP methods this route accepts. Empty set means all methods.
        enabled: Whether the route is active.
        tags: Arbitrary metadata tags.
    """

    route_id: str
    name: str
    path_prefix: str
    upstream_url: str
    strip_prefix: bool = True
    methods: frozenset[str] = field(default_factory=frozenset)
    enabled: bool = True
    tags: tuple[str, ...] = field(default_factory=tuple)

    def matches(self, path: str, method: str) -> bool:
        """Return ``True`` if *path* and *method* match this route."""
        if not self.enabled:
            return False
        path_matches = path.startswith(self.path_prefix)
        method_matches = not self.methods or method.upper() in self.methods
        return path_matches and method_matches

    def rewrite_path(self, original_path: str) -> str:
        """Rewrite *original_path* for the upstream service."""
        if self.strip_prefix and original_path.startswith(self.path_prefix):
            stripped = original_path[len(self.path_prefix):]
            return stripped or "/"
        return original_path
