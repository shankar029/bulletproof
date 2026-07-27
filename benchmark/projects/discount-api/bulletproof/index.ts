import http from 'node:http';
import { roundMoney } from '../shared/money.ts';
import { sendJson } from '../shared/http.ts';

/** Error carrying a stable machine-readable code for HTTP mapping. */
export class DiscountError extends Error {
  readonly code: string;
  constructor(code: string, message: string) {
    super(message);
    this.name = 'DiscountError';
    this.code = code;
  }
}

export interface CodeDef {
  type: 'pct' | 'flat';
  value: number;
  minOrder: number;
  expires: string | null;
}

// Codes live in a registry so new ones are added by data (open/closed) — not by editing the engine.
const CODES: Record<string, CodeDef> = {
  SAVE10: { type: 'pct', value: 10, minOrder: 50, expires: '2099-12-31T23:59:59Z' },
  FLAT5: { type: 'flat', value: 5, minOrder: 0, expires: null },
  HALF: { type: 'pct', value: 50, minOrder: 100, expires: null },
};

/** Register (or override) a discount code without changing applyDiscount. */
export function registerCode(name: string, def: CodeDef): void {
  CODES[name] = def;
}

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
  const discountApplied = roundMoney(Math.min(raw, subtotal)); // reuse shared money rounding
  const finalTotal = roundMoney(Math.max(0, subtotal - discountApplied));
  return { finalTotal, discountApplied };
}

export function createServer(): http.Server {
  return http.createServer((req, res) => {
    if (req.method !== 'POST' || req.url !== '/apply') {
      return sendJson(res, 404, { error: 'NOT_FOUND' }); // reuse shared HTTP helper
    }
    let body = '';
    req.on('data', (chunk) => (body += chunk));
    req.on('end', () => {
      try {
        const parsed = body ? JSON.parse(body) : {};
        sendJson(res, 200, applyDiscount(parsed));
      } catch (err) {
        const code = err instanceof DiscountError ? err.code : 'BAD_REQUEST';
        sendJson(res, 400, { error: code, message: (err as Error).message });
      }
    });
  });
}
