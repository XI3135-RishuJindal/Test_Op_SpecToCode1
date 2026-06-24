"""
Application configuration via environment variables.

Uses pydantic-settings for validation and .env file support.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import AnyHttpUrl, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── Service identity ──────────────────────────────────────────────────────
    app_name: str = Field(default="api-gateway", description="Human-readable service name")
    app_version: str = Field(default="0.1.0", description="Semantic version string")
    environment: Literal["development", "staging", "production"] = Field(
        default="development"
    )

    # ── Server ────────────────────────────────────────────────────────────────
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000, ge=1, le=65535)
    workers: int = Field(default=1, ge=1)
    log_level: Literal["debug", "info", "warning", "error", "critical"] = Field(
        default="info"
    )

    # ── Upstream services ─────────────────────────────────────────────────────
    identity_service_url: str = Field(
        default="http://identity-service:8001",
        description="Base URL of the identity / auth service",
    )

    # ── Redis ─────────────────────────────────────────────────────────────────
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL used for rate limiting and caching",
    )

    # ── Rate limiting ─────────────────────────────────────────────────────────
    rate_limit_requests: int = Field(
        default=100,
        ge=1,
        description="Maximum number of requests per window per client IP",
    )
    rate_limit_window_seconds: int = Field(
        default=60,
        ge=1,
        description="Sliding-window duration in seconds",
    )

    # ── Request size ──────────────────────────────────────────────────────────
    max_request_body_bytes: int = Field(
        default=1_048_576,  # 1 MiB
        ge=1,
        description="Maximum allowed request body size in bytes",
    )

    # ── OpenTelemetry ─────────────────────────────────────────────────────────
    otel_exporter_otlp_endpoint: str = Field(
        default="",
        description="OTLP gRPC endpoint for OpenTelemetry traces (empty = disabled)",
    )
    otel_service_name: str = Field(default="api-gateway")

    # ── CORS ──────────────────────────────────────────────────────────────────
    cors_allow_origins: list[str] = Field(
        default=["*"],
        description="List of allowed CORS origins",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached Settings instance (singleton)."""
    return Settings()
