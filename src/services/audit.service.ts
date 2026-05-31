import { v4 as uuidv4 } from 'uuid';
import { publishMessage } from '../infrastructure/kafka.client';
import { query } from '../infrastructure/postgres.client';
import { config } from '../config';
import { logger } from '../infrastructure/logger';
import { AuditLogEvent, AuditLogEntry, AuditLogListResponse, PaginationMeta } from '../types';
import { auditEventsPublished } from '../infrastructure/metrics';

export class AuditService {
  async log(event: AuditLogEvent): Promise<void> {
    const logId = uuidv4();
    const timestamp = new Date().toISOString();

    const entry: AuditLogEntry = {
      logId,
      ...event,
      timestamp,
    };

    // Persist to Postgres
    try {
      await query(
        `INSERT INTO audit_logs
          (log_id, principal, action, resource, status, status_code, correlation_id,
           path, ip_address, user_agent, error_code, metadata, timestamp)
         VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13)`,
        [
          logId,
          event.principal,
          event.action,
          event.resource,
          event.status,
          event.statusCode ?? null,
          event.correlationId,
          event.path ?? null,
          event.ipAddress ?? null,
          event.userAgent ?? null,
          event.errorCode ?? null,
          event.metadata ? JSON.stringify(event.metadata) : null,
          timestamp,
        ],
      );
    } catch (err) {
      logger.error({ err, event }, 'Failed to persist audit log to Postgres');
    }

    // Publish to Kafka for immutable audit stream
    await publishMessage(config.kafka.auditTopic, logId, entry);

    auditEventsPublished.inc({ action: event.action, status: event.status });
  }

  async queryLogs(filters: {
    principal?: string;
    statusCode?: number;
    path?: string;
    from?: string;
    to?: string;
    page?: number;
    limit?: number;
  }): Promise<AuditLogListResponse> {
    const page = filters.page ?? 1;
    const limit = filters.limit ?? 20;
    const offset = (page - 1) * limit;

    const conditions: string[] = [];
    const params: unknown[] = [];
    let paramIdx = 1;

    if (filters.principal) {
      conditions.push(`principal = $${paramIdx++}`);
      params.push(filters.principal);
    }
    if (filters.statusCode) {
      conditions.push(`status_code = $${paramIdx++}`);
      params.push(filters.statusCode);
    }
    if (filters.path) {
      conditions.push(`path ILIKE $${paramIdx++}`);
      params.push(`%${filters.path}%`);
    }
    if (filters.from) {
      conditions.push(`timestamp >= $${paramIdx++}`);
      params.push(filters.from);
    }
    if (filters.to) {
      conditions.push(`timestamp <= $${paramIdx++}`);
      params.push(filters.to);
    }

    const whereClause = conditions.length > 0 ? `WHERE ${conditions.join(' AND ')}` : '';

    const [countResult] = await query<{ count: string }>(
      `SELECT COUNT(*) as count FROM audit_logs ${whereClause}`,
      params,
    );
    const total = parseInt(countResult?.count ?? '0', 10);

    const rows = await query<{
      log_id: string;
      principal: string;
      action: string;
      resource: string;
      status: string;
      status_code: number;
      correlation_id: string;
      path: string;
      ip_address: string;
      user_agent: string;
      error_code: string;
      metadata: unknown;
      timestamp: string;
    }>(
      `SELECT * FROM audit_logs ${whereClause}
       ORDER BY timestamp DESC
       LIMIT $${paramIdx++} OFFSET $${paramIdx++}`,
      [...params, limit, offset],
    );

    const data: AuditLogEntry[] = rows.map((r) => ({
      logId: r.log_id,
      principal: r.principal,
      action: r.action,
      resource: r.resource,
      status: r.status as 'success' | 'failure',
      statusCode: r.status_code,
      correlationId: r.correlation_id,
      path: r.path,
      ipAddress: r.ip_address,
      userAgent: r.user_agent,
      errorCode: r.error_code,
      metadata: r.metadata as Record<string, unknown>,
      timestamp: r.timestamp,
    }));

    const meta: PaginationMeta = {
      page,
      limit,
      total,
      totalPages: Math.ceil(total / limit),
    };

    return { data, meta };
  }
}
