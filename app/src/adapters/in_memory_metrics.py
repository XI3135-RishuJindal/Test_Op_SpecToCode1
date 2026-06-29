"""In-memory metrics adapter (suitable for testing and single-node deployments)."""
from __future__ import annotations

from collections import deque
from typing import Any

from src.domain.traffic import RequestMetric
from src.ports.outbound import MetricsPort


class InMemoryMetricsAdapter(MetricsPort):
    """Stores request metrics in a bounded in-memory deque."""

    def __init__(self, max_records: int = 10_000) -> None:
        self._records: deque[RequestMetric] = deque(maxlen=max_records)

    async def record(self, metric: RequestMetric) -> None:
        self._records.append(metric)

    async def get_summary(self) -> dict[str, Any]:
        records = list(self._records)
        total = len(records)
        if total == 0:
            return {
                "total_requests": 0,
                "total_errors": 0,
                "avg_latency_ms": 0.0,
                "error_rate": 0.0,
            }
        errors = sum(1 for r in records if r.status_code >= 500)
        avg_latency = sum(r.latency_ms for r in records) / total
        return {
            "total_requests": total,
            "total_errors": errors,
            "avg_latency_ms": round(avg_latency, 2),
            "error_rate": round(errors / total, 4),
        }
