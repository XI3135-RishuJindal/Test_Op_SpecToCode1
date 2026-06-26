import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { v4 as uuidv4 } from 'uuid';
import { IOutboxWriter } from '../../../domain/ports/outbox-writer.port';
import { DomainEvent } from '../../../domain/events/user.events';
import { OutboxEventEntity, OutboxEventStatus } from '../entities/outbox-event.entity';

@Injectable()
export class TypeOrmOutboxWriter implements IOutboxWriter {
  constructor(
    @InjectRepository(OutboxEventEntity)
    private readonly repo: Repository<OutboxEventEntity>,
  ) {}

  async write(event: DomainEvent): Promise<void> {
    const entity = new OutboxEventEntity();
    entity.id = uuidv4();
    entity.eventType = event.eventType;
    entity.aggregateId = event.aggregateId;
    entity.payload = event.payload as Record<string, unknown>;
    entity.status = OutboxEventStatus.PENDING;
    entity.occurredAt = event.occurredAt;
    entity.publishedAt = null;
    await this.repo.save(entity);
  }
}
