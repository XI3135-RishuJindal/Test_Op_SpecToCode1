"""
Unit tests for core domain models and exceptions.
"""
from __future__ import annotations

import pytest

from app.core.exceptions import (
    GatewayError,
    InvalidCorrelationIdError,
    RateLimitExceededError,
    RequestTooLargeError,
    UpstreamUnavailableError,
)
from app.core.models import CorrelationContext, HealthStatus, ProxyRequest, ProxyResponse


class TestCorrelationContext:
    def test_auto_generates_correlation_id(self) -> None:
        ctx = CorrelationContext()
        assert ctx.correlation_id != ""
        assert len(ctx.correlation_id) == 36  # UUID4 format

    def test_accepts_explicit_correlation_id(self) -> None:
        ctx = CorrelationContext(correlation_id="my-id")
        assert ctx.correlation_id == "my-id"

    def test_idempotency_key_defaults_to_none(self) -> None:
        ctx = CorrelationContext()
        assert ctx.idempotency_key is None

    def test_is_frozen(self) -> None:
        ctx = CorrelationContext()
        with pytest.raises(Exception):
            ctx.correlation_id = "new-id"  # type: ignore[misc]


class TestHealthStatus:
    def test_status_and_version_required(self) -> None:
        hs = HealthStatus(status="ok", version="1.0.0")
        assert hs.status == "ok"
        assert hs.version == "1.0.0"

    def test_details_defaults_to_empty_dict(self) -> None:
        hs = HealthStatus(status="ok", version="1.0.0")
        assert hs.details == {}


class TestExceptions:
    def test_rate_limit_exceeded_has_429(self) -> None:
        exc = RateLimitExceededError()
        assert exc.status_code == 429

    def test_upstream_unavailable_has_502(self) -> None:
        exc = UpstreamUnavailableError("svc")
        assert exc.status_code == 502
        assert "svc" in exc.message

    def test_request_too_large_has_413(self) -> None:
        exc = RequestTooLargeError(1024)
        assert exc.status_code == 413
        assert "1024" in exc.message

    def test_invalid_correlation_id_has_400(self) -> None:
        exc = InvalidCorrelationIdError()
        assert exc.status_code == 400

    def test_gateway_error_default_500(self) -> None:
        exc = GatewayError("oops")
        assert exc.status_code == 500
