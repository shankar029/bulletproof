import http from 'node:http';

// Baseline: quick single-pass implementation. Handles the main path.
const CODES: any = {
  SAVE10: { pct: 10, min: 50 },
  FLAT5: { flat: 5 },
  HALF: { pct: 50, min: 100 },
};

export function applyDiscount(input: any) {
  const { subtotal, code } = input;
  const c = CODES[code];
  if (!c) throw new Error('invalid code');
  if (c.min && subtotal < c.min) throw new Error('min not met');
  const discount = c.pct ? (subtotal * c.pct) / 100 : c.flat;
  return { finalTotal: subtotal - discount, discountApplied: discount };
}

export function createServer() {
  return http.createServer((req, res) => {
    let body = '';
    req.on('data', (c) => (body += c));
    req.on('end', () => {
      try {
        const result = applyDiscount(JSON.parse(body || '{}'));
        res.writeHead(200, { 'content-type': 'application/json' });
        res.end(JSON.stringify(result));
      } catch (e) {
        res.writeHead(400, { 'content-type': 'application/json' });
        res.end(JSON.stringify({ error: (e as Error).message }));
      }
    });
  });
}
