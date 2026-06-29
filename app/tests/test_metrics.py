"""Tests for the InMemoryMetricsAdapter."""
from __future__ import annotations

import pytest

from src.adapters.in_memory_metrics import InMemoryMetricsAdapter
from src.domain.traffic import RequestMetric


@pytest.fixture()
def adapter() -> InMemoryMetricsAdapter:
    return InMemoryMetricsAdapter()


@pytest.fixture()
def sample_metric() -> RequestMetric:
    return RequestMetric(
        request_id="req-1",
        route_id="r-1",
        upstream_id="http://upstream:8080",
        method="GET",
        path="/api/v1/resource",
        status_code=200,
        latency_ms=42.5,
    )


@pytest.mark.asyncio
class TestInMemoryMetricsAdapter:
    async def test_summary_empty(self, adapter: InMemoryMetricsAdapter) -> None:
        summary = await adapter.get_summary()
        assert summary["total_requests"] == 0
        assert summary["total_errors"] == 0
        assert summary["avg_latency_ms"] == 0.0

    async def test_record_increments_total(
        self, adapter: InMemoryMetricsAdapter, sample_metric: RequestMetric
    ) -> None:
        await adapter.record(sample_metric)
        summary = await adapter.get_summary()
        assert summary["total_requests"] == 1

    async def test_error_counted_for_5xx(self, adapter: InMemoryMetricsAdapter) -> None:
        error_metric = RequestMetric(
            request_id="req-2",
            route_id="r-1",
            upstream_id="http://upstream:8080",
            method="GET",
            path="/api/v1/resource",
            status_code=500,
            latency_ms=10.0,
        )
        await adapter.record(error_metric)
        summary = await adapter.get_summary()
        assert summary["total_errors"] == 1

    async def test_avg_latency(self, adapter: InMemoryMetricsAdapter) -> None:
        for latency in [10.0, 20.0, 30.0]:
            await adapter.record(
                RequestMetric(
                    request_id=f"req-{latency}",
                    route_id="r-1",
                    upstream_id="http://upstream:8080",
                    method="GET",
                    path="/",
                    status_code=200,
                    latency_ms=latency,
                )
            )
        summary = await adapter.get_summary()
        assert summary["avg_latency_ms"] == 20.0
