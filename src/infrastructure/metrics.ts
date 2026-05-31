import { Registry, Counter, Histogram, Gauge, collectDefaultMetrics } from 'prom-client';

export const registry = new Registry();

collectDefaultMetrics({ register: registry });

export const httpRequestDuration = new Histogram({
  name: 'gateway_http_request_duration_seconds',
  help: 'HTTP request duration in seconds',
  labelNames: ['method', 'route', 'status_code', 'upstream'],
  buckets: [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10],
  registers: [registry],
});

export const httpRequestTotal = new Counter({
  name: 'gateway_http_requests_total',
  help: 'Total number of HTTP requests',
  labelNames: ['method', 'route', 'status_code'],
  registers: [registry],
});

export const rateLimitHits = new Counter({
  name: 'gateway_rate_limit_hits_total',
  help: 'Total number of rate limit hits',
  labelNames: ['endpoint', 'key_type'],
  registers: [registry],
});

export const authFailures = new Counter({
  name: 'gateway_auth_failures_total',
  help: 'Total number of authentication failures',
  labelNames: ['reason'],
  registers: [registry],
});

export const upstreamErrors = new Counter({
  name: 'gateway_upstream_errors_total',
  help: 'Total number of upstream errors',
  labelNames: ['service', 'error_type'],
  registers: [registry],
});

export const circuitBreakerState = new Gauge({
  name: 'gateway_circuit_breaker_state',
  help: 'Circuit breaker state (0=closed, 1=open, 2=half-open)',
  labelNames: ['service'],
  registers: [registry],
});

export const activeWebSocketConnections = new Gauge({
  name: 'gateway_websocket_connections_active',
  help: 'Number of active WebSocket connections',
  registers: [registry],
});

export const auditEventsPublished = new Counter({
  name: 'gateway_audit_events_published_total',
  help: 'Total audit events published',
  labelNames: ['action', 'status'],
  registers: [registry],
});
