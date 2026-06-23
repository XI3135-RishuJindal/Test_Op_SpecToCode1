/**
 * Output port — password hashing service.
 */
export interface IPasswordHasher {
  hash(plaintext: string): Promise<string>;
  verify(plaintext: string, hash: string): Promise<boolean>;
}

export const PASSWORD_HASHER = Symbol('IPasswordHasher');
