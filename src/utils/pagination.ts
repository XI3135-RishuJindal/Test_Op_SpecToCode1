import { Request } from 'express';
import { PaginationMeta } from '../types';

export interface PaginationParams {
  page: number;
  limit: number;
  offset: number;
}

export function parsePagination(req: Request, maxLimit = 100): PaginationParams {
  const page = Math.max(1, parseInt(String(req.query['page'] ?? '1'), 10) || 1);
  const limit = Math.min(maxLimit, Math.max(1, parseInt(String(req.query['limit'] ?? '20'), 10) || 20));
  const offset = (page - 1) * limit;
  return { page, limit, offset };
}

export function buildPaginationMeta(page: number, limit: number, total: number): PaginationMeta {
  return {
    page,
    limit,
    total,
    totalPages: Math.ceil(total / limit),
  };
}
