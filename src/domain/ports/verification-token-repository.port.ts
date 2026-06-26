import { VerificationToken } from '../entities/verification-token.entity';

/**
 * Output port — persistence contract for VerificationToken aggregates.
 */
export interface IVerificationTokenRepository {
  save(token: VerificationToken): Promise<void>;
  findByTokenHash(tokenHash: string): Promise<VerificationToken | null>;
  update(token: VerificationToken): Promise<void>;
}

export const VERIFICATION_TOKEN_REPOSITORY = Symbol('IVerificationTokenRepository');
