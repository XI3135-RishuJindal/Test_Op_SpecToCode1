import { AccountStatus } from '../enums/account-status.enum';

export interface UserProps {
  id: string;
  email: string;
  passwordHash: string;
  status: AccountStatus;
  createdAt: Date;
  updatedAt: Date;
}

/**
 * User aggregate root — core domain entity.
 * All state transitions are expressed as explicit methods.
 */
export class User {
  private readonly _id: string;
  private _email: string;
  private _passwordHash: string;
  private _status: AccountStatus;
  private _createdAt: Date;
  private _updatedAt: Date;

  constructor(props: UserProps) {
    this._id = props.id;
    this._email = props.email;
    this._passwordHash = props.passwordHash;
    this._status = props.status;
    this._createdAt = props.createdAt;
    this._updatedAt = props.updatedAt;
  }

  get id(): string {
    return this._id;
  }

  get email(): string {
    return this._email;
  }

  get passwordHash(): string {
    return this._passwordHash;
  }

  get status(): AccountStatus {
    return this._status;
  }

  get createdAt(): Date {
    return this._createdAt;
  }

  get updatedAt(): Date {
    return this._updatedAt;
  }

  /**
   * Transition account from PENDING_VERIFICATION → ACTIVE.
   * Throws if the account is not in the expected state.
   */
  activate(): void {
    if (this._status !== AccountStatus.PENDING_VERIFICATION) {
      throw new Error(
        `Cannot activate account in status ${this._status}. Expected PENDING_VERIFICATION.`,
      );
    }
    this._status = AccountStatus.ACTIVE;
    this._updatedAt = new Date();
  }

  isPendingVerification(): boolean {
    return this._status === AccountStatus.PENDING_VERIFICATION;
  }

  isActive(): boolean {
    return this._status === AccountStatus.ACTIVE;
  }
}
