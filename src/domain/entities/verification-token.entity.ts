export interface VerificationTokenProps {
  id: string;
  userId: string;
  tokenHash: string;
  expiresAt: Date;
  usedAt?: Date;
}

/**
 * Verification token aggregate.
 * Represents a short-lived, single-use email verification token.
 */
export class VerificationToken {
  private _id: string;
  private _userId: string;
  private _tokenHash: string;
  private _expiresAt: Date;
  private _usedAt?: Date;

  constructor(props: VerificationTokenProps) {
    this._id = props.id;
    this._userId = props.userId;
    this._tokenHash = props.tokenHash;
    this._expiresAt = props.expiresAt;
    this._usedAt = props.usedAt;
  }

  static create(props: Omit<VerificationTokenProps, 'usedAt'>): VerificationToken {
    return new VerificationToken(props);
  }

  static reconstitute(props: VerificationTokenProps): VerificationToken {
    return new VerificationToken(props);
  }

  isExpired(): boolean {
    return new Date() > this._expiresAt;
  }

  isUsed(): boolean {
    return this._usedAt !== undefined;
  }

  markUsed(): void {
    if (this.isUsed()) throw new Error('Token already used');
    if (this.isExpired()) throw new Error('Token has expired');
    this._usedAt = new Date();
  }

  get id(): string { return this._id; }
  get userId(): string { return this._userId; }
  get tokenHash(): string { return this._tokenHash; }
  get expiresAt(): Date { return this._expiresAt; }
  get usedAt(): Date | undefined { return this._usedAt; }
}
