"""
Application service — health check use case.

Implements HealthCheckPort (inbound port).
"""
from __future__ import annotations

from app.core.models import HealthStatus
from app.core.ports import HealthCheckPort
from app.infrastructure.config import Settings


class HealthService(HealthCheckPort):
    """Returns the current liveness / readiness status of the gateway."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def check(self) -> HealthStatus:
        return HealthStatus(
            status="ok",
            version=self._settings.app_version,
            details={
                "environment": self._settings.environment,
                "upstream_identity": self._settings.identity_service_url,
            },
        )
