import { OutboxEvent } from '../entities/outbox-event.entity';

/**
 * Output port — outbox event repository.
 */
export interface IOutboxEventRepository {
  save(event: OutboxEvent): Promise<OutboxEvent>;
  findUnpublished(): Promise<OutboxEvent[]>;
  markPublished(id: string): Promise<void>;
}

export const OUTBOX_EVENT_REPOSITORY = Symbol('IOutboxEventRepository');
