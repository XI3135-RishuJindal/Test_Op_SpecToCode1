"""Application configuration via environment variables."""
from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All configuration values for the API Gateway Service.

    Values are read from environment variables (case-insensitive) or
    from a ``.env`` file in the working directory.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ──────────────────────────────────────────────────────────
    app_env: str = Field("development", description="Runtime environment")
    app_port: int = Field(8000, description="HTTP port to listen on")
    app_host: str = Field("0.0.0.0", description="Bind address")
    app_version: str = Field("1.0.0", description="Service version")
    log_level: str = Field("info", description="Logging level")

    # ── Kong ─────────────────────────────────────────────────────────────────
    kong_admin_url: str = Field("http://kong:8001", description="Kong Admin API URL")
    kong_proxy_url: str = Field("http://kong:8000", description="Kong Proxy URL")
    kong_admin_token: str = Field("", description="Kong Admin API token")

    # ── Tyk ──────────────────────────────────────────────────────────────────
    tyk_gateway_url: str = Field("http://tyk:8080", description="Tyk Gateway URL")
    tyk_dashboard_url: str = Field("http://tyk-dashboard:3000", description="Tyk Dashboard URL")
    tyk_secret: str = Field("tyk-secret-key", description="Tyk shared secret")
    tyk_org_id: str = Field("default", description="Tyk organisation ID")

    # ── Nginx ────────────────────────────────────────────────────────────────
    nginx_upstream_host: str = Field("localhost", description="Nginx upstream host")
    nginx_upstream_port: int = Field(8080, description="Nginx upstream port")

    # ── Security ─────────────────────────────────────────────────────────────
    jwt_secret: str = Field("change-me-in-production", description="JWT signing secret")
    jwt_algorithm: str = Field("HS256", description="JWT signing algorithm")
    jwt_expiry_seconds: int = Field(3600, description="JWT expiry in seconds")
    api_key_header: str = Field("X-API-Key", description="Header name for API key auth")

    # ── Rate Limiting ────────────────────────────────────────────────────────
    rate_limit_rps: int = Field(100, description="Requests per second limit")
    rate_limit_burst: int = Field(200, description="Burst capacity")

    # ── CORS ─────────────────────────────────────────────────────────────────
    cors_allowed_origins: str = Field("*", description="Comma-separated allowed origins")
    cors_allowed_methods: str = Field("GET,POST,PUT,PATCH,DELETE,OPTIONS")
    cors_allowed_headers: str = Field("*")

    # ── Metrics ──────────────────────────────────────────────────────────────
    metrics_enabled: bool = Field(True, description="Enable metrics collection")
    metrics_path: str = Field("/metrics", description="Metrics endpoint path")
    prometheus_port: int = Field(9090, description="Prometheus scrape port")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the cached application settings singleton."""
    return Settings()
