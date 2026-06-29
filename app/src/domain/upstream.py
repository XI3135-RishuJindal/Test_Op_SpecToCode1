"""Upstream domain entity."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class HealthStatus(str, Enum):
    """Health status of an upstream service."""

    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class Upstream:
    """Represents an upstream (backend) service.

    Attributes:
        upstream_id: Unique identifier.
        name: Human-readable name.
        base_url: Base URL of the upstream service.
        health_check_path: Path used for health probing.
        weight: Load-balancing weight (higher = more traffic).
        health_status: Current health status.
        tags: Arbitrary metadata tags.
    """

    upstream_id: str
    name: str
    base_url: str
    health_check_path: str = "/health"
    weight: int = 1
    health_status: HealthStatus = HealthStatus.UNKNOWN
    tags: list[str] = field(default_factory=list)

    @property
    def health_check_url(self) -> str:
        """Full URL used for health probing."""
        return f"{self.base_url.rstrip('/')}{self.health_check_path}"

    def mark_healthy(self) -> None:
        """Mark this upstream as healthy."""
        self.health_status = HealthStatus.HEALTHY

    def mark_unhealthy(self) -> None:
        """Mark this upstream as unhealthy."""
        self.health_status = HealthStatus.UNHEALTHY
