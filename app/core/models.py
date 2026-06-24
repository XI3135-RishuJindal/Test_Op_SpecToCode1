"""
Domain models for the API Gateway / BFF Service.

These are pure data structures with no framework dependencies.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
import uuid


@dataclass(frozen=True)
class CorrelationContext:
    """Carries cross-cutting request identifiers through the call chain."""

    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    idempotency_key: Optional[str] = None


@dataclass(frozen=True)
class HealthStatus:
    """Result of a health-check probe."""

    status: str          # "ok" | "degraded" | "down"
    version: str
    details: dict = field(default_factory=dict)


@dataclass(frozen=True)
class ProxyRequest:
    """Normalised inbound request ready to be forwarded to an upstream."""

    method: str
    path: str
    headers: dict
    body: Optional[bytes]
    context: CorrelationContext


@dataclass(frozen=True)
class ProxyResponse:
    """Normalised response received from an upstream service."""

    status_code: int
    headers: dict
    body: bytes
