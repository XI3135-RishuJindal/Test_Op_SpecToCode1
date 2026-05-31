import { Router, Request, Response } from 'express';
import { z } from 'zod';
import { MfaOrchestrator } from '../services/mfa.orchestrator';
import { AuditService } from '../services/audit.service';
import { AuthMiddleware } from '../middleware/auth.middleware';
import { RbacMiddleware } from '../middleware/rbac.middleware';
import { RateLimitMiddleware } from '../middleware/rate-limit.middleware';
import { config } from '../config';

// ---- Validation schemas ----

const LoginSchema = z.object({
  username: z.string().min(1),
  password: z.string().min(1),
  deviceFingerprint: z.string().optional(),
});

const MfaVerifySchema = z.object({
  otpCode: z.string().min(4).max(8),
});

const TokenRefreshSchema = z.object({
  refreshToken: z.string().min(1),
});

const MfaEnrollSchema = z.object({
  method: z.enum(['totp', 'sms', 'email']),
  phoneNumber: z.string().optional(),
  email: z.string().email().optional(),
});

export function createAuthRouter(
  mfaOrchestrator: MfaOrchestrator,
  auditService: AuditService,
  authMiddleware: AuthMiddleware,
  rbacMiddleware: RbacMiddleware,
  rateLimitMiddleware: RateLimitMiddleware,
): Router {
  const router = Router();

  // POST /api/v1/auth/login
  router.post(
    '/login',
    rateLimitMiddleware.limit({
      ...config.rateLimits.authLogin,
      keyBy: 'ip',
      endpointLabel: 'auth:login',
    }),
    async (req: Request, res: Response) => {
      const body = LoginSchema.parse(req.body);

      const loginResponse = await mfaOrchestrator.login(body);

      await auditService.log({
        principal: body.username,
        action: 'AUTH_LOGIN_INITIATED',
        resource: '/api/v1/auth/login',
        status: 'success',
        correlationId: req.gateway.requestId,
        path: req.path,
        ipAddress: req.ip,
        userAgent: req.headers['user-agent'],
      });

      res.status(200).json(loginResponse);
    },
  );

  // POST /api/v1/auth/mfa/verify
  router.post(
    '/mfa/verify',
    rateLimitMiddleware.limit({
      ...config.rateLimits.authLogin,
      keyBy: 'ip',
      endpointLabel: 'auth:mfa:verify',
    }),
    authMiddleware.authenticateMfaSession(),
    async (req: Request, res: Response) => {
      const body = MfaVerifySchema.parse(req.body);
      const authContext = req.gateway.authContext!;
      const mfaSessionToken = req.headers['authorization']!.slice(7);

      const tokenResponse = await mfaOrchestrator.verifyMfa(
        mfaSessionToken,
        authContext.userId,
        body,
      );

      await auditService.log({
        principal: authContext.userId,
        action: 'AUTH_MFA_VERIFIED',
        resource: '/api/v1/auth/mfa/verify',
        status: 'success',
        correlationId: req.gateway.requestId,
        path: req.path,
        ipAddress: req.ip,
        userAgent: req.headers['user-agent'],
      });

      res.status(200).json(tokenResponse);
    },
  );

  // POST /api/v1/auth/token/refresh
  router.post('/token/refresh', async (req: Request, res: Response) => {
    const body = TokenRefreshSchema.parse(req.body);
    const tokenResponse = await mfaOrchestrator.refreshToken(body);
    res.status(200).json(tokenResponse);
  });

  // POST /api/v1/auth/logout
  router.post(
    '/logout',
    authMiddleware.authenticate(),
    async (req: Request, res: Response) => {
      const authHeader = req.headers['authorization']!;
      const accessToken = authHeader.slice(7);
      const refreshToken = req.body?.refreshToken;

      await mfaOrchestrator.logout(accessToken, refreshToken);

      await auditService.log({
        principal: req.gateway.authContext!.userId,
        action: 'AUTH_LOGOUT',
        resource: '/api/v1/auth/logout',
        status: 'success',
        correlationId: req.gateway.requestId,
        path: req.path,
        ipAddress: req.ip,
      });

      res.status(204).send();
    },
  );

  // POST /api/v1/auth/mfa/enroll
  router.post(
    '/mfa/enroll',
    authMiddleware.authenticate(),
    rbacMiddleware.requireScopes('mfa:enroll'),
    async (req: Request, res: Response) => {
      const body = MfaEnrollSchema.parse(req.body);
      const authContext = req.gateway.authContext!;
      const authHeader = req.headers['authorization']!;

      const enrollResponse = await mfaOrchestrator.enrollMfa(
        authContext.userId,
        body,
        authHeader,
      );

      await auditService.log({
        principal: authContext.userId,
        action: 'MFA_ENROLLED',
        resource: '/api/v1/auth/mfa/enroll',
        status: 'success',
        correlationId: req.gateway.requestId,
        path: req.path,
        metadata: { method: body.method },
      });

      res.status(201).json(enrollResponse);
    },
  );

  // DELETE /api/v1/auth/mfa/enroll/:methodId
  router.delete(
    '/mfa/enroll/:methodId',
    authMiddleware.authenticate(),
    rbacMiddleware.requireScopes('mfa:enroll'),
    async (req: Request, res: Response) => {
      const { methodId } = req.params;
      const authContext = req.gateway.authContext!;
      const authHeader = req.headers['authorization']!;

      await mfaOrchestrator.deEnrollMfa(authContext.userId, methodId, authHeader);

      await auditService.log({
        principal: authContext.userId,
        action: 'MFA_DEENROLLED',
        resource: `/api/v1/auth/mfa/enroll/${methodId}`,
        status: 'success',
        correlationId: req.gateway.requestId,
        path: req.path,
        metadata: { methodId },
      });

      res.status(204).send();
    },
  );

  return router;
}
