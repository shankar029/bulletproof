import { test } from 'node:test';
import assert from 'node:assert/strict';
import { applyDiscount } from './index.ts';

test('applies FLAT5', () => {
  assert.deepEqual(applyDiscount({ subtotal: 20, code: 'FLAT5' }), { finalTotal: 15, discountApplied: 5 });
});
