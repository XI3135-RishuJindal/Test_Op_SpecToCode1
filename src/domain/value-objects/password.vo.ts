/**
 * Password policy value object.
 * Validates raw passwords against the configured policy before hashing.
 */
export class Password {
  static readonly MIN_LENGTH = 8;
  static readonly MAX_LENGTH = 128;

  private constructor() {}

  /**
   * Validates a raw (plain-text) password against the policy.
   * Throws a descriptive error if the policy is violated.
   */
  static validate(raw: string): void {
    if (raw.length < Password.MIN_LENGTH) {
      throw new Error(`Password must be at least ${Password.MIN_LENGTH} characters.`);
    }
    if (raw.length > Password.MAX_LENGTH) {
      throw new Error(`Password must not exceed ${Password.MAX_LENGTH} characters.`);
    }
    if (!/[A-Z]/.test(raw)) {
      throw new Error('Password must contain at least one uppercase letter.');
    }
    if (!/[a-z]/.test(raw)) {
      throw new Error('Password must contain at least one lowercase letter.');
    }
    if (!/[0-9]/.test(raw)) {
      throw new Error('Password must contain at least one digit.');
    }
    if (!/[^A-Za-z0-9]/.test(raw)) {
      throw new Error('Password must contain at least one special character.');
    }
  }
}
