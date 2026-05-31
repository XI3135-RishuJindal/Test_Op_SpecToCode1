/**
 * Maps upstream HTTP status codes to gateway-appropriate responses.
 * Prevents leaking raw upstream error codes while preserving semantics.
 */
export function mapUpstreamStatus(upstreamStatus: number): number {
  if (upstreamStatus === 401) return 401;
  if (upstreamStatus === 403) return 403;
  if (upstreamStatus === 404) return 404;
  if (upstreamStatus === 409) return 409;
  if (upstreamStatus === 422) return 422;
  if (upstreamStatus === 429) return 429;
  if (upstreamStatus === 402) return 402;
  if (upstreamStatus >= 500) return 503; // upstream errors → 503
  return upstreamStatus;
}

/**
 * Builds a standardized upstream error code from status.
 */
export function upstreamErrorCode(status: number): string {
  if (status === 401) return 'UNAUTHORIZED';
  if (status === 403) return 'FORBIDDEN';
  if (status === 404) return 'NOT_FOUND';
  if (status === 409) return 'CONFLICT';
  if (status === 422) return 'VALIDATION_ERROR';
  if (status === 429) return 'RATE_LIMIT_EXCEEDED';
  if (status === 402) return 'PAYMENT_DECLINED';
  if (status >= 500) return 'UPSTREAM_ERROR';
  return 'UPSTREAM_ERROR';
}
