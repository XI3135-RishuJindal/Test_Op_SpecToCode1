import { Router, Request, Response } from 'express';
import { z } from 'zod';
import { upstreamClients } from '../infrastructure/http.client';
import { AuthMiddleware } from '../middleware/auth.middleware';
import { RbacMiddleware } from '../middleware/rbac.middleware';
import { RateLimitMiddleware } from '../middleware/rate-limit.middleware';
import { config } from '../config';
import { parsePagination } from '../utils/pagination';

const NotificationPreferencesSchema = z.object({
  channels: z.array(z.enum(['email', 'sms', 'push', 'in_app'])),
  types: z.array(z.enum(['info', 'warning', 'error', 'success'])),
});

export function createNotificationsRouter(
  authMiddleware: AuthMiddleware,
  rbacMiddleware: RbacMiddleware,
  rateLimitMiddleware: RateLimitMiddleware,
): Router {
  const router = Router();

  const authenticate = authMiddleware.authenticate();
  const defaultRateLimit = rateLimitMiddleware.limit({
    ...config.rateLimits.general,
    keyBy: 'userId',
    endpointLabel: 'notifications',
  });

  function buildUpstreamHeaders(req: Request): Record<string, string> {
    return {
      'Authorization': req.headers['authorization'] ?? '',
      'X-Request-ID': req.gateway.requestId,
      'X-User-ID': req.gateway.authContext?.userId ?? '',
      'Content-Type': 'application/json',
    };
  }

  // GET /api/v1/notifications
  router.get(
    '/',
    authenticate,
    defaultRateLimit,
    async (req: Request, res: Response) => {
      const { page, limit } = parsePagination(req);
      const headers = buildUpstreamHeaders(req);

      const params: Record<string, string> = {
        page: String(page),
        limit: String(limit),
        userId: req.gateway.authContext!.userId, // user-scoped
      };
      if (req.query['read'] !== undefined) params['read'] = String(req.query['read']);
      if (req.query['type']) params['type'] = String(req.query['type']);

      const upstream = await upstreamClients.notification.send(
        'GET', '/v1/notifications', { headers, params },
      );

      res.status(upstream.status).json(upstream.data);
    },
  );

  // PUT /api/v1/notifications/:notificationId/read
  router.put(
    '/:notificationId/read',
    authenticate,
    defaultRateLimit,
    async (req: Request, res: Response) => {
      const { notificationId } = req.params;
      const headers = buildUpstreamHeaders(req);

      const upstream = await upstreamClients.notification.send(
        'PUT',
        `/v1/notifications/${notificationId}/read`,
        { headers, body: { userId: req.gateway.authContext!.userId } },
      );

      res.status(upstream.status).json(upstream.data);
    },
  );

  // GET /api/v1/notifications/preferences
  router.get(
    '/preferences',
    authenticate,
    defaultRateLimit,
    async (req: Request, res: Response) => {
      const headers = buildUpstreamHeaders(req);

      const upstream = await upstreamClients.notification.send(
        'GET',
        `/v1/notifications/preferences?userId=${req.gateway.authContext!.userId}`,
        { headers },
      );

      res.status(upstream.status).json(upstream.data);
    },
  );

  // PUT /api/v1/notifications/preferences
  router.put(
    '/preferences',
    authenticate,
    defaultRateLimit,
    async (req: Request, res: Response) => {
      const body = NotificationPreferencesSchema.parse(req.body);
      const headers = buildUpstreamHeaders(req);

      const upstream = await upstreamClients.notification.send(
        'PUT',
        '/v1/notifications/preferences',
        {
          headers,
          body: { ...body, userId: req.gateway.authContext!.userId },
        },
      );

      res.status(upstream.status).json(upstream.data);
    },
  );

  return router;
}
