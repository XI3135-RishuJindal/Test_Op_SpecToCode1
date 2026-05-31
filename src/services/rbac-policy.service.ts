import { query } from '../infrastructure/postgres.client';
import { RbacPolicy, CreateRbacPolicyRequest } from '../types';
import { v4 as uuidv4 } from 'uuid';

interface RbacPolicyRow {
  policy_id: string;
  name: string;
  roles: string[];
  resource: string;
  actions: string[];
  effect: string;
  conditions: unknown;
  created_at: string;
}

export class RbacPolicyService {
  async findAll(): Promise<RbacPolicy[]> {
    const rows = await query<RbacPolicyRow>(
      'SELECT * FROM rbac_policies ORDER BY created_at DESC',
    );
    return rows.map(this.rowToPolicy);
  }

  async create(request: CreateRbacPolicyRequest): Promise<RbacPolicy> {
    const policyId = uuidv4();
    const now = new Date().toISOString();

    await query(
      `INSERT INTO rbac_policies
        (policy_id, name, roles, resource, actions, effect, conditions, created_at)
       VALUES ($1,$2,$3,$4,$5,$6,$7,$8)`,
      [
        policyId,
        request.name,
        request.roles,
        request.resource,
        request.actions,
        request.effect,
        request.conditions ? JSON.stringify(request.conditions) : null,
        now,
      ],
    );

    return {
      policyId,
      name: request.name,
      roles: request.roles,
      resource: request.resource,
      actions: request.actions,
      effect: request.effect,
      conditions: request.conditions,
      createdAt: now,
    };
  }

  private rowToPolicy(row: RbacPolicyRow): RbacPolicy {
    return {
      policyId: row.policy_id,
      name: row.name,
      roles: row.roles,
      resource: row.resource,
      actions: row.actions,
      effect: row.effect as 'allow' | 'deny',
      conditions: row.conditions as Record<string, unknown> | undefined,
      createdAt: row.created_at,
    };
  }
}
