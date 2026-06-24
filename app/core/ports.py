"""
Port interfaces (abstract base classes) for the API Gateway / BFF Service.

Ports define the contracts that adapters must fulfil.  They contain no
implementation details — only the shape of the interaction.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from app.core.models import HealthStatus, ProxyRequest, ProxyResponse


# ---------------------------------------------------------------------------
# Inbound ports  (driven by external callers → application)
# ---------------------------------------------------------------------------

class HealthCheckPort(ABC):
    """Inbound port: query the liveness / readiness of the service."""

    @abstractmethod
    async def check(self) -> HealthStatus:
        ...


class GatewayPort(ABC):
    """Inbound port: proxy an HTTP request to an upstream service."""

    @abstractmethod
    async def forward(self, request: ProxyRequest) -> ProxyResponse:
        ...


# ---------------------------------------------------------------------------
# Outbound ports  (application → driven adapters)
# ---------------------------------------------------------------------------

class UpstreamClientPort(ABC):
    """Outbound port: send an HTTP request to an upstream service."""

    @abstractmethod
    async def send(self, request: ProxyRequest) -> ProxyResponse:
        ...


class RateLimiterPort(ABC):
    """Outbound port: check and record rate-limit counters."""

    @abstractmethod
    async def is_allowed(self, key: str, limit: int, window_seconds: int) -> bool:
        """Return True if the request is within the allowed rate."""
        ...


class MetricsPort(ABC):
    """Outbound port: emit latency and access-log metrics."""

    @abstractmethod
    def record_request(
        self,
        method: str,
        path: str,
        status_code: int,
        duration_ms: float,
    ) -> None:
        ...


class CachePort(ABC):
    """Outbound port: generic key/value cache (backed by Redis)."""

    @abstractmethod
    async def get(self, key: str) -> Optional[bytes]:
        ...

    @abstractmethod
    async def set(self, key: str, value: bytes, ttl_seconds: int = 60) -> None:
        ...

    @abstractmethod
    async def delete(self, key: str) -> None:
        ...
