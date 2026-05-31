import { Pool, PoolClient } from 'pg';
import { config } from '../config';
import { logger } from './logger';

let pool: Pool | null = null;

export function getPool(): Pool {
  if (!pool) {
    pool = new Pool({
      connectionString: config.database.url,
      max: 20,
      idleTimeoutMillis: 30_000,
      connectionTimeoutMillis: 5_000,
    });

    pool.on('error', (err) => logger.error({ err }, 'Postgres pool error'));
    pool.on('connect', () => logger.debug('Postgres client connected'));
  }
  return pool;
}

export async function query<T = unknown>(
  sql: string,
  params?: unknown[],
): Promise<T[]> {
  const pool = getPool();
  const result = await pool.query<T>(sql, params);
  return result.rows;
}

export async function withTransaction<T>(
  fn: (client: PoolClient) => Promise<T>,
): Promise<T> {
  const pool = getPool();
  const client = await pool.connect();
  try {
    await client.query('BEGIN');
    const result = await fn(client);
    await client.query('COMMIT');
    return result;
  } catch (err) {
    await client.query('ROLLBACK');
    throw err;
  } finally {
    client.release();
  }
}

export async function initSchema(): Promise<void> {
  const pool = getPool();
  await pool.query(`
    CREATE TABLE IF NOT EXISTS gateway_routes (
      route_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      path_pattern TEXT NOT NULL,
      method TEXT NOT NULL,
      upstream_url TEXT NOT NULL,
      auth_required BOOLEAN NOT NULL DEFAULT TRUE,
      required_scopes TEXT[],
      strip_prefix TEXT,
      add_prefix TEXT,
      created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
      updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );

    CREATE TABLE IF NOT EXISTS rate_limit_policies (
      policy_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      name TEXT NOT NULL,
      path_pattern TEXT NOT NULL,
      window_ms BIGINT NOT NULL,
      max_requests INTEGER NOT NULL,
      key_by TEXT NOT NULL,
      burst_allowance INTEGER,
      created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );

    CREATE TABLE IF NOT EXISTS rbac_policies (
      policy_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      name TEXT NOT NULL,
      roles TEXT[] NOT NULL,
      resource TEXT NOT NULL,
      actions TEXT[] NOT NULL,
      effect TEXT NOT NULL,
      conditions JSONB,
      created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );

    CREATE TABLE IF NOT EXISTS audit_logs (
      log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      principal TEXT NOT NULL,
      action TEXT NOT NULL,
      resource TEXT NOT NULL,
      status TEXT NOT NULL,
      status_code INTEGER,
      correlation_id TEXT NOT NULL,
      path TEXT,
      ip_address TEXT,
      user_agent TEXT,
      error_code TEXT,
      metadata JSONB,
      timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );

    CREATE INDEX IF NOT EXISTS idx_audit_logs_principal ON audit_logs(principal);
    CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON audit_logs(timestamp);
    CREATE INDEX IF NOT EXISTS idx_audit_logs_correlation ON audit_logs(correlation_id);
  `);
  logger.info('Database schema initialized');
}

export async function disconnectPostgres(): Promise<void> {
  if (pool) {
    await pool.end();
    pool = null;
  }
}
