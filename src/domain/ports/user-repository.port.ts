import { User } from '../entities/user.entity';
import { Email } from '../value-objects/email.vo';

/**
 * Output port — user repository.
 * Implementations live in the infrastructure layer.
 */
export interface IUserRepository {
  findById(id: string): Promise<User | null>;
  findByEmail(email: Email): Promise<User | null>;
  findByIdempotencyKey(key: string): Promise<User | null>;
  save(user: User): Promise<User>;
  update(user: User): Promise<User>;
}

export const USER_REPOSITORY = Symbol('IUserRepository');
