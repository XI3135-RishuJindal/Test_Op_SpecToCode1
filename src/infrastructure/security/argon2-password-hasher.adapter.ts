import { Injectable } from '@nestjs/common';
import * as argon2 from 'argon2';
import { IPasswordHasher } from '../../../domain/ports/password-hasher.port';

/**
 * Argon2id password hasher — recommended for new systems.
 * Falls back gracefully if argon2 is unavailable (TODO: add bcrypt fallback).
 */
@Injectable()
export class Argon2PasswordHasher implements IPasswordHasher {
  async hash(plainText: string): Promise<string> {
    return argon2.hash(plainText, {
      type: argon2.argon2id,
      memoryCost: 65536, // 64 MiB
      timeCost: 3,
      parallelism: 4,
    });
  }

  async verify(plainText: string, hash: string): Promise<boolean> {
    return argon2.verify(hash, plainText);
  }
}
