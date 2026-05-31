import { Request, Response, NextFunction } from 'express';

const VERSION_PATTERN = /^\/api\/(v\d+)\//;

export function apiVersioningMiddleware(req: Request, _res: Response, next: NextFunction): void {
  const match = req.path.match(VERSION_PATTERN);
  if (match) {
    req.gateway.apiVersion = match[1];
  }
  next();
}
