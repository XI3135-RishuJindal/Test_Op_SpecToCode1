export interface OutboxEventProps {
  id: string;
  aggregateId: string;
  aggregateType: string;
  eventType: string;
  payload: Record<string, unknown>;
  occurredAt: Date;
  publishedAt?: Date;
}

/**
 * Outbox event — written transactionally alongside user data to guarantee
 * at-least-once delivery of integration events.
 */
export class OutboxEvent {
  constructor(private readonly props: OutboxEventProps) {}

  static create(
    props: Omit<OutboxEventProps, 'occurredAt' | 'publishedAt'>,
  ): OutboxEvent {
    return new OutboxEvent({ ...props, occurredAt: new Date() });
  }

  markPublished(): void {
    this.props.publishedAt = new Date();
  }

  get id(): string { return this.props.id; }
  get aggregateId(): string { return this.props.aggregateId; }
  get aggregateType(): string { return this.props.aggregateType; }
  get eventType(): string { return this.props.eventType; }
  get payload(): Record<string, unknown> { return this.props.payload; }
  get occurredAt(): Date { return this.props.occurredAt; }
  get publishedAt(): Date | undefined { return this.props.publishedAt; }
}
