/**
 * Password value object — wraps the raw plaintext password and enforces policy.
 * The hashed form is stored separately; this VO is only used during registration.
 */
export class Password {
  private readonly _value: string;

  private static readonly MIN_LENGTH = 8;
  private static readonly MAX_LENGTH = 128;

  constructor(raw: string) {
    const errors = Password.validate(raw);
    if (errors.length > 0) {
      throw new Error(`Password policy violation: ${errors.join(', ')}`);
    }
    this._value = raw;
  }

  static validate(raw: string): string[] {
    const errors: string[] = [];
    if (raw.length < Password.MIN_LENGTH) {
      errors.push(`minimum length is ${Password.MIN_LENGTH}`);
    }
    if (raw.length > Password.MAX_LENGTH) {
      errors.push(`maximum length is ${Password.MAX_LENGTH}`);
    }
    if (!/[A-Z]/.test(raw)) errors.push('must contain an uppercase letter');
    if (!/[a-z]/.test(raw)) errors.push('must contain a lowercase letter');
    if (!/[0-9]/.test(raw)) errors.push('must contain a digit');
    if (!/[^A-Za-z0-9]/.test(raw)) errors.push('must contain a special character');
    return errors;
  }

  get value(): string {
    return this._value;
  }
}
