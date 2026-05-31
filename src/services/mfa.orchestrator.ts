import { upstreamClients } from '../infrastructure/http.client';
import { AuthService } from './auth.service';
import { LoginRequest, LoginResponse, MfaVerifyRequest, TokenResponse,
  MfaEnrollRequest, MfaEnrollResponse, TokenRefreshRequest } from '../types';
import { UpstreamError } from '../utils/errors';
import { logger } from '../infrastructure/logger';

export class MfaOrchestrator {
  constructor(private readonly authService: AuthService) {}

  /**
   * First-factor login: validates credentials, creates MFA session.
   */
  async login(request: LoginRequest): Promise<LoginResponse> {
    const response = await upstreamClients.mfa.send<LoginResponse>(
      'POST',
      '/v1/auth/login',
      {
        body: request,
        headers: { 'Content-Type': 'application/json' },
      },
    );

    if (response.status !== 200) {
      this.handleUpstreamError(response.status, 'Login failed');
    }

    const { mfaMethod, maskedDestination, expiresIn } = response.data;

    // Create MFA session in Redis
    // We use a placeholder userId from the upstream response
    const upstreamData = response.data as LoginResponse & { userId?: string; email?: string };
    const userId = upstreamData.userId ?? 'unknown';
    const email = upstreamData.email ?? request.username;

    const mfaSessionToken = await this.authService.createMfaSession(
      userId,
      email,
      mfaMethod,
      maskedDestination,
    );

    return {
      mfaSessionToken,
      mfaMethod,
      maskedDestination,
      expiresIn: expiresIn ?? 300,
    };
  }

  /**
   * Second-factor: verifies OTP and issues access/refresh tokens.
   */
  async verifyMfa(
    mfaSessionToken: string,
    userId: string,
    request: MfaVerifyRequest,
  ): Promise<TokenResponse> {
    const response = await upstreamClients.mfa.send<TokenResponse>(
      'POST',
      '/v1/auth/mfa/verify',
      {
        body: { ...request, userId },
        headers: {
          'Content-Type': 'application/json',
          'X-MFA-Session-Token': mfaSessionToken,
        },
      },
    );

    if (response.status !== 200) {
      this.handleUpstreamError(response.status, 'MFA verification failed');
    }

    // Invalidate MFA session after successful verification
    await this.authService.deleteMfaSession(mfaSessionToken);

    return response.data;
  }

  /**
   * Refresh access token using refresh token.
   */
  async refreshToken(request: TokenRefreshRequest): Promise<TokenResponse> {
    const response = await upstreamClients.mfa.send<TokenResponse>(
      'POST',
      '/v1/auth/token/refresh',
      {
        body: request,
        headers: { 'Content-Type': 'application/json' },
      },
    );

    if (response.status !== 200) {
      this.handleUpstreamError(response.status, 'Token refresh failed');
    }

    return response.data;
  }

  /**
   * Logout: revoke tokens.
   */
  async logout(accessToken: string, refreshToken?: string): Promise<void> {
    try {
      await upstreamClients.mfa.send(
        'POST',
        '/v1/auth/logout',
        {
          body: { accessToken, refreshToken },
          headers: { 'Content-Type': 'application/json' },
        },
      );
    } catch (err) {
      logger.warn({ err }, 'Upstream logout failed — revoking token locally');
    }

    // Always revoke in Redis regardless of upstream result
    const ttl = 3600; // 1h — access token lifetime
    await this.authService.revokeToken(accessToken, ttl);
  }

  /**
   * Enroll MFA method.
   */
  async enrollMfa(
    userId: string,
    request: MfaEnrollRequest,
    authHeader: string,
  ): Promise<MfaEnrollResponse> {
    const response = await upstreamClients.mfa.send<MfaEnrollResponse>(
      'POST',
      '/v1/auth/mfa/enroll',
      {
        body: { ...request, userId },
        headers: {
          'Content-Type': 'application/json',
          'Authorization': authHeader,
        },
      },
    );

    if (response.status === 409) {
      throw Object.assign(new Error('MFA method already enrolled'), { statusCode: 409, code: 'CONFLICT' });
    }

    if (response.status !== 201) {
      this.handleUpstreamError(response.status, 'MFA enrollment failed');
    }

    return response.data;
  }

  /**
   * De-enroll MFA method.
   */
  async deEnrollMfa(userId: string, methodId: string, authHeader: string): Promise<void> {
    const response = await upstreamClients.mfa.send(
      'DELETE',
      `/v1/auth/mfa/enroll/${methodId}`,
      {
        headers: {
          'Authorization': authHeader,
          'X-User-ID': userId,
        },
      },
    );

    if (response.status !== 204 && response.status !== 200) {
      this.handleUpstreamError(response.status, 'MFA de-enrollment failed');
    }
  }

  private handleUpstreamError(status: number, defaultMessage: string): never {
    if (status === 401) throw Object.assign(new Error('Unauthorized'), { statusCode: 401, code: 'UNAUTHORIZED' });
    if (status === 403) throw Object.assign(new Error('Forbidden'), { statusCode: 403, code: 'FORBIDDEN' });
    if (status === 404) throw Object.assign(new Error('Not found'), { statusCode: 404, code: 'NOT_FOUND' });
    if (status === 409) throw Object.assign(new Error('Conflict'), { statusCode: 409, code: 'CONFLICT' });
    if (status === 422) throw Object.assign(new Error('Validation error'), { statusCode: 422, code: 'VALIDATION_ERROR' });
    throw new UpstreamError(defaultMessage, status >= 500 ? 503 : status);
  }
}
