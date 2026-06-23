/**
 * Output port — token generator.
 * Produces cryptographically secure random tokens and their hashes.
 */
export interface ITokenGenerator {
  /** Returns { raw, hash } — raw is sent to the user, hash is stored. */
  generate(): Promise<{ raw: string; hash: string }>;
}

export const TOKEN_GENERATOR = Symbol('ITokenGenerator');
