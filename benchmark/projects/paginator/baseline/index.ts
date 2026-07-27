export interface PageInput { total: number; pageSize: number; page: number; }
export interface PageResult {
  page: number; pageSize: number; totalPages: number;
  startIndex: number; endIndex: number; hasPrev: boolean; hasNext: boolean;
}

// Naive pagination. Looks fine on the happy path; wrong on partial last pages,
// out-of-range pages, and empty inputs.
export function paginate(input: PageInput): PageResult {
  const { total, pageSize, page } = input;
  const totalPages = Math.floor(total / pageSize); // BUG: truncates the partial last page
  const startIndex = (page - 1) * pageSize;         // BUG: no clamping of page
  const endIndex = startIndex + pageSize;           // BUG: can exceed total
  return { page, pageSize, totalPages, startIndex, endIndex, hasPrev: page > 1, hasNext: page < totalPages };
}
