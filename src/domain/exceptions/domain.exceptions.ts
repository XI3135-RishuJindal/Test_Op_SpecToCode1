export class DomainException extends Error {
  constructor(message: string) {
    super(message);
    this.name = this.constructor.name;
  }
}

export class UserAlreadyExistsException extends DomainException {
  constructor() {
    super('A user with this email already exists');
  }
}

export class UserNotFoundException extends DomainException {
  constructor() {
    super('User not found');
  }
}

export class InvalidVerificationTokenException extends DomainException {
  constructor() {
    super('Verification token is invalid, expired, or already used');
  }
}

export class AccountNotPendingVerificationException extends DomainException {
  constructor() {
    super('Account is not in PENDING_VERIFICATION status');
  }
}
