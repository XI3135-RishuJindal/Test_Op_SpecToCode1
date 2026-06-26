/**
 * Output port — password hashing and verification.
 */
export interface IPasswordHasher {
  hash(plainText: string): Promise<string>;
  verify(plainText: string, hash: string): Promise<boolean>;
}

export const PASSWORD_HASHER = Symbol('IPasswordHasher');
