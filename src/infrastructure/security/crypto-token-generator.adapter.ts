import { Injectable } from '@nestjs/common';
import * as crypto from 'crypto';
import { ITokenGenerator } from '../../../domain/ports/token-generator.port';

@Injectable()
export class CryptoTokenGenerator implements ITokenGenerator {
  private static readonly TOKEN_BYTES = 32;

  async generate(): Promise<string> {
    return new Promise<string>((resolve, reject) => {
      crypto.randomBytes(CryptoTokenGenerator.TOKEN_BYTES, (err, buf) => {
        if (err) reject(err);
        else resolve(buf.toString('hex'));
      });
    });
  }

  hash(rawToken: string): string {
    return crypto.createHash('sha256').update(rawToken).digest('hex');
  }
}
