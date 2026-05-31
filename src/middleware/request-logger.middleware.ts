import { Request, Response, NextFunction } from 'express';
import { logger } from '../infrastructure/logger';
import { httpRequestDuration, httpRequestTotal } from '../infrastructure/metrics';

export function requestLoggerMiddleware(req: Request, res: Response, next: NextFunction): void {
  const startTime = req.gateway?.startTime ?? Date.now();
  const requestId = req.gateway?.requestId ?? 'unknown';

  logger.info({
    requestId,
    method: req.method,
    path: req.path,
    ip: req.ip,
    userAgent: req.headers['user-agent'],
  }, 'Incoming request');

  res.on('finish', () => {
    const durationMs = Date.now() - startTime;
    const durationSec = durationMs / 1000;
    const route = req.route?.path ?? req.path;

    logger.info({
      requestId,
      method: req.method,
      path: req.path,
      statusCode: res.statusCode,
      durationMs,
      userId: req.gateway?.authContext?.userId,
    }, 'Request completed');

    httpRequestDuration.observe(
      { method: req.method, route, status_code: String(res.statusCode), upstream: '' },
      durationSec,
    );

    httpRequestTotal.inc({
      method: req.method,
      route,
      status_code: String(res.statusCode),
    });
  });

  next();
}
