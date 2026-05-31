import { query } from '../infrastructure/postgres.client';
import { GatewayRoute, CreateGatewayRouteRequest } from '../types';
import { v4 as uuidv4 } from 'uuid';
import { logger } from '../infrastructure/logger';

interface RouteRow {
  route_id: string;
  path_pattern: string;
  method: string;
  upstream_url: string;
  auth_required: boolean;
  required_scopes: string[] | null;
  strip_prefix: string | null;
  add_prefix: string | null;
  created_at: string;
  updated_at: string;
}

export class RoutingService {
  /**
   * Resolves the best matching route for a given path, method, and API version.
   */
  async resolveRoute(
    path: string,
    method: string,
    _version?: string,
  ): Promise<GatewayRoute | null> {
    try {
      const rows = await query<RouteRow>(
        `SELECT * FROM gateway_routes ORDER BY length(path_pattern) DESC`,
      );

      for (const row of rows) {
        if (this.matchesPattern(path, row.path_pattern)) {
          const methodMatch =
            row.method === '*' ||
            row.method.toUpperCase() === method.toUpperCase() ||
            (row.method.includes(',') &&
              row.method.split(',').map((m) => m.trim().toUpperCase()).includes(method.toUpperCase()));

          if (methodMatch) {
            return this.rowToRoute(row);
          }
        }
      }

      return null;
    } catch (err) {
      logger.error({ err }, 'Failed to resolve route from DB');
      return null;
    }
  }

  async findAll(): Promise<GatewayRoute[]> {
    const rows = await query<RouteRow>('SELECT * FROM gateway_routes ORDER BY created_at DESC');
    return rows.map(this.rowToRoute);
  }

  async create(request: CreateGatewayRouteRequest): Promise<GatewayRoute> {
    const routeId = uuidv4();
    const now = new Date().toISOString();

    const method = Array.isArray(request.method) ? request.method.join(',') : request.method;

    await query(
      `INSERT INTO gateway_routes
        (route_id, path_pattern, method, upstream_url, auth_required,
         required_scopes, strip_prefix, add_prefix, created_at, updated_at)
       VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10)`,
      [
        routeId,
        request.pathPattern,
        method,
        request.upstreamUrl,
        request.authRequired ?? true,
        request.requiredScopes ?? null,
        request.stripPrefix ?? null,
        request.addPrefix ?? null,
        now,
        now,
      ],
    );

    return {
      routeId,
      pathPattern: request.pathPattern,
      method: request.method,
      upstreamUrl: request.upstreamUrl,
      authRequired: request.authRequired ?? true,
      requiredScopes: request.requiredScopes,
      stripPrefix: request.stripPrefix,
      addPrefix: request.addPrefix,
      createdAt: now,
      updatedAt: now,
    };
  }

  async update(routeId: string, updates: Partial<CreateGatewayRouteRequest>): Promise<GatewayRoute | null> {
    const now = new Date().toISOString();
    const method = updates.method
      ? Array.isArray(updates.method) ? updates.method.join(',') : updates.method
      : undefined;

    await query(
      `UPDATE gateway_routes SET
        path_pattern = COALESCE($1, path_pattern),
        method = COALESCE($2, method),
        upstream_url = COALESCE($3, upstream_url),
        auth_required = COALESCE($4, auth_required),
        required_scopes = COALESCE($5, required_scopes),
        strip_prefix = COALESCE($6, strip_prefix),
        add_prefix = COALESCE($7, add_prefix),
        updated_at = $8
       WHERE route_id = $9`,
      [
        updates.pathPattern ?? null,
        method ?? null,
        updates.upstreamUrl ?? null,
        updates.authRequired ?? null,
        updates.requiredScopes ?? null,
        updates.stripPrefix ?? null,
        updates.addPrefix ?? null,
        now,
        routeId,
      ],
    );

    const [row] = await query<RouteRow>('SELECT * FROM gateway_routes WHERE route_id = $1', [routeId]);
    return row ? this.rowToRoute(row) : null;
  }

  async delete(routeId: string): Promise<boolean> {
    const result = await query('DELETE FROM gateway_routes WHERE route_id = $1 RETURNING route_id', [routeId]);
    return result.length > 0;
  }

  private matchesPattern(path: string, pattern: string): boolean {
    // Convert glob-like pattern to regex
    // e.g. /api/v1/users/** → matches /api/v1/users/anything
    const escaped = pattern
      .replace(/[.+^${}()|[\]\\]/g, '\\$&')
      .replace(/\*\*/g, '.*')
      .replace(/\*/g, '[^/]*')
      .replace(/\{[^}]+\}/g, '[^/]+');

    const regex = new RegExp(`^${escaped}$`);
    return regex.test(path);
  }

  private rowToRoute(row: RouteRow): GatewayRoute {
    return {
      routeId: row.route_id,
      pathPattern: row.path_pattern,
      method: row.method,
      upstreamUrl: row.upstream_url,
      authRequired: row.auth_required,
      requiredScopes: row.required_scopes ?? undefined,
      stripPrefix: row.strip_prefix ?? undefined,
      addPrefix: row.add_prefix ?? undefined,
      createdAt: row.created_at,
      updatedAt: row.updated_at,
    };
  }
}
