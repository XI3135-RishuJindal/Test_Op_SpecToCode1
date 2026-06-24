"""
Outbound adapter — Redis-backed distributed rate limiter.

Uses a sliding-window counter stored in Redis.
Implements RateLimiterPort.
"""
from __future__ import annotations

import time

import redis.asyncio as aioredis

from app.core.ports import RateLimiterPort
from app.infrastructure.logging import get_logger

logger = get_logger(__name__)

_SCRIPT = """
local key    = KEYS[1]
local limit  = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
local now    = tonumber(ARGV[3])

redis.call('ZREMRANGEBYSCORE', key, '-inf', now - window * 1000)
local count = redis.call('ZCARD', key)
if count < limit then
    redis.call('ZADD', key, now, now)
    redis.call('PEXPIRE', key, window * 1000)
    return 1
end
return 0
"""


class RedisRateLimiter(RateLimiterPort):
    """Sliding-window rate limiter backed by Redis sorted sets."""

    def __init__(self, redis_client: aioredis.Redis) -> None:
        self._redis = redis_client
        self._script = self._redis.register_script(_SCRIPT)

    async def is_allowed(self, key: str, limit: int, window_seconds: int) -> bool:
        now_ms = int(time.time() * 1000)
        result = await self._script(
            keys=[f"ratelimit:{key}"],
            args=[limit, window_seconds, now_ms],
        )
        allowed = bool(result)
        if not allowed:
            logger.warning("rate_limit_exceeded", extra={"key": key})
        return allowed
