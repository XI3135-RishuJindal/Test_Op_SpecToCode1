import { Router, Request, Response } from 'express';
import { z } from 'zod';
import { upstreamClients } from '../infrastructure/http.client';
import { AuthMiddleware } from '../middleware/auth.middleware';
import { RbacMiddleware } from '../middleware/rbac.middleware';
import { RateLimitMiddleware } from '../middleware/rate-limit.middleware';
import { AuditService } from '../services/audit.service';
import { config } from '../config';
import { parsePagination } from '../utils/pagination';

const CreateReportSchema = z.object({
  name: z.string().min(1),
  type: z.string().min(1),
  format: z.enum(['pdf', 'csv']),
  parameters: z.record(z.unknown()).optional(),
});

const UpdateReportSchema = z.object({
  name: z.string().min(1).optional(),
  parameters: z.record(z.unknown()).optional(),
});

const ReportScheduleSchema = z.object({
  cronExpression: z.string().min(1),
  timezone: z.string().optional(),
  enabled: z.boolean(),
});

export function createReportsRouter(
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
    endpointLabel: 'reports',
  });

  function buildUpstreamHeaders(req: Request): Record<string, string> {
    return {
      'Authorization': req.headers['authorization'] ?? '',
      'X-Request-ID': req.gateway.requestId,
      'X-User-ID': req.gateway.authContext?.userId ?? '',
      'Content-Type': 'application/json',
    };
  }

  // POST /api/v1/reports
  router.post(
    '/',
    authenticate,
    rbacMiddleware.requireScopes('reports:write'),
    defaultRateLimit,
    async (req: Request, res: Response) => {
      const body = CreateReportSchema.parse(req.body);
      const headers = buildUpstreamHeaders(req);

      const upstream = await upstreamClients.reporting.send(
        'POST', '/v1/reports', { body, headers },
      );

      await auditService.log({
        principal: req.gateway.authContext!.userId,
        action: 'REPORT_CREATED',
        resource: '/api/v1/reports',
        status: 'success',
        correlationId: req.gateway.requestId,
        path: req.path,
        statusCode: upstream.status,
      });

      res.status(upstream.status).json(upstream.data);
    },
  );

  // GET /api/v1/reports
  router.get(
    '/',
    authenticate,
    rbacMiddleware.requireScopes('reports:read'),
    defaultRateLimit,
    async (req: Request, res: Response) => {
      const { page, limit } = parsePagination(req);
      const headers = buildUpstreamHeaders(req);

      const upstream = await upstreamClients.reporting.send(
        'GET', '/v1/reports', { headers, params: { page: String(page), limit: String(limit) } },
      );

      res.status(upstream.status).json(upstream.data);
    },
  );

  // GET /api/v1/reports/:reportId
  router.get(
    '/:reportId',
    authenticate,
    rbacMiddleware.requireScopes('reports:read'),
    defaultRateLimit,
    async (req: Request, res: Response) => {
      const { reportId } = req.params;
      const headers = buildUpstreamHeaders(req);

      const upstream = await upstreamClients.reporting.send(
        'GET', `/v1/reports/${reportId}`, { headers },
      );

      res.status(upstream.status).json(upstream.data);
    },
  );

  // PUT /api/v1/reports/:reportId
  router.put(
    '/:reportId',
    authenticate,
    rbacMiddleware.requireScopes('reports:write'),
    defaultRateLimit,
    async (req: Request, res: Response) => {
      const { reportId } = req.params;
      const body = UpdateReportSchema.parse(req.body);
      const headers = buildUpstreamHeaders(req);

      const upstream = await upstreamClients.reporting.send(
        'PUT', `/v1/reports/${reportId}`, { body, headers },
      );

      res.status(upstream.status).json(upstream.data);
    },
  );

  // PUT /api/v1/reports/:reportId/schedule
  router.put(
    '/:reportId/schedule',
    authenticate,
    rbacMiddleware.requireScopes('reports:write'),
    defaultRateLimit,
    async (req: Request, res: Response) => {
      const { reportId } = req.params;
      const body = ReportScheduleSchema.parse(req.body);
      const headers = buildUpstreamHeaders(req);

      const upstream = await upstreamClients.reporting.send(
        'PUT', `/v1/reports/${reportId}/schedule`, { body, headers },
      );

      res.status(upstream.status).json(upstream.data);
    },
  );

  // GET /api/v1/reports/:reportId/download
  router.get(
    '/:reportId/download',
    authenticate,
    rbacMiddleware.requireScopes('reports:read'),
    defaultRateLimit,
    async (req: Request, res: Response) => {
      const { reportId } = req.params;
      const headers = buildUpstreamHeaders(req);

      const upstream = await upstreamClients.reporting.send<Buffer>(
        'GET', `/v1/reports/${reportId}/download`, { headers },
      );

      // Forward content-type and disposition headers from upstream
      const contentType = upstream.headers['content-type'] as string ?? 'application/octet-stream';
      const contentDisposition = upstream.headers['content-disposition'] as string;

      res.setHeader('Content-Type', contentType);
      if (contentDisposition) res.setHeader('Content-Disposition', contentDisposition);

      res.status(upstream.status).send(upstream.data);
    },
  );

  return router;
}
