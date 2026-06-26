import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { IVerificationTokenRepository } from '../../../domain/ports/verification-token-repository.port';
import { VerificationToken } from '../../../domain/entities/verification-token.entity';
import { VerificationTokenEntity } from '../entities/verification-token.entity';

@Injectable()
export class TypeOrmVerificationTokenRepository implements IVerificationTokenRepository {
  constructor(
    @InjectRepository(VerificationTokenEntity)
    private readonly repo: Repository<VerificationTokenEntity>,
  ) {}

  async save(token: VerificationToken): Promise<void> {
    const entity = this.toEntity(token);
    await this.repo.save(entity);
  }

  async findByTokenHash(tokenHash: string): Promise<VerificationToken | null> {
    const entity = await this.repo.findOne({ where: { tokenHash } });
    return entity ? this.toDomain(entity) : null;
  }

  async update(token: VerificationToken): Promise<void> {
    await this.repo.update(token.id, { usedAt: token.usedAt });
  }

  private toEntity(token: VerificationToken): VerificationTokenEntity {
    const entity = new VerificationTokenEntity();
    entity.id = token.id;
    entity.userId = token.userId;
    entity.tokenHash = token.tokenHash;
    entity.expiresAt = token.expiresAt;
    entity.usedAt = token.usedAt;
    return entity;
  }

  private toDomain(entity: VerificationTokenEntity): VerificationToken {
    return new VerificationToken({
      id: entity.id,
      userId: entity.userId,
      tokenHash: entity.tokenHash,
      expiresAt: entity.expiresAt,
      usedAt: entity.usedAt,
    });
  }
}
