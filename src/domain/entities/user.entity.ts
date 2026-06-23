import { Email } from '../value-objects/email.vo';
import { AccountStatus } from '../enums/account-status.enum';

export interface UserProps {
  id: string;
  email: Email;
  passwordHash: string;
  status: AccountStatus;
  idempotencyKey: string;
  createdAt: Date;
  updatedAt: Date;
}

/**
 * User aggregate root.
 * Encapsulates all state transitions and invariants for a user account.
 */
export class User {
  private _id: string;
  private _email: Email;
  private _passwordHash: string;
  private _status: AccountStatus;
  private _idempotencyKey: string;
  private _createdAt: Date;
  private _updatedAt: Date;

  constructor(props: UserProps) {
    this._id = props.id;
    this._email = props.email;
    this._passwordHash = props.passwordHash;
    this._status = props.status;
    this._idempotencyKey = props.idempotencyKey;
    this._createdAt = props.createdAt;
    this._updatedAt = props.updatedAt;
  }

  // ── Factories ──────────────────────────────────────────────────────────────

  static create(props: Omit<UserProps, 'createdAt' | 'updatedAt'>): User {
    const now = new Date();
    return new User({
      ...props,
      createdAt: now,
      updatedAt: now,
    });
  }

  static reconstitute(props: UserProps): User {
    return new User(props);
  }

  // ── Commands ───────────────────────────────────────────────────────────────

  activate(): void {
    if (this._status !== AccountStatus.PENDING_VERIFICATION) {
      throw new Error(
        `Cannot activate account in status ${this._status}`,
      );
    }
    this._status = AccountStatus.ACTIVE;
    this._updatedAt = new Date();
  }

  suspend(): void {
    if (this._status === AccountStatus.DEACTIVATED) {
      throw new Error('Cannot suspend a deactivated account');
    }
    this._status = AccountStatus.SUSPENDED;
    this._updatedAt = new Date();
  }

  // ── Getters ────────────────────────────────────────────────────────────────

  get id(): string { return this._id; }
  get email(): Email { return this._email; }
  get passwordHash(): string { return this._passwordHash; }
  get status(): AccountStatus { return this._status; }
  get idempotencyKey(): string { return this._idempotencyKey; }
  get createdAt(): Date { return this._createdAt; }
  get updatedAt(): Date { return this._updatedAt; }
}
