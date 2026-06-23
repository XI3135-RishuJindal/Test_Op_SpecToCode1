/**
 * Strongly-typed Email value object.
 * Normalises to lowercase and validates format on construction.
 */
export class Email {
  private readonly _value: string;

  constructor(raw: string) {
    const normalised = raw.trim().toLowerCase();
    if (!Email.isValid(normalised)) {
      throw new Error(`Invalid email address: ${raw}`);
    }
    this._value = normalised;
  }

  static isValid(value: string): boolean {
    // RFC-5322 simplified pattern
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
  }

  get value(): string {
    return this._value;
  }

  equals(other: Email): boolean {
    return this._value === other._value;
  }

  toString(): string {
    return this._value;
  }
}
