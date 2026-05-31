import { Request, Response, NextFunction } from 'express';
import { RbacService } from '../services/rbac.service';
import { createErrorResponse } from '../utils/errors';

export class RbacMiddleware {
  constructor(private readonly rbacService: RbacService) {}

  /**
   * Checks that the authenticated principal has at least one of the required scopes.
   */
  requireScopes(...requiredScopes: string[]) {
    return async (req: Request, res: Response, next: NextFunction): Promise<void> => {
      const authContext = req.gateway.authContext;

      if (!authContext) {
        res.status(401).json(
          createErrorResponse('UNAUTHORIZED', 'Not authenticated', 401, req),
        );
        return;
      }

      const decision = await this.rbacService.evaluate({
        principal: {
          userId: authContext.userId,
          roles: authContext.roles,
          scopes: authContext.scopes,
        },
        resource: req.path,
        action: req.method,
        requiredScopes,
      });

      if (!decision.allow) {
        res.status(403).json(
          createErrorResponse(
            'FORBIDDEN',
            decision.reason ?? 'Insufficient permissions',
            403,
            req,
          ),
        );
        return;
      }

      next();
    };
  }

  /**
   * Checks that the principal has at least one of the given roles.
   */
  requireRoles(...roles: string[]) {
    return (req: Request, res: Response, next: NextFunction): void => {
      const authContext = req.gateway.authContext;

      if (!authContext) {
        res.status(401).json(
          createErrorResponse('UNAUTHORIZED', 'Not authenticated', 401, req),
        );
        return;
      }

      const hasRole = roles.some((r) => authContext.roles.includes(r));
      if (!hasRole) {
        res.status(403).json(
          createErrorResponse('FORBIDDEN', 'Insufficient role', 403, req),
        );
        return;
      }

      next();
    };
  }
}
