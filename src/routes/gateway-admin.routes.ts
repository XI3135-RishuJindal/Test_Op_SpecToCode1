import { Router, Request, Response } from 'express';
import { z } from 'zod';
import { AuthMiddleware } from '../middleware/auth.middleware';
import { RbacMiddleware } from '../middleware/rbac.middleware';
import { RateLimitMiddleware } from '../middleware/rate-limit.middleware';
import { RoutingService } from '../services/routing.service';
import { RateLimitPolicyService } from '../services/rate-limit-policy.service';
import { RbacPolicyService } from '../services/rbac-policy.service';
import { AuditService } from '../services/audit.service';
import { config } from '../config';

const CreateRouteSchema = z.object({
  pathPattern: z.string().min(1),
  method: z.union([z.string(), z.array(z.string())]),
  upstreamUrl: z.string().url(),
  authRequired: z.boolean().optional().default(true),
  requiredScopes: z.array(z.string()).optional(),
  stripPrefix: z.string().optional(),
  addPrefix: z.string().optional(),
});

const UpdateRouteSchema = CreateRouteSchema.partial();

const CreateRateLimitSchema = z.object({
  name: z.string().min(1),
  pathPattern: z.string().min(1),
  windowMs: z.number().positive(),
  maxRequests: z.number().positive(),
  keyBy: z.enum(['ip', 'userId', 'apiKey']),
  burstAllowance: z.number().optional(),
});

const CreateRbacPolicySchema = z.object({
  name: z.string().min(1),
  roles: z.array(z.string()).min(1),
  resource: z.string().min(1),
  actions: z.array(z.string()).min(1),
  effect: z.enum(['allow', 'deny']),
  conditions: z.record(z.unknown()).optional(),
});

export function createGatewayAdminRouter(
  authMiddleware: AuthMiddleware,
  rbacMiddleware: RbacMiddleware,
  rateLimitMiddleware: RateLimitMiddleware,
  routingService: RoutingService,
  rateLimitPolicyService: RateLimitPolicyService,
  rbacPolicyService: RbacPolicyService,
  auditService: AuditService,
): Router {
  const router = Router();

  const authenticate = authMiddleware.authenticate();
  const adminRateLimit = rateLimitMiddleware.limit({
    ...config.rateLimits.admin,
    keyBy: 'userId',
    endpointLabel: 'admin',
  });

  // ---- Routes management ----

  // GET /api/v1/gateway/routes
  router.get(
    '/routes',
    authenticate,
    rbacMiddleware.requireScopes('admin:gateway'),
    adminRateLimit,
    async (_req: Request, res: Response) => {
      const routes = await routingService.findAll();
      res.json({ data: routes });
    },
  );

  // POST /api/v1/gateway/routes
  router.post(
    '/routes',
    authenticate,
    rbacMiddleware.requireScopes('admin:gateway'),
    adminRateLimit,
    async (req: Request, res: Response) => {
      const body = CreateRouteSchema.parse(req.body);
      const route = await routingService.create(body);

      await auditService.log({
        principal: req.gateway.authContext!.userId,
        action: 'GATEWAY_ROUTE_CREATED',
        resource: '/api/v1/gateway/routes',
        status: 'success',
        correlationId: req.gateway.requestId,
        path: req.path,
        metadata: { routeId: route.routeId, pathPattern: route.pathPattern },
      });

      res.status(201).json(route);
    },
  );

  // PUT /api/v1/gateway/routes/:routeId
  router.put(
    '/routes/:routeId',
    authenticate,
    rbacMiddleware.requireScopes('admin:gateway'),
    adminRateLimit,
    async (req: Request, res: Response) => {
      const { routeId } = req.params;
      const body = UpdateRouteSchema.parse(req.body);
      const route = await routingService.update(routeId, body);

      if (!route) {
        res.status(404).json({ error: 'NOT_FOUND', message: 'Route not found', statusCode: 404 });
        return;
      }

      await auditService.log({
        principal: req.gateway.authContext!.userId,
        action: 'GATEWAY_ROUTE_UPDATED',
        resource: `/api/v1/gateway/routes/${routeId}`,
        status: 'success',
        correlationId: req.gateway.requestId,
        path: req.path,
        metadata: { routeId },
      });

      res.json(route);
    },
  );

  // DELETE /api/v1/gateway/routes/:routeId
  router.delete(
    '/routes/:routeId',
    authenticate,
    rbacMiddleware.requireScopes('admin:gateway'),
    adminRateLimit,
    async (req: Request, res: Response) => {
      const { routeId } = req.params;
      const deleted = await routingService.delete(routeId);

      if (!deleted) {
        res.status(404).json({ error: 'NOT_FOUND', message: 'Route not found', statusCode: 404 });
        return;
      }

      await auditService.log({
        principal: req.gateway.authContext!.userId,
        action: 'GATEWAY_ROUTE_DELETED',
        resource: `/api/v1/gateway/routes/${routeId}`,
        status: 'success',
        correlationId: req.gateway.requestId,
        path: req.path,
        metadata: { routeId },
      });

      res.status(204).send();
    },
  );

  // ---- Rate limit policies ----

  // GET /api/v1/gateway/rate-limits
  router.get(
    '/rate-limits',
    authenticate,
    rbacMiddleware.requireScopes('admin:gateway'),
    adminRateLimit,
    async (_req: Request, res: Response) => {
      const policies = await rateLimitPolicyService.findAll();
      res.json({ data: policies });
    },
  );

  // POST /api/v1/gateway/rate-limits
  router.post(
    '/rate-limits',
    authenticate,
    rbacMiddleware.requireScopes('admin:gateway'),
    adminRateLimit,
    async (req: Request, res: Response) => {
      const body = CreateRateLimitSchema.parse(req.body);
      const policy = await rateLimitPolicyService.create(body);

      await auditService.log({
        principal: req.gateway.authContext!.userId,
        action: 'RATE_LIMIT_POLICY_CREATED',
        resource: '/api/v1/gateway/rate-limits',
        status: 'success',
        correlationId: req.gateway.requestId,
        path: req.path,
        metadata: { policyId: policy.policyId, name: policy.name },
      });

      res.status(201).json(policy);
    },
  );

  // ---- RBAC policies ----

  // GET /api/v1/gateway/rbac/policies
  router.get(
    '/rbac/policies',
    authenticate,
    rbacMiddleware.requireScopes('admin:rbac'),
    adminRateLimit,
    async (_req: Request, res: Response) => {
      const policies = await rbacPolicyService.findAll();
      res.json({ data: policies });
    },
  );

  // POST /api/v1/gateway/rbac/policies
  router.post(
    '/rbac/policies',
    authenticate,
    rbacMiddleware.requireScopes('admin:rbac'),
    adminRateLimit,
    async (req: Request, res: Response) => {
      const body = CreateRbacPolicySchema.parse(req.body);
      const policy = await rbacPolicyService.create(body);

      await auditService.log({
        principal: req.gateway.authContext!.userId,
        action: 'RBAC_POLICY_CREATED',
        resource: '/api/v1/gateway/rbac/policies',
        status: 'success',
        correlationId: req.gateway.requestId,
        path: req.path,
        metadata: { policyId: policy.policyId, name: policy.name },
      });

      res.status(201).json(policy);
    },
  );

  // ---- Audit logs ----

  // GET /api/v1/gateway/audit-logs
  router.get(
    '/audit-logs',
    authenticate,
    rbacMiddleware.requireScopes('admin:audit'),
    adminRateLimit,
    async (req: Request, res: Response) => {
      const page = parseInt(String(req.query['page'] ?? '1'), 10);
      const limit = Math.min(100, parseInt(String(req.query['limit'] ?? '20'), 10));

      const result = await auditService.queryLogs({
        principal: req.query['principal'] as string | undefined,
        statusCode: req.query['statusCode'] ? parseInt(String(req.query['statusCode']), 10) : undefined,
        path: req.query['path'] as string | undefined,
        from: req.query['from'] as string | undefined,
        to: req.query['to'] as string | undefined,
        page,
        limit,
      });

      res.json(result);
    },
  );

  return router;
}
