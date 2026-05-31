import { getRedisClient } from '../infrastructure/redis.client';
import { RateLimitResult } from '../types';
import { logger } from '../infrastructure/logger';
import { rateLimitHits } from '../infrastructure/metrics';

// Lua script for atomic rate limiting (sliding window counter)
const RATE_LIMIT_SCRIPT = `
local key = KEYS[1]
local window_ms = tonumber(ARGV[1])
local max_requests = tonumber(ARGV[2])
local now = tonumber(ARGV[3])
local window_start = now - window_ms

-- Remove expired entries
redis.call('ZREMRANGEBYSCORE', key, '-inf', window_start)

-- Count current requests in window
local count = redis.call('ZCARD', key)

if count < max_requests then
  -- Add current request
  redis.call('ZADD', key, now, now .. '-' .. math.random(1000000))
  redis.call('PEXPIRE', key, window_ms)
  return {1, max_requests, max_requests - count - 1, now + window_ms}
else
  -- Get oldest entry to compute retry-after
  local oldest = redis.call('ZRANGE', key, 0, 0, 'WITHSCORES')
  local reset_at = tonumber(oldest[2]) + window_ms
  return {0, max_requests, 0, reset_at}
end
`;

export class RateLimiterService {
  async consume(key: string, windowMs: number, maxRequests: number): Promise<RateLimitResult> {
    try {
      const redis = getRedisClient();
      const now = Date.now();

      const result = await redis.eval(
        RATE_LIMIT_SCRIPT,
        1,
        `rl:${key}`,
        String(windowMs),
        String(maxRequests),
        String(now),
      ) as [number, number, number, number];

      const [allowed, limit, remaining, resetAt] = result;
      const isAllowed = allowed === 1;

      if (!isAllowed) {
        rateLimitHits.inc({ endpoint: key.split(':')[0] ?? key, key_type: 'sliding_window' });
      }

      return {
        allowed: isAllowed,
        limit,
        remaining,
        resetAt: Math.ceil(resetAt / 1000),
        retryAfter: isAllowed ? undefined : Math.ceil((resetAt - now) / 1000),
      };
    } catch (err) {
      logger.error({ err, key }, 'Rate limiter error — allowing request');
      // Fail open: if Redis is unavailable, allow the request
      return {
        allowed: true,
        limit: maxRequests,
        remaining: maxRequests - 1,
        resetAt: Math.ceil((Date.now() + windowMs) / 1000),
      };
    }
  }
}
