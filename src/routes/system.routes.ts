import { Router, Request, Response } from 'express';
import { upstreamClients } from '../infrastructure/http.client';
import { getRedisClient } from '../infrastructure/redis.client';
import { registry } from '../infrastructure/metrics';
import { config } from '../config';
import { HealthResponse, GatewayInfo, DependencyHealth } from '../types';
import { AuthMiddleware } from '../middleware/auth.middleware';
import { RbacMiddleware } from '../middleware/rbac.middleware';
import { logger } from '../infrastructure/logger';

export function createSystemRouter(
  authMiddleware: AuthMiddleware,
  rbacMiddleware: RbacMiddleware,
): Router {
  const router = Router();

  // GET /health — unauthenticated
  router.get('/health', async (_req: Request, res: Response) => {
    const dependencies: DependencyHealth[] = [];
    let overallStatus: 'healthy' | 'degraded' | 'unhealthy' = 'healthy';

    // Check Redis
    try {
      const start = Date.now();
      await getRedisClient().ping();
      dependencies.push({ name: 'redis', status: 'healthy', latencyMs: Date.now() - start });
    } catch (err) {
      dependencies.push({ name: 'redis', status: 'unhealthy', error: (err as Error).message });
      overallStatus = 'unhealthy';
    }

    // Check upstream services
    const upstreamChecks: Array<{ name: string; client: typeof upstreamClients.userProfile }> = [
      { name: 'user-profile-service', client: upstreamClients.userProfile },
      { name: 'mfa-service', client: upstreamClients.mfa },
      { name: 'payment-service', client: upstreamClients.payment },
      { name: 'reporting-service', client: upstreamClients.reporting },
      { name: 'notification-service', client: upstreamClients.notification },
    ];

    await Promise.allSettled(
      upstreamChecks.map(async ({ name, client }) => {
        const start = Date.now();
        try {
          await client.send('GET', '/health', {});
          dependencies.push({ name, status: 'healthy', latencyMs: Date.now() - start });
        } catch {
          dependencies.push({ name, status: 'degraded' });
          if (overallStatus === 'healthy') overallStatus = 'degraded';
        }
      }),
    );

    const body: HealthResponse = {
      status: overallStatus,
      version: config.service.version,
      timestamp: new Date().toISOString(),
      dependencies,
    };

    res.status(overallStatus === 'unhealthy' ? 503 : 200).json(body);
  });

  // GET /ready — unauthenticated
  router.get('/ready', async (_req: Request, res: Response) => {
    try {
      await getRedisClient().ping();
      res.status(200).json({ status: 'ready', timestamp: new Date().toISOString() });
    } catch (err) {
      logger.warn({ err }, 'Readiness check failed');
      res.status(503).json({ status: 'not_ready', timestamp: new Date().toISOString() });
    }
  });

  // GET /metrics — requires admin:metrics scope
  router.get(
    '/metrics',
    authMiddleware.authenticate(),
    rbacMiddleware.requireScopes('admin:metrics'),
    async (_req: Request, res: Response) => {
      res.set('Content-Type', registry.contentType);
      const metrics = await registry.metrics();
      res.send(metrics);
    },
  );

  // GET /api/v1/info — unauthenticated
  router.get('/api/v1/info', (_req: Request, res: Response) => {
    const info: GatewayInfo = {
      name: config.service.name,
      version: config.service.version,
      environment: config.env,
      supportedApiVersions: ['v1'],
      deprecatedApiVersions: [],
      documentationUrl: 'https://api.example.com/docs',
    };
    res.json(info);
  });

  return router;
}
