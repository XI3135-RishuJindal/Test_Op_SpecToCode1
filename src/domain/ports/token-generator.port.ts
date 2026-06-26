/**
 * Output port — cryptographically secure token generation.
 */
export interface ITokenGenerator {
  /**
   * Generate a URL-safe random token string.
   */
  generate(): Promise<string>;

  /**
   * Hash a raw token for safe storage.
   */
  hash(rawToken: string): string;
}

export const TOKEN_GENERATOR = Symbol('ITokenGenerator');
