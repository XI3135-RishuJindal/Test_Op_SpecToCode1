import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { IUserRepository } from '../../../domain/ports/user-repository.port';
import { User } from '../../../domain/entities/user.entity';
import { Email } from '../../../domain/value-objects/email.vo';
import { AccountStatus } from '../../../domain/enums/account-status.enum';
import { UserEntity } from '../entities/user.entity';

@Injectable()
export class TypeOrmUserRepository implements IUserRepository {
  constructor(
    @InjectRepository(UserEntity)
    private readonly repo: Repository<UserEntity>,
  ) {}

  async findById(id: string): Promise<User | null> {
    const entity = await this.repo.findOne({ where: { id } });
    return entity ? this.toDomain(entity) : null;
  }

  async findByEmail(email: Email): Promise<User | null> {
    const entity = await this.repo.findOne({ where: { email: email.value } });
    return entity ? this.toDomain(entity) : null;
  }

  async findByIdempotencyKey(key: string): Promise<User | null> {
    const entity = await this.repo.findOne({ where: { idempotencyKey: key } });
    return entity ? this.toDomain(entity) : null;
  }

  async save(user: User): Promise<User> {
    const entity = this.toEntity(user);
    const saved = await this.repo.save(entity);
    return this.toDomain(saved);
  }

  async update(user: User): Promise<User> {
    const entity = this.toEntity(user);
    const updated = await this.repo.save(entity);
    return this.toDomain(updated);
  }

  private toDomain(entity: UserEntity): User {
    return User.reconstitute({
      id: entity.id,
      email: new Email(entity.email),
      passwordHash: entity.passwordHash,
      status: entity.status as AccountStatus,
      idempotencyKey: entity.idempotencyKey,
      createdAt: entity.createdAt,
      updatedAt: entity.updatedAt,
    });
  }

  private toEntity(user: User): UserEntity {
    const entity = new UserEntity();
    entity.id = user.id;
    entity.email = user.email.value;
    entity.passwordHash = user.passwordHash;
    entity.status = user.status;
    entity.idempotencyKey = user.idempotencyKey;
    return entity;
  }
}
