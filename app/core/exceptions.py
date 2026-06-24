"""
Custom exception hierarchy for the API Gateway / BFF Service.
"""
from __future__ import annotations


class GatewayError(Exception):
    """Base class for all gateway errors."""

    def __init__(self, message: str, status_code: int = 500) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class RateLimitExceededError(GatewayError):
    """Raised when a client exceeds the configured rate limit."""

    def __init__(self, message: str = "Rate limit exceeded") -> None:
        super().__init__(message, status_code=429)


class UpstreamUnavailableError(GatewayError):
    """Raised when an upstream service cannot be reached."""

    def __init__(self, upstream: str) -> None:
        super().__init__(f"Upstream '{upstream}' is unavailable", status_code=502)


class RequestTooLargeError(GatewayError):
    """Raised when the request body exceeds the configured size limit."""

    def __init__(self, max_bytes: int) -> None:
        super().__init__(
            f"Request body exceeds maximum allowed size of {max_bytes} bytes",
            status_code=413,
        )


class InvalidCorrelationIdError(GatewayError):
    """Raised when a supplied correlation-ID header is malformed."""

    def __init__(self) -> None:
        super().__init__("X-Correlation-ID header is malformed", status_code=400)
