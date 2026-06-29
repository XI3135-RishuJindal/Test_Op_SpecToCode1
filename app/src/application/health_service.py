"""Health check use-case."""
from __future__ import annotations

from typing import Any

from src.ports.outbound import MetricsPort


class HealthService:
    """Provides the gateway's own health status.

    Aggregates liveness and readiness information from internal
    sub-systems and returns a structured health payload.
    """

    def __init__(self, metrics: MetricsPort) -> None:
        self._metrics = metrics

    async def check(self) -> dict[str, Any]:
        """Return a health-check payload.

        Returns:
            A dictionary with at minimum ``status`` (``"ok"`` or
            ``"degraded"``) and ``details`` sub-keys.
        """
        try:
            summary = await self._metrics.get_summary()
            metrics_ok = True
        except Exception:  # noqa: BLE001
            summary = {}
            metrics_ok = False

        status = "ok" if metrics_ok else "degraded"

        return {
            "status": status,
            "service": "api-gateway-service",
            "details": {
                "metrics": "ok" if metrics_ok else "unavailable",
                "traffic_summary": summary,
            },
        }
