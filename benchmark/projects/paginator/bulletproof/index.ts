import { clamp } from '../shared/clamp.ts';

export interface PageInput { total: number; pageSize: number; page: number; }
export interface PageResult {
  page: number; pageSize: number; totalPages: number;
  startIndex: number; endIndex: number; hasPrev: boolean; hasNext: boolean;
}

export function paginate(input: PageInput): PageResult {
  const { total, pageSize } = input;
  if (!Number.isInteger(pageSize) || pageSize < 1) throw new Error('pageSize must be a positive integer');
  if (!Number.isInteger(total) || total < 0) throw new Error('total must be a non-negative integer');

  const totalPages = total === 0 ? 0 : Math.ceil(total / pageSize);
  const page = clamp(Math.trunc(input.page) || 1, 1, Math.max(totalPages, 1)); // reuse shared clamp
  const startIndex = total === 0 ? 0 : (page - 1) * pageSize;
  const endIndex = Math.min(startIndex + pageSize, total);

  return { page, pageSize, totalPages, startIndex, endIndex, hasPrev: page > 1, hasNext: page < totalPages };
}
