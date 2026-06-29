"""Traffic / metrics domain value objects."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class RequestMetric:
    """Captures metrics for a single proxied request.

    Attributes:
        request_id: Unique request identifier.
        route_id: Matched route identifier.
        upstream_id: Target upstream identifier.
        method: HTTP method.
        path: Original request path.
        status_code: HTTP response status code.
        latency_ms: Round-trip latency in milliseconds.
        timestamp: When the request was received (UTC).
        consumer_id: Authenticated consumer, if any.
    """

    request_id: str
    route_id: str
    upstream_id: str
    method: str
    path: str
    status_code: int
    latency_ms: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    consumer_id: str = ""


@dataclass
class TrafficSummary:
    """Aggregated traffic statistics.

    Attributes:
        total_requests: Total number of requests processed.
        total_errors: Number of 5xx responses.
        avg_latency_ms: Average latency across all requests.
        requests_per_second: Current throughput.
    """

    total_requests: int = 0
    total_errors: int = 0
    avg_latency_ms: float = 0.0
    requests_per_second: float = 0.0

    @property
    def error_rate(self) -> float:
        """Return the fraction of requests that resulted in errors."""
        if self.total_requests == 0:
            return 0.0
        return self.total_errors / self.total_requests
