import { Request, Response, NextFunction } from 'express';
import { RateLimiterService } from '../services/rate-limiter.service';
import { createErrorResponse } from '../utils/errors';

export interface RateLimitOptions {
  windowMs: number;
  maxRequests: number;
  keyBy: 'ip' | 'userId' | 'apiKey';
  endpointLabel?: string;
}

export class RateLimitMiddleware {
  constructor(private readonly rateLimiter: RateLimiterService) {}

  limit(options: RateLimitOptions) {
    return async (req: Request, res: Response, next: NextFunction): Promise<void> => {
      const key = this.resolveKey(req, options.keyBy);
      const endpointLabel = options.endpointLabel ?? req.path;

      const result = await this.rateLimiter.consume(
        `${endpointLabel}:${key}`,
        options.windowMs,
        options.maxRequests,
      );

      // Always set rate limit headers
      res.setHeader('X-RateLimit-Limit', result.limit);
      res.setHeader('X-RateLimit-Remaining', Math.max(0, result.remaining));
      res.setHeader('X-RateLimit-Reset', result.resetAt);

      if (!result.allowed) {
        res.setHeader('Retry-After', result.retryAfter ?? Math.ceil(options.windowMs / 1000));
        res.status(429).json(
          createErrorResponse('RATE_LIMIT_EXCEEDED', 'Too many requests — please slow down', 429, req),
        );
        return;
      }

      next();
    };
  }

  private resolveKey(req: Request, keyBy: 'ip' | 'userId' | 'apiKey'): string {
    switch (keyBy) {
      case 'userId':
        return req.gateway.authContext?.userId ?? req.ip ?? 'unknown';
      case 'apiKey':
        return (req.headers['x-api-key'] as string) ?? req.ip ?? 'unknown';
      case 'ip':
      default:
        return req.ip ?? req.socket.remoteAddress ?? 'unknown';
    }
  }
}
