import dotenv from 'dotenv';

dotenv.config();

function required(key: string): string {
  const val = process.env[key];
  if (!val) throw new Error(`Missing required environment variable: ${key}`);
  return val;
}

function optional(key: string, defaultValue: string): string {
  return process.env[key] ?? defaultValue;
}

function optionalNumber(key: string, defaultValue: number): number {
  const val = process.env[key];
  return val ? parseInt(val, 10) : defaultValue;
}

export const config = {
  env: optional('NODE_ENV', 'development'),
  port: optionalNumber('PORT', 3000),

  // Service info
  service: {
    name: 'api-gateway-service',
    version: process.env.npm_package_version ?? '1.0.0',
  },

  // JWT / OIDC
  jwt: {
    issuer: optional('JWT_ISSUER', 'https://auth.example.com/'),
    audience: optional('JWT_AUDIENCE', 'api.example.com'),
    jwksUri: optional('JWT_JWKS_URI', 'https://auth.example.com/.well-known/jwks.json'),
    jwksCacheTtl: optionalNumber('JWKS_CACHE_TTL_MS', 600_000), // 10 min
    accessTokenTtl: optionalNumber('ACCESS_TOKEN_TTL_S', 3600),   // 1h
    refreshTokenTtl: optionalNumber('REFRESH_TOKEN_TTL_S', 2592000), // 30d
  },

  // Redis
  redis: {
    url: optional('REDIS_URL', 'redis://localhost:6379'),
    mfaSessionTtl: optionalNumber('MFA_SESSION_TTL_S', 300),
    idempotencyKeyTtl: optionalNumber('IDEMPOTENCY_KEY_TTL_S', 86400), // 24h
  },

  // Postgres
  database: {
    url: optional('DATABASE_URL', 'postgresql://gateway:gateway@localhost:5432/gateway'),
  },

  // Kafka
  kafka: {
    brokers: optional('KAFKA_BROKERS', 'localhost:9092').split(','),
    auditTopic: optional('KAFKA_AUDIT_TOPIC', 'gateway.audit-events'),
    clientId: optional('KAFKA_CLIENT_ID', 'api-gateway-service'),
  },

  // OPA
  opa: {
    url: optional('OPA_URL', 'http://localhost:8181'),
    policyPath: optional('OPA_POLICY_PATH', '/v1/data/gateway/authz/allow'),
    timeoutMs: optionalNumber('OPA_TIMEOUT_MS', 5000),
  },

  // Upstream services
  upstreams: {
    userProfile: optional('USER_PROFILE_SERVICE_URL', 'http://user-profile-service:4001'),
    mfa: optional('MFA_SERVICE_URL', 'http://mfa-service:4002'),
    reporting: optional('REPORTING_SERVICE_URL', 'http://reporting-service:4003'),
    payment: optional('PAYMENT_SERVICE_URL', 'http://payment-service:4004'),
    notification: optional('NOTIFICATION_SERVICE_URL', 'http://notification-service:4005'),
  },

  // Proxy / circuit breaker
  proxy: {
    upstreamTimeoutMs: optionalNumber('UPSTREAM_TIMEOUT_MS', 30_000),
    circuitBreakerThreshold: optionalNumber('CB_THRESHOLD', 5),
    circuitBreakerResetMs: optionalNumber('CB_RESET_MS', 30_000),
  },

  // Rate limits (defaults, overridable via DB policies)
  rateLimits: {
    authLogin: { windowMs: 60_000, maxRequests: 10 },     // 10/min per IP
    payments: { windowMs: 60_000, maxRequests: 100 },      // 100/min per user
    general: { windowMs: 60_000, maxRequests: 1000 },      // 1000/min per user
    admin: { windowMs: 60_000, maxRequests: 200 },
  },

  // Observability
  observability: {
    logLevel: optional('LOG_LEVEL', 'info'),
    jaegerEndpoint: optional('JAEGER_ENDPOINT', 'http://localhost:14268/api/traces'),
    prometheusEnabled: optional('PROMETHEUS_ENABLED', 'true') === 'true',
  },

  // CORS
  cors: {
    allowedOrigins: optional('CORS_ALLOWED_ORIGINS', '*').split(','),
  },
} as const;
