/**
 * Domain event emitted after a user successfully registers.
 * Written to the outbox transactionally.
 */
export interface UserRegisteredEvent {
  eventType: 'USER_REGISTERED';
  aggregateId: string;
  occurredAt: Date;
  payload: {
    userId: string;
    email: string;
    status: string;
  };
}

/**
 * Domain event emitted after a user's email is verified and account activated.
 */
export interface UserActivatedEvent {
  eventType: 'USER_ACTIVATED';
  aggregateId: string;
  occurredAt: Date;
  payload: {
    userId: string;
    email: string;
  };
}

export type DomainEvent = UserRegisteredEvent | UserActivatedEvent;
