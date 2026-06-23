export interface DomainEvent {
  readonly eventType: string;
  readonly aggregateId: string;
  readonly occurredAt: Date;
}

export class UserRegisteredEvent implements DomainEvent {
  readonly eventType = 'user.registered';
  readonly occurredAt = new Date();

  constructor(
    readonly aggregateId: string,
    readonly email: string,
    readonly idempotencyKey: string,
  ) {}
}

export class UserEmailVerifiedEvent implements DomainEvent {
  readonly eventType = 'user.email_verified';
  readonly occurredAt = new Date();

  constructor(
    readonly aggregateId: string,
    readonly email: string,
  ) {}
}
