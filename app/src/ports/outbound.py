"""Outbound port interfaces (driven side)."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Optional

from src.domain.security import ApiKey, JwtClaims
from src.domain.traffic import RequestMetric


class HttpClientPort(ABC):
    """Port for making outbound HTTP requests to upstream services."""

    @abstractmethod
    async def forward(
        self,
        method: str,
        url: str,
        headers: dict[str, str],
        body: Optional[bytes],
        timeout_seconds: float = 30.0,
    ) -> tuple[int, dict[str, str], bytes]:
        """Forward a request and return ``(status_code, headers, body)``."""


class SecurityPort(ABC):
    """Port for authentication and authorisation operations."""

    @abstractmethod
    async def validate_api_key(self, raw_key: str) -> Optional[ApiKey]:
        """Return the ``ApiKey`` entity if *raw_key* is valid, else ``None``."""

    @abstractmethod
    async def validate_jwt(self, token: str) -> Optional[JwtClaims]:
        """Return decoded ``JwtClaims`` if *token* is valid, else ``None``."""

    @abstractmethod
    async def store_api_key(self, api_key: ApiKey) -> None:
        """Persist an API key."""

    @abstractmethod
    async def revoke_api_key(self, key_id: str) -> bool:
        """Revoke an API key; return ``True`` if it existed."""


class MetricsPort(ABC):
    """Port for recording and querying traffic metrics."""

    @abstractmethod
    async def record(self, metric: RequestMetric) -> None:
        """Persist a single request metric."""

    @abstractmethod
    async def get_summary(self) -> dict[str, Any]:
        """Return an aggregated traffic summary."""


class CachePort(ABC):
    """Port for caching (e.g. rate-limit counters, route cache)."""

    @abstractmethod
    async def get(self, key: str) -> Optional[str]:
        """Return the cached value for *key*, or ``None``."""

    @abstractmethod
    async def set(self, key: str, value: str, ttl_seconds: int = 60) -> None:
        """Store *value* under *key* with an optional TTL."""

    @abstractmethod
    async def increment(self, key: str, ttl_seconds: int = 60) -> int:
        """Atomically increment a counter and return the new value."""

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Remove *key* from the cache."""
