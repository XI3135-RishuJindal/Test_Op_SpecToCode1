import { query } from '../infrastructure/postgres.client';
import { RateLimitPolicy, CreateRateLimitPolicyRequest } from '../types';
import { v4 as uuidv4 } from 'uuid';

interface RateLimitPolicyRow {
  policy_id: string;
  name: string;
  path_pattern: string;
  window_ms: string;
  max_requests: number;
  key_by: string;
  burst_allowance: number | null;
  created_at: string;
}

export class RateLimitPolicyService {
  async findAll(): Promise<RateLimitPolicy[]> {
    const rows = await query<RateLimitPolicyRow>(
      'SELECT * FROM rate_limit_policies ORDER BY created_at DESC',
    );
    return rows.map(this.rowToPolicy);
  }

  async create(request: CreateRateLimitPolicyRequest): Promise<RateLimitPolicy> {
    const policyId = uuidv4();
    const now = new Date().toISOString();

    await query(
      `INSERT INTO rate_limit_policies
        (policy_id, name, path_pattern, window_ms, max_requests, key_by, burst_allowance, created_at)
       VALUES ($1,$2,$3,$4,$5,$6,$7,$8)`,
      [
        policyId,
        request.name,
        request.pathPattern,
        request.windowMs,
        request.maxRequests,
        request.keyBy,
        request.burstAllowance ?? null,
        now,
      ],
    );

    return {
      policyId,
      name: request.name,
      pathPattern: request.pathPattern,
      windowMs: request.windowMs,
      maxRequests: request.maxRequests,
      keyBy: request.keyBy,
      burstAllowance: request.burstAllowance,
      createdAt: now,
    };
  }

  private rowToPolicy(row: RateLimitPolicyRow): RateLimitPolicy {
    return {
      policyId: row.policy_id,
      name: row.name,
      pathPattern: row.path_pattern,
      windowMs: parseInt(row.window_ms, 10),
      maxRequests: row.max_requests,
      keyBy: row.key_by as 'ip' | 'userId' | 'apiKey',
      burstAllowance: row.burst_allowance ?? undefined,
      createdAt: row.created_at,
    };
  }
}
