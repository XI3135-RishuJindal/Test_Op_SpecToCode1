import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { IsNull, Repository } from 'typeorm';
import { IOutboxEventRepository } from '../../../domain/ports/outbox-event-repository.port';
import { OutboxEvent } from '../../../domain/entities/outbox-event.entity';
import { OutboxEventEntity } from '../entities/outbox-event.entity';

@Injectable()
export class TypeOrmOutboxEventRepository implements IOutboxEventRepository {
  constructor(
    @InjectRepository(OutboxEventEntity)
    private readonly repo: Repository<OutboxEventEntity>,
  ) {}

  async save(event: OutboxEvent): Promise<OutboxEvent> {
    const entity = this.toEntity(event);
    const saved = await this.repo.save(entity);
    return this.toDomain(saved);
  }

  async findUnpublished(): Promise<OutboxEvent[]> {
    const entities = await this.repo.find({
      where: { publishedAt: IsNull() },
      order: { occurredAt: 'ASC' },
    });
    return entities.map((e) => this.toDomain(e));
  }

  async markPublished(id: string): Promise<void> {
    await this.repo.update(id, { publishedAt: new Date() });
  }

  private toDomain(entity: OutboxEventEntity): OutboxEvent {
    const event = OutboxEvent.create({
      id: entity.id,
      aggregateId: entity.aggregateId,
      aggregateType: entity.aggregateType,
      eventType: entity.eventType,
      payload: entity.payload,
    });
    if (entity.publishedAt) event.markPublished();
    return event;
  }

  private toEntity(event: OutboxEvent): OutboxEventEntity {
    const entity = new OutboxEventEntity();
    entity.id = event.id;
    entity.aggregateId = event.aggregateId;
    entity.aggregateType = event.aggregateType;
    entity.eventType = event.eventType;
    entity.payload = event.payload;
    entity.publishedAt = event.publishedAt ?? null;
    return entity;
  }
}
