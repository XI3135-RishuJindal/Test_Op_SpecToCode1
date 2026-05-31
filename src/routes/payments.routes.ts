import { Router, Request, Response } from 'express';
import { z } from 'zod';
import { upstreamClients } from '../infrastructure/http.client';
import { AuthMiddleware } from '../middleware/auth.middleware';
import { RbacMiddleware } from '../middleware/rbac.middleware';
import { RateLimitMiddleware } from '../middleware/rate-limit.middleware';
import { AuditService } from '../services/audit.service';
import { IdempotencyService } from '../services/idempotency.service';
import { config } from '../config';
import { parsePagination } from '../utils/pagination';
import { createErrorResponse } from '../utils/errors';

// PCI-DSS: tokenized payment methods only — no raw card data
const PaymentMethodSchema = z.object({
  tokenId: z.string().min(1),
  type: z.enum(['card', 'bank_transfer', 'wallet']),
});

const CreatePaymentSchema = z.object({
  amount: z.number().positive(),
  currency: z.string().length(3),
  paymentMethod: PaymentMethodSchema,
  description: z.string().optional(),
  metadata: z.record(z.unknown()).optional(),
});

const RefundSchema = z.object({
  amount: z.number().positive().optional(),
  reason: z.string().optional(),
});

export function createPaymentsRouter(
  authMiddleware: AuthMiddleware,
  rbacMiddleware: RbacMiddleware,
  rateLimitMiddleware: RateLimitMiddleware,
  auditService: AuditService,
  idempotencyService: IdempotencyService,
): Router {
  const router = Router();

  const authenticate = authMiddleware.authenticate();
  const paymentRateLimit = rateLimitMiddleware.limit({
    ...config.rateLimits.payments,
    keyBy: 'userId',
    endpointLabel: 'payments',
  });

  function buildUpstreamHeaders(req: Request): Record<string, string> {
    return {
      'Authorization': req.headers['authorization'] ?? '',
      'X-Request-ID': req.gateway.requestId,
      'X-User-ID': req.gateway.authContext?.userId ?? '',
      'Content-Type': 'application/json',
    };
  }

  // POST /api/v1/payments
  router.post(
    '/',
    authenticate,
    rbacMiddleware.requireScopes('payments:write'),
    paymentRateLimit,
    async (req: Request, res: Response) => {
      const body = CreatePaymentSchema.parse(req.body);
      const idempotencyKey = req.headers['idempotency-key'] as string | undefined;

      // Idempotency check
      if (idempotencyKey) {
        const requestHash = idempotencyService.hashRequest(body);
        const existing = await idempotencyService.check(idempotencyKey, requestHash);

        if (existing.exists) {
          if (existing.conflict) {
            res.status(409).json(
              createErrorResponse('DUPLICATE_IDEMPOTENCY_KEY', 'Idempotency key conflict — payload differs', 409, req),
            );
            return;
          }
          // Return cached response
          res.status(existing.record.statusCode).json(existing.record.response);
          return;
        }
      }

      const headers = buildUpstreamHeaders(req);
      if (idempotencyKey) headers['Idempotency-Key'] = idempotencyKey;

      const upstream = await upstreamClients.payment.send(
        'POST', '/v1/payments', { body, headers },
      );

      // Store idempotency result
      if (idempotencyKey) {
        const requestHash = idempotencyService.hashRequest(body);
        await idempotencyService.store(idempotencyKey, requestHash, upstream.data, upstream.status);
      }

      await auditService.log({
        principal: req.gateway.authContext!.userId,
        action: 'PAYMENT_INITIATED',
        resource: '/api/v1/payments',
        status: upstream.status < 400 ? 'success' : 'failure',
        correlationId: req.gateway.requestId,
        path: req.path,
        statusCode: upstream.status,
        metadata: { currency: body.currency, amount: body.amount },
      });

      res.status(upstream.status).json(upstream.data);
    },
  );

  // GET /api/v1/payments
  router.get(
    '/',
    authenticate,
    rbacMiddleware.requireScopes('payments:read'),
    paymentRateLimit,
    async (req: Request, res: Response) => {
      const { page, limit } = parsePagination(req);
      const headers = buildUpstreamHeaders(req);

      const params: Record<string, string> = {
        page: String(page),
        limit: String(limit),
      };
      if (req.query['status']) params['status'] = String(req.query['status']);
      if (req.query['currency']) params['currency'] = String(req.query['currency']);
      if (req.query['from']) params['from'] = String(req.query['from']);
      if (req.query['to']) params['to'] = String(req.query['to']);

      const upstream = await upstreamClients.payment.send(
        'GET', '/v1/payments', { headers, params },
      );

      res.status(upstream.status).json(upstream.data);
    },
  );

  // GET /api/v1/payments/:paymentId
  router.get(
    '/:paymentId',
    authenticate,
    rbacMiddleware.requireScopes('payments:read'),
    paymentRateLimit,
    async (req: Request, res: Response) => {
      const { paymentId } = req.params;
      const headers = buildUpstreamHeaders(req);

      const upstream = await upstreamClients.payment.send(
        'GET', `/v1/payments/${paymentId}`, { headers },
      );

      res.status(upstream.status).json(upstream.data);
    },
  );

  // POST /api/v1/payments/:paymentId/refund
  router.post(
    '/:paymentId/refund',
    authenticate,
    rbacMiddleware.requireScopes('payments:refund'),
    paymentRateLimit,
    async (req: Request, res: Response) => {
      const { paymentId } = req.params;
      const body = RefundSchema.parse(req.body);
      const headers = buildUpstreamHeaders(req);

      const upstream = await upstreamClients.payment.send(
        'POST', `/v1/payments/${paymentId}/refund`, { body, headers },
      );

      await auditService.log({
        principal: req.gateway.authContext!.userId,
        action: 'PAYMENT_REFUND_INITIATED',
        resource: `/api/v1/payments/${paymentId}/refund`,
        status: upstream.status < 400 ? 'success' : 'failure',
        correlationId: req.gateway.requestId,
        path: req.path,
        statusCode: upstream.status,
        metadata: { paymentId, amount: body.amount },
      });

      res.status(upstream.status).json(upstream.data);
    },
  );

  return router;
}
