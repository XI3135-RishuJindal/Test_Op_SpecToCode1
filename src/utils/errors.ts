import { Request } from 'express';
import { ErrorResponse } from '../types';

export function createErrorResponse(
  error: string,
  message: string,
  statusCode: number,
  req: Request,
): ErrorResponse {
  return {
    error,
    message,
    statusCode,
    timestamp: new Date().toISOString(),
    requestId: req.gateway?.requestId ?? 'unknown',
    path: req.path,
  };
}

export class GatewayError extends Error {
  constructor(
    public readonly code: string,
    message: string,
    public readonly statusCode: number,
  ) {
    super(message);
    this.name = 'GatewayError';
  }
}

export class UnauthorizedError extends GatewayError {
  constructor(message = 'Unauthorized') {
    super('UNAUTHORIZED', message, 401);
  }
}

export class ForbiddenError extends GatewayError {
  constructor(message = 'Forbidden') {
    super('FORBIDDEN', message, 403);
  }
}

export class NotFoundError extends GatewayError {
  constructor(message = 'Not found') {
    super('NOT_FOUND', message, 404);
  }
}

export class ConflictError extends GatewayError {
  constructor(message = 'Conflict', code = 'CONFLICT') {
    super(code, message, 409);
  }
}

export class ValidationError extends GatewayError {
  constructor(message = 'Validation failed') {
    super('VALIDATION_ERROR', message, 422);
  }
}

export class UpstreamError extends GatewayError {
  constructor(message = 'Upstream service error', statusCode = 503) {
    super('UPSTREAM_ERROR', message, statusCode);
  }
}

export class RateLimitError extends GatewayError {
  constructor(message = 'Rate limit exceeded') {
    super('RATE_LIMIT_EXCEEDED', message, 429);
  }
}
