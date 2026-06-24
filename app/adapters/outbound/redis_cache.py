"""
Outbound adapter — Redis-backed cache.

Implements CachePort.
"""
from __future__ import annotations

from typing import Optional

import redis.asyncio as aioredis

from app.core.ports import CachePort


class RedisCache(CachePort):
    """Generic key/value cache backed by Redis."""

    def __init__(self, redis_client: aioredis.Redis) -> None:
        self._redis = redis_client

    async def get(self, key: str) -> Optional[bytes]:
        value: Optional[bytes] = await self._redis.get(key)
        return value

    async def set(self, key: str, value: bytes, ttl_seconds: int = 60) -> None:
        await self._redis.set(key, value, ex=ttl_seconds)

    async def delete(self, key: str) -> None:
        await self._redis.delete(key)
