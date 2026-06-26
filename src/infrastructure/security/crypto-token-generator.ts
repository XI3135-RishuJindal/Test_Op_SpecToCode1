import { Injectable } from '@nestjs/common';
import { randomBytes, createHash } from 'crypto';
import { ITokenGenerator } from '../../domain/ports/token-generator.port';

/**
 * Cryptographically secure token generator.
 * Generates 32-byte random tokens; stores SHA-256 hash.
 */
@Injectable()
export class CryptoTokenGenerator implements ITokenGenerator {
  async generate(): Promise<{ raw: string; hash: string }> {
    const raw = randomBytes(32).toString('hex');
    const hash = createHash('sha256').update(raw).digest('hex');
    return { raw, hash };
  }
}
