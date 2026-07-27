import { test, before, after } from 'node:test';
import assert from 'node:assert/strict';
import type { AddressInfo } from 'node:net';
import { applyDiscount, DiscountError, createServer } from './index.ts';

// --- unit: happy paths ---
test('FLAT5 subtracts a flat amount', () =>
  assert.deepEqual(applyDiscount({ subtotal: 20, code: 'FLAT5' }), { finalTotal: 15, discountApplied: 5 }));
test('SAVE10 subtracts a percentage', () =>
  assert.deepEqual(applyDiscount({ subtotal: 100, code: 'SAVE10' }), { finalTotal: 90, discountApplied: 10 }));
test('HALF subtracts 50 percent', () =>
  assert.deepEqual(applyDiscount({ subtotal: 100, code: 'HALF' }), { finalTotal: 50, discountApplied: 50 }));

// --- unit: edge cases ---
test('finalTotal floors at zero', () =>
  assert.deepEqual(applyDiscount({ subtotal: 3, code: 'FLAT5' }), { finalTotal: 0, discountApplied: 3 }));
test('money rounds to 2 decimals', () =>
  assert.deepEqual(applyDiscount({ subtotal: 99.99, code: 'SAVE10' }), { finalTotal: 89.99, discountApplied: 10 }));
test('min-order boundary is inclusive', () =>
  assert.deepEqual(applyDiscount({ subtotal: 50, code: 'SAVE10' }), { finalTotal: 45, discountApplied: 5 }));

// --- unit: validation & rules (typed errors) ---
for (const bad of [0, -1, Number.NaN, Infinity, '10' as any, null as any]) {
  test(`rejects invalid subtotal: ${String(bad)}`, () =>
    assert.throws(() => applyDiscount({ subtotal: bad, code: 'FLAT5' }), (e) => (e as DiscountError).code === 'INVALID_INPUT'));
}
test('rejects unknown code', () =>
  assert.throws(() => applyDiscount({ subtotal: 100, code: 'NOPE' }), (e) => (e as DiscountError).code === 'UNKNOWN_CODE'));
test('rejects empty code', () =>
  assert.throws(() => applyDiscount({ subtotal: 100, code: '' }), (e) => (e as DiscountError).code === 'INVALID_INPUT'));
test('rejects below-min order', () =>
  assert.throws(() => applyDiscount({ subtotal: 40, code: 'SAVE10' }), (e) => (e as DiscountError).code === 'MIN_NOT_MET'));
test('rejects expired code', () =>
  assert.throws(() => applyDiscount({ subtotal: 100, code: 'SAVE10' }, new Date('2100-01-01')), (e) => (e as DiscountError).code === 'EXPIRED'));
test('accepts code before expiry', () =>
  assert.deepEqual(applyDiscount({ subtotal: 100, code: 'SAVE10' }, new Date('2025-06-01')), { finalTotal: 90, discountApplied: 10 }));

// --- integration: real HTTP ---
let server: http.Server, base: string;
before(async () => {
  server = createServer();
  await new Promise<void>((r) => server.listen(0, () => r()));
  base = `http://127.0.0.1:${(server.address() as AddressInfo).port}`;
});
after(() => server.close());

test('POST /apply returns 200 with result', async () => {
  const res = await fetch(`${base}/apply`, { method: 'POST', body: JSON.stringify({ subtotal: 20, code: 'FLAT5' }) });
  assert.equal(res.status, 200);
  assert.deepEqual(await res.json(), { finalTotal: 15, discountApplied: 5 });
});
test('POST /apply returns 400 on rule failure', async () => {
  const res = await fetch(`${base}/apply`, { method: 'POST', body: JSON.stringify({ subtotal: 40, code: 'SAVE10' }) });
  assert.equal(res.status, 400);
  assert.equal((await res.json() as any).error, 'MIN_NOT_MET');
});
test('unknown route returns 404', async () => {
  const res = await fetch(`${base}/nope`);
  assert.equal(res.status, 404);
});
