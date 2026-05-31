import 'express-async-errors';
import express, { Application } from 'express';
import cors from 'cors';
import { config } from './config';

// Middleware
import { requestIdMiddleware } from './middleware/request-id.middleware';
import { securityHeadersMiddleware } from './middleware/security-headers.middleware';
import { apiVersioningMiddleware } from './middleware/versioning.middleware';
import { requestLoggerMiddleware } from './middleware/request-logger.middleware';
import { errorHandlerMiddleware } from './middleware/error-handler.middleware';
import { AuthMiddleware } from './middleware/auth.middleware';
import { RbacMiddleware } from './middleware/rbac.middleware';
import { RateLimitMiddleware } from './middleware/rate-limit.middleware';

// Services
import { AuthService } from './services/auth.service';
import { RbacService } from './services/rbac.service';
import { RateLimiterService } from './services/rate-limiter.service';
import { AuditService } from './services/audit.service';
import { MfaOrchestrator } from './services/mfa.orchestrator';
import { RoutingService } from './services/routing.service';
import { RateLimitPolicyService } from './services/rate-limit-policy.service';
import { RbacPolicyService } from './services/rbac-policy.service';
import { IdempotencyService } from './services/idempotency.service';

// Routes
import { createSystemRouter } from './routes/system.routes';
import { createAuthRouter } from './routes/auth.routes';
import { createUsersRouter } from './routes/users.routes';
import { createReportsRouter } from './routes/reports.routes';
import { createPaymentsRouter } from './routes/payments.routes';
import { createNotificationsRouter } from './routes/notifications.routes';
import { createGatewayAdminRouter } from './routes/gateway-admin.routes';

export function createApp(): Application {
  const app = express();

  // ---- Instantiate services ----
  const authService = new AuthService();
  const rbacService = new RbacService();
  const rateLimiterService = new RateLimiterService();
  const auditService = new AuditService();
  const mfaOrchestrator = new MfaOrchestrator(authService);
  const routingService = new RoutingService();
  const rateLimitPolicyService = new RateLimitPolicyService();
  const rbacPolicyService = new RbacPolicyService();
  const idempotencyService = new IdempotencyService();

  // ---- Instantiate middleware ----
  const authMiddleware = new AuthMiddleware(authService);
  const rbacMiddleware = new RbacMiddleware(rbacService);
  const rateLimitMiddleware = new RateLimitMiddleware(rateLimiterService);

  // ---- Global middleware ----
  app.set('trust proxy', 1);
  app.use(securityHeadersMiddleware);
  app.use(
    cors({
      origin: config.cors.allowedOrigins,
      methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'],
      allowedHeaders: [
        'Authorization',
        'Content-Type',
        'X-Request-ID',
        'X-API-Key',
        'Idempotency-Key',
      ],
      exposedHeaders: [
        'X-Request-ID',
        'X-RateLimit-Limit',
        'X-RateLimit-Remaining',
        'X-RateLimit-Reset',
        'Retry-After',
        'ETag',
      ],
      credentials: true,
    }),
  );
  app.use(requestIdMiddleware);
  app.use(requestLoggerMiddleware);
  app.use(express.json({ limit: '1mb' }));
  app.use(express.urlencoded({ extended: true }));
  app.use(apiVersioningMiddleware);

  // ---- System routes (unauthenticated where noted) ----
  app.use(
    createSystemRouter(authMiddleware, rbacMiddleware),
  );

  // ---- Domain routes ----
  app.use(
    '/api/v1/auth',
    createAuthRouter(
      mfaOrchestrator,
      auditService,
      authMiddleware,
      rbacMiddleware,
      rateLimitMiddleware,
    ),
  );

  app.use(
    '/api/v1/users',
    createUsersRouter(authMiddleware, rbacMiddleware, rateLimitMiddleware, auditService),
  );

  app.use(
    '/api/v1/reports',
    createReportsRouter(authMiddleware, rbacMiddleware, rateLimitMiddleware, auditService),
  );

  app.use(
    '/api/v1/payments',
    createPaymentsRouter(
      authMiddleware,
      rbacMiddleware,
      rateLimitMiddleware,
      auditService,
      idempotencyService,
    ),
  );

  app.use(
    '/api/v1/notifications',
    createNotificationsRouter(authMiddleware, rbacMiddleware, rateLimitMiddleware),
  );

  app.use(
    '/api/v1/gateway',
    createGatewayAdminRouter(
      authMiddleware,
      rbacMiddleware,
      rateLimitMiddleware,
      routingService,
      rateLimitPolicyService,
      rbacPolicyService,
      auditService,
    ),
  );

  // ---- 404 handler ----
  app.use((_req, res) => {
    res.status(404).json({
      error: 'NOT_FOUND',
      message: 'The requested resource does not exist',
      statusCode: 404,
      timestamp: new Date().toISOString(),
    });
  });

  // ---- Global error handler ----
  app.use(errorHandlerMiddleware);

  return app;
}
