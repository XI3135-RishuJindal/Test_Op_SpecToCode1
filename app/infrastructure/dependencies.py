"""
Dependency-injection helpers for FastAPI.

These functions are used as FastAPI Depends() callables and wire together
the ports, adapters, and application services.
"""
from __future__ import annotations

from functools import lru_cache
from typing import AsyncGenerator

import redis.asyncio as aioredis
from fastapi import Depends

from app.application.gateway_service import GatewayService
from app.application.health_service import HealthService
from app.adapters.outbound.http_upstream_client import HttpUpstreamClient
from app.adapters.outbound.redis_rate_limiter import RedisRateLimiter
from app.infrastructure.config import Settings, get_settings


# ---------------------------------------------------------------------------
# Redis connection pool (shared singleton)
# ---------------------------------------------------------------------------

@lru_cache(maxsize=1)
def _get_redis_pool(redis_url: str) -> aioredis.Redis:
    return aioredis.from_url(redis_url, decode_responses=False)


def get_redis(settings: Settings = Depends(get_settings)) -> aioredis.Redis:
    return _get_redis_pool(settings.redis_url)


# ---------------------------------------------------------------------------
# Outbound adapters
# ---------------------------------------------------------------------------

def get_rate_limiter(
    redis: aioredis.Redis = Depends(get_redis),
) -> RedisRateLimiter:
    return RedisRateLimiter(redis)


def get_upstream_client(
    settings: Settings = Depends(get_settings),
) -> HttpUpstreamClient:
    return HttpUpstreamClient(base_url=settings.identity_service_url)


# ---------------------------------------------------------------------------
# Application services
# ---------------------------------------------------------------------------

def get_health_service(
    settings: Settings = Depends(get_settings),
) -> HealthService:
    return HealthService(settings)


def get_gateway_service(
    upstream: HttpUpstreamClient = Depends(get_upstream_client),
    rate_limiter: RedisRateLimiter = Depends(get_rate_limiter),
    settings: Settings = Depends(get_settings),
) -> GatewayService:
    return GatewayService(
        upstream_client=upstream,
        rate_limiter=rate_limiter,
        settings=settings,
    )
