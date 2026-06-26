import { User } from '../entities/user.entity';

/**
 * Output port — persistence contract for User aggregates.
 * Implemented by the infrastructure layer.
 */
export interface IUserRepository {
  /**
   * Persist a new user. Throws if a user with the same email already exists.
   */
  save(user: User): Promise<void>;

  /**
   * Find a user by their unique identifier.
   */
  findById(id: string): Promise<User | null>;

  /**
   * Find a user by their normalised email address.
   */
  findByEmail(email: string): Promise<User | null>;

  /**
   * Persist state changes to an existing user.
   */
  update(user: User): Promise<void>;
}

export const USER_REPOSITORY = Symbol('IUserRepository');
