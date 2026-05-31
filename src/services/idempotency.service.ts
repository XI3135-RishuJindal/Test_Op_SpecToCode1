import { getRedisClient } from '../infrastructure/redis.client';
import { config } from '../config';
import { createHash } from 'crypto';

export interface IdempotencyRecord {
  response: unknown;
  statusCode: number;
  createdAt: string;
}

export class IdempotencyService {
  private keyPrefix = 'idempotency:';

  /**
   * Check if an idempotency key already exists.
   * Returns the cached response if it does.
   */
  async check(
    key: string,
    requestHash: string,
  ): Promise<{ exists: true; conflict: boolean; record: IdempotencyRecord } | { exists: false }> {
    const redis = getRedisClient();
    const data = await redis.get(`${this.keyPrefix}${key}`);

    if (!data) return { exists: false };

    const record = JSON.parse(data) as IdempotencyRecord & { requestHash: string };

    if (record.requestHash !== requestHash) {
      return { exists: true, conflict: true, record };
    }

    return { exists: true, conflict: false, record };
  }

  /**
   * Store the result for an idempotency key.
   */
  async store(key: string, requestHash: string, response: unknown, statusCode: number): Promise<void> {
    const redis = getRedisClient();
    const record = {
      response,
      statusCode,
      requestHash,
      createdAt: new Date().toISOString(),
    };

    await redis.setex(
      `${this.keyPrefix}${key}`,
      config.redis.idempotencyKeyTtl,
      JSON.stringify(record),
    );
  }

  /**
   * Compute a hash of the request body for conflict detection.
   */
  hashRequest(body: unknown): string {
    return createHash('sha256')
      .update(JSON.stringify(body))
      .digest('hex');
  }
}
