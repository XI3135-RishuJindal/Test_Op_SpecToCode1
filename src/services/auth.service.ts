import jwt from 'jsonwebtoken';
import jwksClient, { JwksClient } from 'jwks-rsa';
import { v4 as uuidv4 } from 'uuid';
import { getRedisClient } from '../infrastructure/redis.client';
import { config } from '../config';
import { logger } from '../infrastructure/logger';
import { AuthContext } from '../types';
import { authFailures } from '../infrastructure/metrics';

interface MfaSession {
  userId: string;
  email: string;
  mfaMethod: string;
  maskedDestination: string;
}

export class AuthService {
  private readonly jwksClient: JwksClient;

  constructor() {
    this.jwksClient = jwksClient({
      jwksUri: config.jwt.jwksUri,
      cache: true,
      cacheMaxAge: config.jwt.jwksCacheTtl,
      rateLimit: true,
      jwksRequestsPerMinute: 10,
    });
  }

  async verifyJwt(token: string): Promise<AuthContext | null> {
    try {
      const decoded = jwt.decode(token, { complete: true });
      if (!decoded || typeof decoded === 'string') {
        authFailures.inc({ reason: 'decode_failed' });
        return null;
      }

      const kid = decoded.header.kid;
      const signingKey = await this.getSigningKey(kid);

      const payload = jwt.verify(token, signingKey, {
        issuer: config.jwt.issuer,
        audience: config.jwt.audience,
        algorithms: ['RS256'],
      }) as jwt.JwtPayload;

      // Check if token is revoked (blacklisted in Redis)
      const isRevoked = await this.isTokenRevoked(token);
      if (isRevoked) {
        authFailures.inc({ reason: 'token_revoked' });
        return null;
      }

      const scopes: string[] = typeof payload['scope'] === 'string'
        ? payload['scope'].split(' ')
        : Array.isArray(payload['scope']) ? payload['scope'] : [];

      const roles: string[] = Array.isArray(payload['roles'])
        ? payload['roles']
        : (payload['realm_access']?.roles ?? []);

      return {
        userId: payload['sub'] ?? payload['userId'],
        email: payload['email'] ?? '',
        roles,
        scopes,
        mfaSatisfied: payload['mfa_satisfied'] === true,
        sessionId: payload['sid'],
        sub: payload['sub'] ?? '',
        iss: payload['iss'] ?? '',
        aud: payload['aud'] ?? '',
        exp: payload['exp'] ?? 0,
        iat: payload['iat'] ?? 0,
      };
    } catch (err) {
      const reason = (err as Error).name ?? 'unknown';
      authFailures.inc({ reason });
      logger.warn({ err }, 'JWT verification failed');
      return null;
    }
  }

  async verifyApiKey(apiKey: string): Promise<AuthContext | null> {
    // TODO: Lookup API key from Vault/config store
    // For now, check Redis cache
    const redis = getRedisClient();
    const cached = await redis.get(`api_key:${apiKey}`);
    if (!cached) return null;

    try {
      return JSON.parse(cached) as AuthContext;
    } catch {
      return null;
    }
  }

  async createMfaSession(
    userId: string,
    email: string,
    mfaMethod: string,
    maskedDestination: string,
  ): Promise<string> {
    const token = uuidv4();
    const session: MfaSession = { userId, email, mfaMethod, maskedDestination };
    const redis = getRedisClient();
    await redis.setex(
      `mfa_session:${token}`,
      config.redis.mfaSessionTtl,
      JSON.stringify(session),
    );
    return token;
  }

  async validateMfaSession(token: string): Promise<MfaSession | null> {
    const redis = getRedisClient();
    const data = await redis.get(`mfa_session:${token}`);
    if (!data) return null;
    try {
      return JSON.parse(data) as MfaSession;
    } catch {
      return null;
    }
  }

  async deleteMfaSession(token: string): Promise<void> {
    const redis = getRedisClient();
    await redis.del(`mfa_session:${token}`);
  }

  async revokeToken(token: string, ttlSeconds: number): Promise<void> {
    const redis = getRedisClient();
    await redis.setex(`revoked_token:${token}`, ttlSeconds, '1');
  }

  private async isTokenRevoked(token: string): Promise<boolean> {
    const redis = getRedisClient();
    const result = await redis.exists(`revoked_token:${token}`);
    return result === 1;
  }

  private async getSigningKey(kid: string | undefined): Promise<string> {
    return new Promise((resolve, reject) => {
      this.jwksClient.getSigningKey(kid, (err, key) => {
        if (err || !key) return reject(err ?? new Error('No signing key found'));
        const signingKey = key.getPublicKey();
        resolve(signingKey);
      });
    });
  }
}
