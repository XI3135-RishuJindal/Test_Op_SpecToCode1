import { VerificationToken } from '../entities/verification-token.entity';

/**
 * Output port — verification token repository.
 */
export interface IVerificationTokenRepository {
  findByTokenHash(tokenHash: string): Promise<VerificationToken | null>;
  findActiveByUserId(userId: string): Promise<VerificationToken | null>;
  save(token: VerificationToken): Promise<VerificationToken>;
  update(token: VerificationToken): Promise<VerificationToken>;
}

export const VERIFICATION_TOKEN_REPOSITORY = Symbol('IVerificationTokenRepository');
