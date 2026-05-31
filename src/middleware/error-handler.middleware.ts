import { Request, Response, NextFunction } from 'express';
import { logger } from '../infrastructure/logger';
import { createErrorResponse } from '../utils/errors';
import { ZodError } from 'zod';

export function errorHandlerMiddleware(
  err: unknown,
  req: Request,
  res: Response,
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  _next: NextFunction,
): void {
  if (err instanceof ZodError) {
    const details = err.errors.map((e) => ({
      field: e.path.join('.'),
      message: e.message,
      code: e.code,
    }));

    res.status(422).json({
      ...createErrorResponse('VALIDATION_ERROR', 'Request validation failed', 422, req),
      details,
    });
    return;
  }

  const error = err as { statusCode?: number; message?: string; code?: string };

  const statusCode = error.statusCode ?? 500;
  const message = statusCode < 500 ? (error.message ?? 'An error occurred') : 'Internal server error';
  const code = error.code ?? (statusCode >= 500 ? 'INTERNAL_ERROR' : 'BAD_REQUEST');

  if (statusCode >= 500) {
    logger.error({ err, requestId: req.gateway?.requestId }, 'Unhandled server error');
  }

  res.status(statusCode).json(createErrorResponse(code, message, statusCode, req));
}
