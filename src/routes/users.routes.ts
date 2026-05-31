import { Router, Request, Response } from 'express';
import { z } from 'zod';
import { upstreamClients } from '../infrastructure/http.client';
import { AuthMiddleware } from '../middleware/auth.middleware';
import { RbacMiddleware } from '../middleware/rbac.middleware';
import { RateLimitMiddleware } from '../middleware/rate-limit.middleware';
import { AuditService } from '../services/audit.service';
import { config } from '../config';
import { parsePagination } from '../utils/pagination';

const CreateUserSchema = z.object({
  email: z.string().email(),
  firstName: z.string().min(1),
  lastName: z.string().min(1),
  phoneNumber: z.string().optional(),
  privacySettings: z.object({
    shareEmail: z.boolean(),
    sharePhone: z.boolean(),
  }).optional(),
});

const UpdateUserSchema = z.object({
  firstName: z.string().min(1).optional(),
  lastName: z.string().min(1).optional(),
  phoneNumber: z.string().optional(),
  privacySettings: z.object({
    shareEmail: z.boolean(),
    sharePhone: z.boolean(),
  }).optional(),
});

export function createUsersRouter(
  authMiddleware: AuthMiddleware,
  rbacMiddleware: RbacMiddleware,
  rateLimitMiddleware: RateLimitMiddleware,
  auditService: AuditService,
): Router {
  const router = Router();

  const authenticate = authMiddleware.authenticate();
  const defaultRateLimit = rateLimitMiddleware.limit({
    ...config.rateLimits.general,
    keyBy: 'userId',
    endpointLabel: 'users',
  });

  function buildUpstreamHeaders(req: Request): Record<string, string> {
    return {
      'Authorization': req.headers['authorization'] ?? '',
      'X-Request-ID': req.gateway.requestId,
      'X-User-ID': req.gateway.authContext?.userId ?? '',
      'Content-Type': 'application/json',
    };
  }

  // POST /api/v1/users
  router.post(
    '/',
    authenticate,
    rbacMiddleware.requireScopes('users:write'),
    defaultRateLimit,
    async (req: Request, res: Response) => {
      const body = CreateUserSchema.parse(req.body);
      const headers = buildUpstreamHeaders(req);

      const upstream = await upstreamClients.userProfile.send(
        'POST', '/v1/users', { body, headers },
      );

      await auditService.log({
        principal: req.gateway.authContext!.userId,
        action: 'USER_CREATED',
        resource: '/api/v1/users',
        status: 'success',
        correlationId: req.gateway.requestId,
        path: req.path,
        statusCode: upstream.status,
      });

      res.status(upstream.status).json(upstream.data);
    },
  );

  // GET /api/v1/users
  router.get(
    '/',
    authenticate,
    rbacMiddleware.requireScopes('users:read'),
    defaultRateLimit,
    async (req: Request, res: Response) => {
      const { page, limit } = parsePagination(req);
      const headers = buildUpstreamHeaders(req);

      const upstream = await upstreamClients.userProfile.send(
        'GET', '/v1/users', { headers, params: { page: String(page), limit: String(limit) } },
      );

      res.status(upstream.status).json(upstream.data);
    },
  );

  // GET /api/v1/users/:userId
  router.get(
    '/:userId',
    authenticate,
    rbacMiddleware.requireScopes('users:read'),
    defaultRateLimit,
    async (req: Request, res: Response) => {
      const { userId } = req.params;
      const headers = buildUpstreamHeaders(req);

      const upstream = await upstreamClients.userProfile.send(
        'GET', `/v1/users/${userId}`, { headers },
      );

      if (upstream.status === 200) {
        res.setHeader('ETag', `"${userId}-${Date.now()}"`);
        res.setHeader('Cache-Control', 'private, max-age=60');
      }

      res.status(upstream.status).json(upstream.data);
    },
  );

  // PUT /api/v1/users/:userId
  router.put(
    '/:userId',
    authenticate,
    rbacMiddleware.requireScopes('users:write'),
    defaultRateLimit,
    async (req: Request, res: Response) => {
      const { userId } = req.params;
      const body = UpdateUserSchema.parse(req.body);
      const headers = buildUpstreamHeaders(req);

      const upstream = await upstreamClients.userProfile.send(
        'PUT', `/v1/users/${userId}`, { body, headers },
      );

      await auditService.log({
        principal: req.gateway.authContext!.userId,
        action: 'USER_UPDATED',
        resource: `/api/v1/users/${userId}`,
        status: 'success',
        correlationId: req.gateway.requestId,
        path: req.path,
        statusCode: upstream.status,
      });

      res.status(upstream.status).json(upstream.data);
    },
  );

  // DELETE /api/v1/users/:userId
  router.delete(
    '/:userId',
    authenticate,
    rbacMiddleware.requireScopes('users:delete'),
    defaultRateLimit,
    async (req: Request, res: Response) => {
      const { userId } = req.params;
      const headers = buildUpstreamHeaders(req);

      const upstream = await upstreamClients.userProfile.send(
        'DELETE', `/v1/users/${userId}`, { headers },
      );

      await auditService.log({
        principal: req.gateway.authContext!.userId,
        action: 'USER_DELETED',
        resource: `/api/v1/users/${userId}`,
        status: 'success',
        correlationId: req.gateway.requestId,
        path: req.path,
        statusCode: upstream.status,
      });

      res.status(upstream.status).send();
    },
  );

  return router;
}
