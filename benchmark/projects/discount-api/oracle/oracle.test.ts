import { test, before, after } from 'node:test';
import assert from 'node:assert/strict';
import { pathToFileURL } from 'node:url';
import type { AddressInfo } from 'node:net';

// Held-out acceptance suite. Runs against whichever arm ARM_PATH points to.
const armPath = process.env.ARM_PATH;
if (!armPath) throw new Error('ARM_PATH env var required');
const arm: any = await import(pathToFileURL(armPath).href);
const { applyDiscount, createServer } = arm;

// ---- function-level: correctness & edge cases ----
test('FLAT5 basic', () =>
  assert.deepEqual(applyDiscount({ subtotal: 20, code: 'FLAT5' }), { finalTotal: 15, discountApplied: 5 }));
test('FLAT5 floors finalTotal at zero', () =>
  assert.deepEqual(applyDiscount({ subtotal: 3, code: 'FLAT5' }), { finalTotal: 0, discountApplied: 3 }));
test('SAVE10 basic', () =>
  assert.deepEqual(applyDiscount({ subtotal: 100, code: 'SAVE10' }), { finalTotal: 90, discountApplied: 10 }));
test('SAVE10 min boundary (exactly 50) ok', () =>
  assert.deepEqual(applyDiscount({ subtotal: 50, code: 'SAVE10' }), { finalTotal: 45, discountApplied: 5 }));
test('SAVE10 below min throws', () =>
  assert.throws(() => applyDiscount({ subtotal: 40, code: 'SAVE10' })));
test('HALF basic', () =>
  assert.deepEqual(applyDiscount({ subtotal: 100, code: 'HALF' }), { finalTotal: 50, discountApplied: 50 }));
test('HALF below min throws', () =>
  assert.throws(() => applyDiscount({ subtotal: 99.99, code: 'HALF' })));
test('rounds money to 2 decimals', () =>
  assert.deepEqual(applyDiscount({ subtotal: 99.99, code: 'SAVE10' }), { finalTotal: 89.99, discountApplied: 10 }));
test('unknown code throws', () =>
  assert.throws(() => applyDiscount({ subtotal: 100, code: 'NOPE' })));
test('empty code throws', () =>
  assert.throws(() => applyDiscount({ subtotal: 100, code: '' })));
test('zero subtotal throws', () =>
  assert.throws(() => applyDiscount({ subtotal: 0, code: 'FLAT5' })));
test('negative subtotal throws', () =>
  assert.throws(() => applyDiscount({ subtotal: -5, code: 'FLAT5' })));
test('non-numeric subtotal throws', () =>
  assert.throws(() => applyDiscount({ subtotal: '50' as any, code: 'FLAT5' })));
test('expired code throws', () =>
  assert.throws(() => applyDiscount({ subtotal: 100, code: 'SAVE10' }, new Date('2100-01-01'))));
test('not-yet-expired code ok', () =>
  assert.deepEqual(applyDiscount({ subtotal: 100, code: 'SAVE10' }, new Date('2025-06-01')), { finalTotal: 90, discountApplied: 10 }));

// ---- HTTP E2E: real requests against a running server ----
let server: any, base: string;
before(async () => {
  server = createServer();
  await new Promise<void>((r) => server.listen(0, () => r()));
  base = `http://127.0.0.1:${(server.address() as AddressInfo).port}`;
});
after(() => server?.close());

const post = (body: unknown) =>
  fetch(`${base}/apply`, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(body) });

test('POST /apply happy path', async () => {
  const res = await post({ subtotal: 20, code: 'FLAT5' });
  assert.equal(res.status, 200);
  assert.deepEqual(await res.json(), { finalTotal: 15, discountApplied: 5 });
});
test('POST /apply floors at zero', async () => {
  const res = await post({ subtotal: 3, code: 'FLAT5' });
  assert.equal(res.status, 200);
  assert.deepEqual(await res.json(), { finalTotal: 0, discountApplied: 3 });
});
test('POST /apply rounds money', async () => {
  const res = await post({ subtotal: 99.99, code: 'SAVE10' });
  assert.equal(res.status, 200);
  assert.deepEqual(await res.json(), { finalTotal: 89.99, discountApplied: 10 });
});
test('POST /apply below min -> 400', async () => {
  const res = await post({ subtotal: 40, code: 'SAVE10' });
  assert.equal(res.status, 400);
});
test('POST /apply invalid input -> 400', async () => {
  const res = await post({ subtotal: 0, code: 'FLAT5' });
  assert.equal(res.status, 400);
});
