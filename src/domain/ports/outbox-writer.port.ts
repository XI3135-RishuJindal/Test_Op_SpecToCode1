import { DomainEvent } from '../events/user.events';

/**
 * Output port — transactional outbox writer.
 * Implementations must write events atomically with the triggering DB transaction.
 */
export interface IOutboxWriter {
  write(event: DomainEvent): Promise<void>;
}

export const OUTBOX_WRITER = Symbol('IOutboxWriter');
