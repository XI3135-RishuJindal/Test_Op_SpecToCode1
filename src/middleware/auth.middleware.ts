import { Request, Response, NextFunction } from 'express';
import { AuthService } from '../services/auth.service';
import { createErrorResponse } from '../utils/errors';

export class AuthMiddleware {
  constructor(private readonly authService: AuthService) {}

  /**
   * Validates the Bearer JWT in Authorization header.
   * Attaches AuthContext to req.gateway.authContext.
   */
  authenticate() {
    return async (req: Request, res: Response, next: NextFunction): Promise<void> => {
      try {
        const authHeader = req.headers['authorization'];
        const apiKey = req.headers['x-api-key'] as string | undefined;

        if (!authHeader && !apiKey) {
          res.status(401).json(
            createErrorResponse('UNAUTHORIZED', 'Missing authorization credentials', 401, req),
          );
          return;
        }

        let authContext;

        if (authHeader) {
          if (!authHeader.startsWith('Bearer ')) {
            res.status(401).json(
              createErrorResponse('UNAUTHORIZED', 'Invalid authorization format — expected Bearer token', 401, req),
            );
            return;
          }
          const token = authHeader.slice(7);
          authContext = await this.authService.verifyJwt(token);
        } else if (apiKey) {
          authContext = await this.authService.verifyApiKey(apiKey);
        }

        if (!authContext) {
          res.status(401).json(
            createErrorResponse('UNAUTHORIZED', 'Invalid or expired token', 401, req),
          );
          return;
        }

        req.gateway.authContext = authContext;
        next();
      } catch (err) {
        res.status(401).json(
          createErrorResponse('UNAUTHORIZED', 'Token validation failed', 401, req),
        );
      }
    };
  }

  /**
   * Validates an MFA session token (opaque token from Redis).
   */
  authenticateMfaSession() {
    return async (req: Request, res: Response, next: NextFunction): Promise<void> => {
      try {
        const authHeader = req.headers['authorization'];
        if (!authHeader?.startsWith('Bearer ')) {
          res.status(401).json(
            createErrorResponse('UNAUTHORIZED', 'Missing MFA session token', 401, req),
          );
          return;
        }

        const mfaSessionToken = authHeader.slice(7);
        const session = await this.authService.validateMfaSession(mfaSessionToken);

        if (!session) {
          res.status(401).json(
            createErrorResponse('UNAUTHORIZED', 'Invalid or expired MFA session token', 401, req),
          );
          return;
        }

        // Attach minimal context for MFA verify step
        req.gateway.authContext = {
          userId: session.userId,
          email: session.email,
          roles: [],
          scopes: [],
          mfaSatisfied: false,
          sub: session.userId,
          iss: '',
          aud: '',
          exp: 0,
          iat: 0,
        };
        next();
      } catch {
        res.status(401).json(
          createErrorResponse('UNAUTHORIZED', 'MFA session validation failed', 401, req),
        );
      }
    };
  }
}
