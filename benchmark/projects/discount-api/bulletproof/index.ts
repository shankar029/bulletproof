import http from 'node:http';

/** Error carrying a stable machine-readable code for HTTP mapping. */
export class DiscountError extends Error {
  readonly code: string;
  constructor(code: string, message: string) {
    super(message);
    this.name = 'DiscountError';
    this.code = code;
  }
}

interface CodeDef {
  type: 'pct' | 'flat';
  value: number;
  minOrder: number;
  expires: string | null;
}

const CODES: Record<string, CodeDef> = {
  SAVE10: { type: 'pct', value: 10, minOrder: 50, expires: '2099-12-31T23:59:59Z' },
  FLAT5: { type: 'flat', value: 5, minOrder: 0, expires: null },
  HALF: { type: 'pct', value: 50, minOrder: 100, expires: null },
};

const round2 = (n: number): number => Math.round((n + Number.EPSILON) * 100) / 100;

export interface ApplyInput {
  subtotal: number;
  code: string;
}
export interface ApplyResult {
  finalTotal: number;
  discountApplied: number;
}

export function applyDiscount(input: ApplyInput, now: Date = new Date()): ApplyResult {
  const { subtotal, code } = input ?? ({} as ApplyInput);

  if (typeof subtotal !== 'number' || !Number.isFinite(subtotal) || subtotal <= 0) {
    throw new DiscountError('INVALID_INPUT', 'subtotal must be a positive, finite number');
  }
  if (typeof code !== 'string' || code.length === 0) {
    throw new DiscountError('INVALID_INPUT', 'code is required');
  }

  const def = CODES[code];
  if (!def) throw new DiscountError('UNKNOWN_CODE', `unknown code: ${code}`);
  if (def.expires && now.getTime() > new Date(def.expires).getTime()) {
    throw new DiscountError('EXPIRED', `code expired: ${code}`);
  }
  if (subtotal < def.minOrder) {
    throw new DiscountError('MIN_NOT_MET', `order below minimum of ${def.minOrder}`);
  }

  const raw = def.type === 'pct' ? (subtotal * def.value) / 100 : def.value;
  const discountApplied = round2(Math.min(raw, subtotal)); // never discount more than the order
  const finalTotal = round2(Math.max(0, subtotal - discountApplied)); // never negative
  return { finalTotal, discountApplied };
}

export function createServer(): http.Server {
  return http.createServer((req, res) => {
    const json = (status: number, payload: unknown) => {
      res.writeHead(status, { 'content-type': 'application/json' });
      res.end(JSON.stringify(payload));
    };

    if (req.method !== 'POST' || req.url !== '/apply') {
      return json(404, { error: 'NOT_FOUND' });
    }

    let body = '';
    req.on('data', (chunk) => (body += chunk));
    req.on('end', () => {
      try {
        const parsed = body ? JSON.parse(body) : {};
        json(200, applyDiscount(parsed));
      } catch (err) {
        const code = err instanceof DiscountError ? err.code : 'BAD_REQUEST';
        json(400, { error: code, message: (err as Error).message });
      }
    });
  });
}
