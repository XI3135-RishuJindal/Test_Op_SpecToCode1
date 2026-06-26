export interface VerificationTokenProps {
  id: string;
  userId: string;
  tokenHash: string;
  expiresAt: Date;
  usedAt?: Date | null;
}

/**
 * Verification token — short-lived, single-use.
 */
export class VerificationToken {
  private readonly _id: string;
  private readonly _userId: string;
  private readonly _tokenHash: string;
  private readonly _expiresAt: Date;
  private _usedAt: Date | null;

  constructor(props: VerificationTokenProps) {
    this._id = props.id;
    this._userId = props.userId;
    this._tokenHash = props.tokenHash;
    this._expiresAt = props.expiresAt;
    this._usedAt = props.usedAt ?? null;
  }

  get id(): string {
    return this._id;
  }

  get userId(): string {
    return this._userId;
  }

  get tokenHash(): string {
    return this._tokenHash;
  }

  get expiresAt(): Date {
    return this._expiresAt;
  }

  get usedAt(): Date | null {
    return this._usedAt;
  }

  isExpired(): boolean {
    return new Date() > this._expiresAt;
  }

  isUsed(): boolean {
    return this._usedAt !== null;
  }

  isValid(): boolean {
    return !this.isExpired() && !this.isUsed();
  }

  markUsed(): void {
    if (!this.isValid()) {
      throw new Error('Token is already used or expired.');
    }
    this._usedAt = new Date();
  }
}
