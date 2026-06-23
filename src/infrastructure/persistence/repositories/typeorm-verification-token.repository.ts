import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { IsNull, Repository } from 'typeorm';
import { IVerificationTokenRepository } from '../../../domain/ports/verification-token-repository.port';
import { VerificationToken } from '../../../domain/entities/verification-token.entity';
import { VerificationTokenEntity } from '../entities/verification-token.entity';

@Injectable()
export class TypeOrmVerificationTokenRepository implements IVerificationTokenRepository {
  constructor(
    @InjectRepository(VerificationTokenEntity)
    private readonly repo: Repository<VerificationTokenEntity>,
  ) {}

  async findByTokenHash(tokenHash: string): Promise<VerificationToken | null> {
    const entity = await this.repo.findOne({ where: { tokenHash } });
    return entity ? this.toDomain(entity) : null;
  }

  async findActiveByUserId(userId: string): Promise<VerificationToken | null> {
    const entity = await this.repo.findOne({
      where: { userId, usedAt: IsNull() },
      order: { createdAt: 'DESC' },
    });
    return entity ? this.toDomain(entity) : null;
  }

  async save(token: VerificationToken): Promise<VerificationToken> {
    const entity = this.toEntity(token);
    const saved = await this.repo.save(entity);
    return this.toDomain(saved);
  }

  async update(token: VerificationToken): Promise<VerificationToken> {
    const entity = this.toEntity(token);
    const updated = await this.repo.save(entity);
    return this.toDomain(updated);
  }

  private toDomain(entity: VerificationTokenEntity): VerificationToken {
    return VerificationToken.reconstitute({
      id: entity.id,
      userId: entity.userId,
      tokenHash: entity.tokenHash,
      expiresAt: entity.expiresAt,
      usedAt: entity.usedAt ?? undefined,
    });
  }

  private toEntity(token: VerificationToken): VerificationTokenEntity {
    const entity = new VerificationTokenEntity();
    entity.id = token.id;
    entity.userId = token.userId;
    entity.tokenHash = token.tokenHash;
    entity.expiresAt = token.expiresAt;
    entity.usedAt = token.usedAt ?? null;
    return entity;
  }
}
