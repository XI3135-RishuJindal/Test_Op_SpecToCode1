import { Injectable, ConflictException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { IUserRepository } from '../../../domain/ports/user-repository.port';
import { User } from '../../../domain/entities/user.entity';
import { UserEntity } from '../entities/user.entity';
import { AccountStatus } from '../../../domain/enums/account-status.enum';

@Injectable()
export class TypeOrmUserRepository implements IUserRepository {
  constructor(
    @InjectRepository(UserEntity)
    private readonly repo: Repository<UserEntity>,
  ) {}

  async save(user: User): Promise<void> {
    const existing = await this.repo.findOne({ where: { email: user.email } });
    if (existing) {
      throw new ConflictException(`User with email ${user.email} already exists.`);
    }
    const entity = this.toEntity(user);
    await this.repo.save(entity);
  }

  async findById(id: string): Promise<User | null> {
    const entity = await this.repo.findOne({ where: { id } });
    return entity ? this.toDomain(entity) : null;
  }

  async findByEmail(email: string): Promise<User | null> {
    const entity = await this.repo.findOne({ where: { email } });
    return entity ? this.toDomain(entity) : null;
  }

  async update(user: User): Promise<void> {
    await this.repo.update(user.id, {
      status: user.status,
      updatedAt: user.updatedAt,
    });
  }

  private toEntity(user: User): UserEntity {
    const entity = new UserEntity();
    entity.id = user.id;
    entity.email = user.email;
    entity.passwordHash = user.passwordHash;
    entity.status = user.status as AccountStatus;
    entity.createdAt = user.createdAt;
    entity.updatedAt = user.updatedAt;
    return entity;
  }

  private toDomain(entity: UserEntity): User {
    return new User({
      id: entity.id,
      email: entity.email,
      passwordHash: entity.passwordHash,
      status: entity.status,
      createdAt: entity.createdAt,
      updatedAt: entity.updatedAt,
    });
  }
}
